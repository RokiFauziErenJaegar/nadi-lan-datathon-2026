"""Uji penghalang kebocoran data pribadi.

Berkas ini adalah bukti yang dapat dijalankan atas janji privasi pada proposal
NADI. Seluruh nomor di bawah adalah rekaan dan tidak merujuk orang mana pun.
"""

from __future__ import annotations

import pytest

from nadi.security import pii

# --- Nilai rekaan untuk pengujian -----------------------------------------
NIK_RAPAT = "1810012509900001"
NIK_BERTITIK = "1810.0125.0990.0001"
NIK_BERSTRIP = "1810-0125-0990-0001"
BPJS_REKAAN = "0001234567890"
PONSEL_REKAAN = "081234567890"
PONSEL_KODE_NEGARA = "+6281234567890"


class TestDeteksiPola:
    """Pola pengenal pribadi harus tertangkap dalam berbagai bentuk penulisan."""

    @pytest.mark.parametrize(
        "teks",
        [
            NIK_RAPAT,
            NIK_BERTITIK,
            NIK_BERSTRIP,
            f"Keluarga dengan NIK {NIK_RAPAT} perlu diverifikasi.",
            f"no.{NIK_RAPAT}",
        ],
    )
    def test_nik_terdeteksi(self, teks: str) -> None:
        hasil = pii.pindai(teks)
        assert not hasil.bersih
        assert any(t.kind is pii.PIIKind.NIK_ATAU_KK for t in hasil.temuan)

    def test_bpjs_terdeteksi(self) -> None:
        assert not pii.pindai(f"Nomor kepesertaan {BPJS_REKAAN}").bersih

    @pytest.mark.parametrize("nomor", [PONSEL_REKAAN, PONSEL_KODE_NEGARA])
    def test_nomor_ponsel_terdeteksi(self, nomor: str) -> None:
        hasil = pii.pindai(f"Hubungi {nomor} untuk konfirmasi.")
        assert any(t.kind is pii.PIIKind.NOMOR_TELEPON for t in hasil.temuan)

    def test_surel_terdeteksi(self) -> None:
        hasil = pii.pindai("Kirim ke petugas.rekaan@contoh.go.id")
        assert any(t.kind is pii.PIIKind.SUREL for t in hasil.temuan)

    def test_alamat_rt_rw_terdeteksi(self) -> None:
        hasil = pii.pindai("Beralamat di RT 003 RW 005 Pekon Podomoro")
        assert any(t.kind is pii.PIIKind.RT_RW for t in hasil.temuan)

    def test_koordinat_presisi_tinggi_terdeteksi(self) -> None:
        """Koordinat berpresisi meteran dapat menunjuk satu rumah."""
        hasil = pii.pindai("-5.3581234, 104.9751234")
        assert any(t.kind is pii.PIIKind.KOORDINAT_PRESISI for t in hasil.temuan)


class TestBukanPositifPalsu:
    """Data agregat yang sah tidak boleh ikut terblokir."""

    @pytest.mark.parametrize(
        "teks",
        [
            "Deret tahun 2020 2021 2022 2023 menunjukkan penurunan.",
            "Jumlah penduduk miskin 31,66 ribu jiwa atau 7,60 persen.",
            "Garis kemiskinan Rp 512.345 per kapita per bulan.",
            "Koordinat pusat kecamatan -5.358, 104.975",
            "Skor kerentanan 0.7391234567890123 pada gelombang ketiga.",
            "Kode wilayah 18.10.05.2001 untuk Pekon Podomoro.",
        ],
    )
    def test_teks_agregat_lolos(self, teks: str) -> None:
        hasil = pii.pindai(teks)
        assert hasil.bersih, f"Positif palsu pada teks agregat: {hasil.ringkas()}"

    def test_bilangan_pecahan_panjang_lolos(self) -> None:
        """Hasil perhitungan numerik sering membawa banyak angka desimal."""
        muatan = {"skor": 0.1234567890123456, "kontribusi": [0.9876543210987654]}
        assert pii.pindai(muatan).bersih


