"""Transparansi model - metrik, keadilan, dan batas kemampuan.

Titik akhir pada modul ini membuka isi model kepada penggunanya. Ini bukan
kelengkapan teknis melainkan pemenuhan janji: sistem yang memengaruhi siapa
didahulukan menerima kunjungan petugas harus sanggup memperlihatkan seberapa
sering ia keliru, dan pada kelompok mana kekeliruannya menumpuk.

Bagian yang paling penting justru bukan angka keberhasilannya, melainkan
:func:`batas` - daftar hal yang tidak dapat dilakukan model ini. Sistem yang
hanya menampilkan kelebihannya menuntut kepercayaan; sistem yang menyebutkan
batasnya justru layak dipercaya.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from nadi.api.deps import SesiDB, wajib
from nadi.ml.fitur import (
    DAFTAR_FITUR,
    NAMA_FITUR_DTSEN,
    NAMA_FITUR_LENGKAP,
    NAMA_FITUR_MELINGKAR,
    NAMA_FITUR_OPERASIONAL,
    fitur_per_dimensi,
)
from nadi.security.rbac import Kewenangan, ringkasan_matriks

logger = logging.getLogger("nadi.api.model")
router = APIRouter(prefix="/model", tags=["model"])


@router.get("/aktif", summary="Model yang sedang dipakai",
            dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def aktif(sesi: SesiDB) -> dict:
    """Metrik model yang sedang melayani permintaan."""
    b = sesi.execute(
        text(
            """
            SELECT nama, versi, jenis, algoritma, dilatih_pada, gelombang_latih,
                   gelombang_uji, jumlah_baris_latih, jumlah_fitur, metrik,
                   metrik_keadilan, kepentingan_fitur, sidik_jari_dataset, catatan
            FROM versi_model WHERE aktif = 1 LIMIT 1
            """
        )
    ).one_or_none()
    if b is None:
        raise HTTPException(404, "Belum ada model aktif. Jalankan backend/scripts/latih_model.py.")

    def _json(nilai):
        return json.loads(nilai) if isinstance(nilai, str) else (nilai or {})

    metrik = _json(b.metrik)
    kepentingan = _json(b.kepentingan_fitur)
    teratas = sorted(kepentingan.items(), key=lambda x: -x[1])[:15]

    from nadi.ml.fitur import PETA_FITUR

    return {
        "nama": b.nama,
        "versi": b.versi,
        "jenis": b.jenis,
        "algoritma": b.algoritma,
        "dilatih_pada": str(b.dilatih_pada),
        "gelombang_latih": _json(b.gelombang_latih),
        "gelombang_uji": _json(b.gelombang_uji),
        "jumlah_baris_latih": b.jumlah_baris_latih,
        "jumlah_fitur": b.jumlah_fitur,
        "sidik_jari_dataset": b.sidik_jari_dataset,
        "metrik": metrik,
        "keadilan": _json(b.metrik_keadilan),
        "fitur_paling_berpengaruh": [
            {
                "nama": n,
                "label": PETA_FITUR[n].label if n in PETA_FITUR else n,
                "kepentingan_persen": v,
                "dimensi": PETA_FITUR[n].dimensi.value if n in PETA_FITUR else None,
                "sumber_data": PETA_FITUR[n].sumber if n in PETA_FITUR else None,
            }
            for n, v in teratas
        ],
        "catatan": b.catatan,
    }


@router.get("/fitur", summary="Daftar fitur beserta asal datanya",
            dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def fitur() -> dict:
    """Seluruh fitur, dikelompokkan menurut dimensi dan asal datanya.

    Pembedaan asal data pada tanggapan ini menjawab pertanyaan kebijakan yang
    nyata: seberapa jauh kemampuan menargetkan dapat ditingkatkan dengan
    memadukan data antar-dinas, dan seberapa jauh lagi bila pencacahan
    pengeluaran ikut dipadankan.
    """
    from nadi.ml.fitur import PETA_FITUR

    per_dimensi = fitur_per_dimensi()
    return {
        "lapis": {
            "dtsen_saja": {
                "jumlah": len(NAMA_FITUR_DTSEN),
                "keterangan": "Tersedia langsung pada Data Tunggal Sosial dan Ekonomi Nasional.",
            },
            "operasional": {
                "jumlah": len(NAMA_FITUR_OPERASIONAL),
                "keterangan": (
                    "DTSEN ditambah sinyal lintas dinas - catatan kematian, pemutusan "
                    "hubungan kerja, gagal panen, bencana. Inilah himpunan yang dipakai "
                    "model yang dijalankan."
                ),
            },
            "dengan_survei_konsumsi": {
                "jumlah": len(NAMA_FITUR_LENGKAP),
                "keterangan": (
                    "Ditambah pengeluaran terukur gaya Susenas. HANYA dipakai sebagai "
                    "pembanding batas atas, tidak pernah untuk model yang dijalankan, "
                    "sebab angka itu tidak akan tersedia saat sistem benar-benar dipakai."
                ),
            },
        },
        "dikecualikan": {
            "jumlah": len(NAMA_FITUR_MELINGKAR),
            "fitur": [
                {"nama": n, "label": PETA_FITUR[n].label} for n in NAMA_FITUR_MELINGKAR
            ],
            "alasan": (
                "Fitur kepesertaan program mencerminkan KEPUTUSAN penargetan pemerintah, "
                "bukan KEADAAN keluarga. Model yang memakainya akan menempatkan keluarga "
                "yang belum tersentuh bantuan lebih rendah pada antrean - padahal "
                "merekalah yang paling perlu ditemukan. Pengujian menunjukkan biaya "
                "mengeluarkannya hampir nol: AUC turun dari 0,859 menjadi 0,858."
            ),
        },
        "per_dimensi": [
            {
                "dimensi": d.value,
                "label": d.label,
                "ikon": d.ikon,
                "jumlah": len(daftar),
                "fitur": [
                    {
                        "nama": f.nama,
                        "label": f.label,
                        "keterangan": f.keterangan,
                        "kode_risiko": f.kode_risiko,
                        "sumber": f.sumber,
                        "dipakai_model": f.nama in NAMA_FITUR_OPERASIONAL,
                    }
                    for f in daftar
                ],
            }
            for d, daftar in per_dimensi.items()
        ],
        "total": len(DAFTAR_FITUR),
    }


@router.get("/batas", summary="Batas kemampuan dan tata kelola model")
def batas() -> dict:
    """Nyatakan terus terang apa yang tidak dapat dilakukan sistem ini.

    Dibuka tanpa autentikasi. Batas sebuah sistem yang memengaruhi penyaluran
    bantuan bukanlah keterangan internal - ia keterangan publik.
    """
    return {
        "yang_dilakukan": [
            "Memperkirakan peluang sebuah keluarga berada di bawah garis kemiskinan "
            "pada pemutakhiran data berikutnya.",
            "Menjelaskan faktor apa yang mendorong perkiraan itu, per keluarga.",
            "Menandai ketidaksesuaian sasaran untuk diperiksa petugas.",
            "Mencocokkan faktor risiko dengan program dan dinas pelaksananya.",
            "Menghitung aritmetika cakupan, biaya, dan kapasitas verifikasi.",
        ],
        "yang_tidak_dilakukan": [
            "Menetapkan siapa yang berhak menerima bantuan.",
            "Menghentikan, mengurangi, atau menunda bantuan siapa pun.",
            "Mendeteksi kecurangan atau penyalahgunaan bantuan.",
            "Memperkirakan dampak sebuah kebijakan terhadap angka kemiskinan.",
            "Menyimpan nama, nomor induk kependudukan, atau alamat.",
        ],
        "batas_teknis": [
            {
                "batas": "Ketepatan model terbatas pada sifat data yang tersedia",
                "keterangan": (
                    "Penduga tak langsung seperti proxy means test hanya menjelaskan "
                    "sekitar separuh keragaman kesejahteraan antar-keluarga. Kajian "
                    "lintas negara menempatkan batas atas yang wajar pada AUC sekitar "
                    "0,85. Angka di atas 0,90 pada persoalan ini lebih sering "
                    "menandakan kebocoran data daripada model yang baik."
                ),
            },
            {
                "batas": "Penjelasan bukan sebab-akibat",
                "keterangan": (
                    "Nilai kontribusi fitur menerangkan apa yang dibaca model, bukan apa "
                    "yang menyebabkan kemiskinan. Memperbaiki satu penanda tidak dengan "
                    "sendirinya memperbaiki keadaan keluarga."
                ),
            },
            {
                "batas": "Data sintetis",
                "keterangan": (
                    "Seluruh data pada sistem ini dibangkitkan menyerupai bentuk "
                    "statistik penduduk Kabupaten Pringsewu. Tidak ada keluarga nyata "
                    "di dalamnya. Angka kinerja model berlaku pada data ini, dan wajib "
                    "diukur ulang pada data sesungguhnya."
                ),
            },
            {
                "batas": "Guncangan menuntut pemaduan data antar-dinas",
                "keterangan": (
                    "Sinyal guncangan - kematian pencari nafkah, pemutusan hubungan "
                    "kerja, gagal panen, bencana - tidak ada pada DTSEN. Keunggulan "
                    "sistem ini pada deteksi dini bergantung pada kesediaan dinas "
                    "berbagi data, yang merupakan pekerjaan koordinasi, bukan teknis."
                ),
            },
        ],
        "tata_kelola": {
            "keputusan_otomatis": (
                "Tidak ada. Seluruh keluaran sistem berupa antrean prioritas "
                "pemeriksaan. Penetapan penerima melalui musyawarah pekon dan keputusan "
                "pejabat berwenang."
            ),
            "hak_membantah": (
                "Setiap penandaan menyertakan alasan yang dapat diperiksa, sehingga "
                "petugas maupun warga dapat menyanggahnya. Ini pemenuhan hak atas "
                "penjelasan sebagaimana diatur Undang-Undang Nomor 27 Tahun 2022 "
                "tentang Pelindungan Data Pribadi."
            ),
            "jejak_audit": "Setiap pembukaan data keluarga tercatat beserta pelakunya.",
            "minimalisasi_data": (
                "Nama, nomor induk kependudukan, dan alamat tidak tersimpan. Koordinat "
                "digeser acak dalam radius 250 meter."
            ),
            "pelajaran_sistem_lain": (
                "Rancangan ini menempatkan tiga alasan pelarangan sistem SyRI di Belanda "
                "sebagai daftar periksa terbalik: tidak buram, data diminimalkan, dan "
                "tujuannya khusus - hanya untuk memperluas jangkauan layanan, tidak "
                "pernah untuk memutus bantuan maupun mendeteksi kecurangan."
            ),
        },
        "peran_dan_akses": ringkasan_matriks(),
    }


@router.get("/versi", summary="Riwayat versi model",
            dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def versi(sesi: SesiDB) -> dict:
    """Seluruh versi model yang pernah dilatih beserta metriknya."""
    baris = sesi.execute(
        text(
            """
            SELECT nama, versi, jenis, dilatih_pada, jumlah_fitur,
                   jumlah_baris_latih, metrik, aktif, catatan
            FROM versi_model ORDER BY dilatih_pada DESC
            """
        )
    ).all()
    return {
        "jumlah": len(baris),
        "versi": [
            {
                "nama": b.nama,
                "versi": b.versi,
                "jenis": b.jenis,
                "dilatih_pada": str(b.dilatih_pada),
                "jumlah_fitur": b.jumlah_fitur,
                "jumlah_baris_latih": b.jumlah_baris_latih,
                "auc": (json.loads(b.metrik) if isinstance(b.metrik, str) else (b.metrik or {})).get("auc"),
                "aktif": bool(b.aktif),
                "catatan": b.catatan,
            }
            for b in baris
        ],
    }


__all__ = ["router"]