class TestKunciTerlarang:
    """Nama kunci yang mengandung identitas ditolak apa pun isinya."""

    @pytest.mark.parametrize(
        "muatan",
        [
            {"nama": "Budi"},
            {"nik": "kosong"},
            {"keluarga": {"nama_kepala_keluarga": "-"}},
            {"lokasi": {"latitude": 0, "longitude": 0}},
            {"daftar": [{"alamat": "Jalan Mawar"}]},
        ],
    )
    def test_kunci_identitas_ditolak(self, muatan: dict) -> None:
        hasil = pii.pindai(muatan)
        assert not hasil.bersih
        assert any("kunci terlarang" in t.contoh_tersamar for t in hasil.temuan)

    def test_muatan_analitik_yang_benar_lolos(self) -> None:
        """Bentuk muatan yang memang dirancang untuk dikirim ke layanan AI."""
        muatan = {
            "kode_keluarga": "KLG-7F3A-2B9K",
            "kecamatan": "Pagelaran",
            "skor_kerentanan": 78,
            "faktor_risiko": [
                {"nama_faktor": "rasio_tanggungan_tinggi", "kontribusi": 12.4},
                {"nama_faktor": "sanitasi_tidak_layak", "kontribusi": 9.1},
            ],
            "program_diterima": ["PKH", "Program Sembako"],
        }
        hasil = pii.pindai(muatan)
        assert hasil.bersih, hasil.ringkas()


class TestPenegakan:
    """``pastikan_bersih`` harus membatalkan permintaan, bukan menyamarkannya."""

    def test_muatan_kotor_mengangkat_galat(self) -> None:
        with pytest.raises(pii.PIILeakError) as info:
            pii.pastikan_bersih({"catatan": f"NIK {NIK_RAPAT}"})
        assert "DIBATALKAN" in str(info.value)

    def test_nilai_asli_tidak_bocor_ke_pesan_galat(self) -> None:
        """Pesan galat dan log tidak boleh memuat nilai aslinya."""
        with pytest.raises(pii.PIILeakError) as info:
            pii.pastikan_bersih({"catatan": f"NIK {NIK_RAPAT}"})
        assert NIK_RAPAT not in str(info.value)

    def test_muatan_bersih_lolos_tanpa_galat(self) -> None:
        pii.pastikan_bersih({"kecamatan": "Sukoharjo", "jumlah_kasus": 42})

    def test_pemindaian_menelusuri_struktur_bersarang(self) -> None:
        muatan = {"tingkat1": {"tingkat2": [{"tingkat3": f"KK {NIK_RAPAT}"}]}}
        hasil = pii.pindai(muatan)
        assert not hasil.bersih
        assert hasil.temuan[0].lokasi == "$.tingkat1.tingkat2[0].tingkat3"

    def test_angka_yang_tersimpan_sebagai_bilangan_ikut_terpindai(self) -> None:
        """NIK yang tersimpan sebagai integer, bukan untai, tetap tertangkap."""
        assert not pii.pindai({"pengenal": int(NIK_RAPAT)}).bersih


class TestRedaksi:
    """Masukan bebas dari pengguna diredaksi, bukan ditolak."""

    def test_redaksi_mengganti_nilai(self) -> None:
        hasil = pii.redaksi_teks(f"Cek keluarga NIK {NIK_RAPAT} di Pagelaran")
        assert NIK_RAPAT not in hasil
        assert "[DIREDAKSI]" in hasil
        assert "Pagelaran" in hasil

    def test_teks_hasil_redaksi_lolos_pemindaian(self) -> None:
        kotor = f"NIK {NIK_RAPAT}, HP {PONSEL_REKAAN}, surel a@b.go.id"
        assert pii.pindai(pii.redaksi_teks(kotor)).bersih

    def test_penyamaran_menyisakan_ujung_saja(self) -> None:
        assert pii.samarkan_nilai("1810012509900001") == "18************01"
        assert pii.samarkan_nilai("abc") == "***"
