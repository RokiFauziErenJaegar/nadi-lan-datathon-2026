"""Sketsa rancangan awal - wireframe seolah-olah digambar sebelum aplikasi ada.

Berbeda dari mockup berketelitian tinggi, sketsa ini sengaja kasar: kotak
bergaris tangan, huruf seperti tulisan pena, hitam-putih dengan coretan biru
untuk catatan. Isinya diambil dari **deskripsi delapan modul pada proposal**,
bukan dari aplikasi yang sudah jadi - inilah "imajinasi awal" yang kemudian
menjadi kenyataan pada halaman mockup.

Nilainya bagi dewan juri: menyandingkan gambaran awal dengan hasil akhir
memperlihatkan bahwa yang dibangun memang yang dijanjikan.
"""

from __future__ import annotations

W, H = 1440, 900
KERTAS = "#fdfdfb"
TINTA = "#2b2b2b"
ISI = "#ececec"
PENA = "#1d4ed8"
PENA_MUDA = "#93c5fd"

# Sudut tidak rata - trik CSS klasik untuk kesan garis tangan.
GORES = "border-radius:255px 15px 225px 15px / 15px 225px 15px 255px;"
GORES_KECIL = "border-radius:12px 4px 10px 4px / 4px 10px 4px 12px;"


def kepala(judul: str) -> str:
    return f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <title>{judul}</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Patrick+Hand&amp;family=Caveat:wght@500;700&amp;display=swap">
  <style>
    body {{ margin: 0; font-family: "Patrick Hand", "Segoe Print", "Comic Sans MS", cursive; color: {TINTA}; }}
    a {{ color: {PENA}; }} a:hover {{ color: #1e40af; }}
  </style>
</helmet>'''


KAKI = "</x-dc>\n</body>\n</html>\n"


def kotak(isi: str, *, w: str = "auto", h: str = "auto", isi_bg: str = "#fff", style: str = "",
          garis: str = "solid") -> str:
    return (f'<div style="box-sizing:border-box;width:{w};height:{h};border:2px {garis} {TINTA};{GORES_KECIL}'
            f'background:{isi_bg};padding:10px 12px;{style}">{isi}</div>')


def silang(label: str, *, w: str = "100%", h: str = "160px") -> str:
    """Kotak penampung gambar/grafik: bersilang diagonal, seperti pada wireframe."""
    return (f'<div style="position:relative;box-sizing:border-box;width:{w};height:{h};border:2px solid {TINTA};{GORES_KECIL}'
            f'background:{ISI};overflow:hidden">'
            f'<svg width="100%" height="100%" style="position:absolute;inset:0" preserveAspectRatio="none" viewBox="0 0 100 100">'
            f'<line x1="0" y1="0" x2="100" y2="100" stroke="{TINTA}" stroke-width="0.6" vector-effect="non-scaling-stroke"/>'
            f'<line x1="100" y1="0" x2="0" y2="100" stroke="{TINTA}" stroke-width="0.6" vector-effect="non-scaling-stroke"/></svg>'
            f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">'
            f'<span style="background:{KERTAS};padding:4px 12px;border:1.5px solid {TINTA};{GORES_KECIL}font-size:16px">{label}</span></div></div>')


def teks(t: str, *, ukuran: int = 16, tebal: bool = False, warna: str = TINTA, style: str = "") -> str:
    return f'<div style="font-size:{ukuran}px;line-height:1.3;{"font-weight:700;" if tebal else ""}color:{warna};{style}">{t}</div>'


def garis_teks(n: int, lebar: str = "100%") -> str:
    """Baris-baris abu sebagai penampung teks."""
    return "".join(
        f'<div style="height:9px;width:{(100 - (i * 17) % 40) if i else 92}%;max-width:{lebar};background:#d4d4d4;'
        f'border-radius:4px;margin:7px 0"></div>' for i in range(n))


def catatan(t: str, *, x: int, y: int, w: int = 220, panah: str = "") -> str:
    """Coretan pena biru dengan panah sederhana."""
    p = ""
    if panah:
        dx, dy = {"kiri": (-1, 0), "kanan": (1, 0), "bawah": (0, 1), "atas": (0, -1)}[panah]
        x1, y1 = (0 if dx < 0 else (w if dx > 0 else w // 2)), (0 if dy < 0 else (44 if dy > 0 else 22))
        x2, y2 = x1 + dx * 42, y1 + dy * 34
        p = (f'<svg style="position:absolute;left:{min(x1,x2)-6}px;top:{min(y1,y2)-6}px;overflow:visible" width="60" height="60">'
             f'<path d="M{x1-min(x1,x2)+6},{y1-min(y1,y2)+6} Q{(x1+x2)/2-min(x1,x2)+6+8},{(y1+y2)/2-min(y1,y2)+6-8} {x2-min(x1,x2)+6},{y2-min(y1,y2)+6}" '
             f'fill="none" stroke="{PENA}" stroke-width="2" stroke-linecap="round"/>'
             f'<circle cx="{x2-min(x1,x2)+6}" cy="{y2-min(y1,y2)+6}" r="3" fill="{PENA}"/></svg>')
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font-family:Caveat,\'Segoe Print\',cursive;'
            f'font-size:19px;line-height:1.15;font-weight:600;color:{PENA};transform:rotate(-1.5deg);pointer-events:none">{t}{p}</div>')


def stempel(t: str) -> str:
    return (f'<div style="position:absolute;right:28px;top:22px;transform:rotate(6deg);border:3px solid {PENA};{GORES_KECIL}'
            f'padding:4px 14px;font-family:Caveat,cursive;font-size:22px;font-weight:700;color:{PENA};opacity:0.85;letter-spacing:0.04em">{t}</div>')


def bilah_samping(aktif: int) -> str:
    modul = ["Command Center", "Digital Twin", "Peta Risiko (GeoAI)", "Antrean Mismatch",
             "Rekomendasi", "Simulator What-if", "Policy Copilot", "Monitoring Outcome"]
    butir = "".join(
        f'<div style="display:flex;align-items:center;gap:10px;padding:7px 10px;{"border:2px solid "+TINTA+";"+GORES_KECIL+"background:"+ISI if i==aktif else ""}">'
        f'<span style="width:16px;height:16px;border:2px solid {TINTA};border-radius:4px;flex-shrink:0"></span>'
        f'<span style="font-size:17px">{i+1:02d} {m}</span></div>' for i, m in enumerate(modul))
    return (f'<div style="width:250px;flex-shrink:0;box-sizing:border-box;border-right:2px solid {TINTA};padding:14px 12px;display:flex;flex-direction:column">'
            f'<div style="border-bottom:2px solid {TINTA};padding-bottom:10px;margin-bottom:12px"><div style="font-size:30px;font-weight:700;font-family:Caveat,cursive">NADI</div>'
            f'<div style="font-size:14px;color:#666">Navigasi AI Data Intervensi</div></div>'
            f'<div style="display:flex;flex-direction:column;gap:4px">{butir}</div>'
            f'<div style="margin-top:auto;border:2px dashed {TINTA};{GORES_KECIL}padding:8px;font-size:14px;color:#555">[ peran pengguna ]<br>[ tombol keluar ]</div></div>')


def kerangka(judul: str, aktif: int, isi: str, coretan: str = "", stempel_teks: str = "SKETSA AWAL") -> str:
    return (kepala(judul) + f'''
<div style="position:relative;display:flex;width:{W}px;height:{H}px;background:{KERTAS};overflow:hidden;
  background-image:linear-gradient(#e8e8e8 1px, transparent 1px),linear-gradient(90deg,#e8e8e8 1px, transparent 1px);background-size:24px 24px">
  {bilah_samping(aktif)}
  <div style="display:flex;flex:1;min-width:0;flex-direction:column">
    <div style="display:flex;align-items:center;justify-content:space-between;height:62px;border-bottom:2px solid {TINTA};padding:0 22px">
      <div><div style="font-size:24px;font-weight:700">{judul}</div><div style="font-size:14px;color:#666">Kabupaten Pringsewu</div></div>
      <div style="border:2px solid {TINTA};{GORES_KECIL}padding:4px 12px;font-size:14px">[ pencarian ]</div>
    </div>
    <div style="position:relative;flex:1;padding:20px 22px;overflow:hidden">{isi}</div>
  </div>
  {coretan}{stempel(stempel_teks)}
</div>
''' + KAKI)


# ===========================================================================
def sketsa_masuk() -> str:
    return kepala("Sketsa: Masuk") + f'''
<div style="position:relative;display:flex;width:{W}px;height:{H}px;align-items:center;justify-content:center;background:{KERTAS};
  background-image:linear-gradient(#e8e8e8 1px, transparent 1px),linear-gradient(90deg,#e8e8e8 1px, transparent 1px);background-size:24px 24px">
  <div style="display:flex;gap:40px;align-items:stretch">
    {kotak(f'<div style="font-size:34px;font-weight:700;font-family:Caveat,cursive">NADI</div><div style="font-size:15px;color:#666;margin-bottom:22px">Navigasi AI Data Intervensi</div>'
           f'{teks("nama pengguna", ukuran=14)}{kotak("", h="40px", style="margin:4px 0 14px")}{teks("kata sandi", ukuran=14)}{kotak("", h="40px", style="margin:4px 0 22px")}'
           f'{kotak("MASUK", h="44px", isi_bg=ISI, style="text-align:center;font-weight:700;font-size:18px")}', w="360px", style="padding:24px")}
    {kotak(f'{teks("Akun uji per peran", ukuran=18, tebal=True)}<div style="margin-top:12px;display:flex;flex-direction:column;gap:8px">'
           + "".join(kotak(f"{p}", h="36px", garis="dashed", style="font-size:15px") for p in ("Bupati / Sekda", "Bappeda", "Dinas Sosial", "OPD pelaksana", "Verifikator lapangan"))
           + "</div>", w="340px", style="padding:24px")}
  </div>
  {catatan("akses berbasis peran (RBAC)<br>— pimpinan hanya agregat!", x=1040, y=280, w=240, panah="kiri")}
  {catatan("pseudonimisasi: tidak ada NIK<br>di mana pun pada aplikasi", x=1040, y=470, w=260)}
  {stempel("SKETSA AWAL")}
</div>
''' + KAKI


def sketsa_command_center() -> str:
    tiles = "".join(kotak(f'{teks(l, ukuran=13, warna="#666")}<div style="font-size:30px;font-weight:700;margin-top:2px">####</div>', h="88px")
                    for l in ("keluarga rentan", "risiko tinggi", "alert baru", "intervensi berjalan"))
    isi = f'''
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px">{tiles}</div>
<div style="display:grid;grid-template-columns:1.5fr 1fr;gap:16px;margin-bottom:16px">
  {kotak(teks("Tren kerentanan antar-waktu", ukuran=17, tebal=True) + silang("grafik garis, 6 gelombang", h="200px"), h="260px")}
  {kotak(teks("Prioritas wilayah", ukuran=17, tebal=True) + garis_teks(7), h="260px")}
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  {kotak(teks("Status intervensi", ukuran=17, tebal=True) + silang("batang per OPD", h="150px"), h="210px")}
  {kotak(teks("Alert baru", ukuran=17, tebal=True) + garis_teks(5), h="210px")}
</div>'''
    cor = (catatan("indikator risiko →<br>dari NADI Vulnerability Score", x=1180, y=110, w=230, panah="kiri")
           + catatan("satu layar untuk Bupati:<br>tren, wilayah, alert", x=290, y=370, w=230))
    return kerangka("01  Executive Command Center", 0, isi, cor)


def sketsa_digital_twin() -> str:
    isi = f'''
<div style="display:flex;gap:16px;margin-bottom:16px;align-items:stretch">
  {kotak(teks("KELUARGA #kode-semu", ukuran=20, tebal=True) + teks("pekon · kecamatan · desil · anggota", ukuran=14, warna="#666") + garis_teks(2), style="flex:1")}
  {kotak(teks("NADI Score", ukuran=14, warna="#666") + '<div style="font-size:44px;font-weight:700;line-height:1">0–100</div>' + teks("+ kategori risiko", ukuran=13), w="200px", isi_bg=ISI)}
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
  {kotak(teks("Riwayat perubahan (state dinamis)", ukuran=17, tebal=True) + silang("lintasan kondisi vs garis kemiskinan", h="180px"), h="240px")}
  {kotak(teks("Top risk drivers (explainable AI)", ukuran=17, tebal=True) + "".join(f'<div style="display:flex;align-items:center;gap:8px;margin:8px 0"><div style="height:14px;width:{w}%;background:#bbb;{GORES_KECIL}"></div><span style="font-size:13px">{t}</span></div>' for w, t in ((70,"pendapatan tidak stabil"),(52,"rasio tanggungan tinggi"),(38,"akses sanitasi rendah"),(22,"riwayat intervensi belum sesuai"))), h="240px")}
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
  {kotak(teks("Program diterima", ukuran=16, tebal=True) + garis_teks(4), h="150px")}
  {kotak(teks("Guncangan tercatat", ukuran=16, tebal=True) + garis_teks(4), h="150px")}
  {kotak(teks("Rekomendasi intervensi", ukuran=16, tebal=True) + garis_teks(4), h="150px", garis="dashed")}
</div>'''
    cor = (catatan("skor tidak boleh jadi<br>'kotak hitam' — selalu<br>ada alasan (SHAP)", x=1150, y=330, w=230, panah="kiri")
           + catatan("state diperbarui tiap<br>pemutakhiran data", x=300, y=560, w=210, panah="atas"))
    return kerangka("02  Household Digital Twin", 1, isi, cor)


def sketsa_geoai() -> str:
    isi = f'''
<div style="display:grid;grid-template-columns:1fr 300px;gap:16px;height:100%">
  <div style="display:flex;flex-direction:column;gap:12px">
    <div style="display:flex;gap:8px">{"".join(kotak(t, h="36px", isi_bg=(ISI if i==0 else "#fff"), style="font-size:14px") for i,t in enumerate(("tingkat kemiskinan","skor kerentanan","cakupan bantuan","hunian layak")))}</div>
    <div style="position:relative;flex:1">{silang("PETA CLUSTER RISIKO — sampai tingkat pekon", h="560px")}
      <div style="position:absolute;left:14px;bottom:14px;border:2px solid {TINTA};{GORES_KECIL}background:{KERTAS};padding:8px 12px;font-size:14px">legenda: rendah → tinggi<br><span style="display:inline-block;width:120px;height:12px;background:linear-gradient(90deg,#eee,#555);border:1px solid {TINTA}"></span></div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:12px">
    {kotak(teks("Peringkat kecamatan", ukuran=16, tebal=True) + garis_teks(9), h="300px")}
    {kotak(teks("Drill-down sesuai hak akses", ukuran=15, tebal=True) + teks("kabupaten → kecamatan → pekon; titik keluarga hanya untuk yang berwenang", ukuran=13, warna="#666"), garis="dashed")}
    {kotak(teks("Privasi", ukuran=15, tebal=True) + teks("agregasi wilayah kecil disembunyikan; koordinat digeser", ukuran=13, warna="#666"), garis="dashed")}
  </div>
</div>'''
    cor = catatan("batas wilayah resmi —<br>bukan bentuk perkiraan", x=520, y=140, w=220, panah="bawah")
    return kerangka("03  GeoAI Poverty Radar", 2, isi, cor)


def sketsa_mismatch() -> str:
    baris = "".join(
        f'<div style="display:flex;gap:12px;align-items:flex-start;padding:12px;border-bottom:2px dashed {TINTA}">'
        f'<div style="border:2px solid {TINTA};{GORES_KECIL}padding:2px 8px;font-weight:700;font-size:14px;flex-shrink:0">P{p}</div>'
        f'<div style="flex:1"><div style="font-size:17px;font-weight:700">{j}</div><div style="font-size:14px;color:#555;margin-top:2px">alasan flag: {a}</div>{garis_teks(1)}</div>'
        f'<div style="border:2px solid {TINTA};{GORES_KECIL}padding:3px 10px;font-size:13px;flex-shrink:0">{s}</div></div>'
        for p, j, a, s in ((1, "Sangat rentan, belum tersentuh program", "skor tinggi + 0 program", "baru"),
                           (1, "Kondisi memburuk, penanganan belum berubah", "skor naik tajam", "ditugaskan"),
                           (2, "Duplikasi pola bantuan", "2 program serupa", "verifikasi"),
                           (3, "Ketidaksesuaian data", "isian bertentangan", "baru")))
    isi = f'''
<div style="display:flex;gap:10px;margin-bottom:14px">{"".join(kotak(t, h="36px", style="font-size:14px") for t in ("jenis flag ▾","prioritas ▾","wilayah ▾","status ▾"))}</div>
{kotak(teks("Kasus prioritas untuk verifikasi", ukuran=18, tebal=True) + f'<div style="margin-top:8px;border:2px solid {TINTA};{GORES_KECIL}overflow:hidden">{baris}</div>', style="padding:14px")}
{kotak(teks("⚠ Flag bukan keputusan final — tetap harus diverifikasi petugas", ukuran=15), garis="dashed", isi_bg=ISI, style="margin-top:14px")}'''
    cor = (catatan("inclusion / exclusion<br>mismatch + rule validation<br>+ anomaly detection", x=1160, y=110, w=240, panah="kiri")
           + catatan("setiap flag bawa ALASAN<br>+ status tindak lanjut", x=1160, y=420, w=230, panah="kiri"))
    return kerangka("04  Mismatch & Anomaly Queue", 3, isi, cor)


def sketsa_recommender() -> str:
    isi = f'''
<div style="display:grid;grid-template-columns:1fr 1.2fr;gap:16px">
  <div style="display:flex;flex-direction:column;gap:14px">
    {kotak(teks("Faktor risiko keluarga", ukuran=17, tebal=True) + "".join(f'<div style="display:inline-block;border:2px solid {TINTA};{GORES_KECIL}padding:2px 10px;margin:4px 6px 0 0;font-size:14px">{t}</div>' for t in ("tanpa dokumen","pendapatan rendah","putus sekolah","RTLH")), h="180px")}
    {kotak(teks("Constraint matching", ukuran=17, tebal=True) + teks("faktor risiko × kriteria program × OPD berwenang × wilayah × periode", ukuran=14, warna="#666") + silang("mesin pencocokan", h="120px"), h="240px", garis="dashed")}
  </div>
  <div style="display:flex;flex-direction:column;gap:12px">
    {teks("Rekomendasi program / OPD", ukuran=18, tebal=True)}
    {"".join(kotak(f'<div style="display:flex;justify-content:space-between"><span style="font-size:17px;font-weight:700">#{i} {n}</span><span style="font-size:14px">{o}</span></div><div style="font-size:14px;color:#555;margin-top:4px">alasan: {a}</div><div style="font-size:13px;color:#555">rule/kriteria dirujuk: {r}</div>', isi_bg=(ISI if i==1 else "#fff")) for i,n,o,a,r in ((1,"Adminduk jemput bola","Disdukcapil","tanpa NIK → program lain tak bisa masuk","syarat administrasi"),(2,"PKH","Dinsos","anak usia sekolah + desil 1","Permensos, desil ≤2"),(3,"Perbaikan rumah","PUPR","4 kriteria RTLH tak terpenuhi","backlog RTLH")))}
  </div>
</div>'''
    cor = catatan("knowledge base program:<br>tujuan, kriteria, OPD, jenis,<br>wilayah, periode — dipelihara OPD", x=60, y=520, w=280)
    return kerangka("05  Intervention Recommender", 4, isi, cor)


def sketsa_simulator() -> str:
    geser = "".join(f'<div style="margin:12px 0"><div style="display:flex;justify-content:space-between;font-size:14px"><span>{t}</span><span>###</span></div><div style="height:4px;background:{TINTA};margin-top:8px;position:relative"><span style="position:absolute;left:{p}%;top:-8px;width:18px;height:18px;border:2px solid {TINTA};border-radius:50%;background:{KERTAS}"></span></div></div>'
                    for t, p in (("pelatihan kerja", 30), ("bantuan pangan", 55), ("perbaikan rumah", 40), ("paket gabungan", 70)))
    isi = f'''
<div style="display:grid;grid-template-columns:340px 1fr;gap:16px">
  {kotak(teks("Parameter skenario", ukuran=17, tebal=True) + geser + kotak("JALANKAN", h="40px", isi_bg=ISI, style="text-align:center;font-weight:700"), style="padding:16px")}
  <div style="display:flex;flex-direction:column;gap:14px">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">{"".join(kotak(teks(l, ukuran=13, warna="#666") + '<div style="font-size:28px;font-weight:700">####</div>', h="84px") for l in ("cakupan sasaran","kebutuhan sumber daya","proyeksi indikatif"))}</div>
    {kotak(teks("Perbandingan skenario A vs B", ukuran=17, tebal=True) + silang("grafik proyeksi indikatif", h="230px"), h="290px")}
    {kotak(teks("⚠ proyeksi berbasis parameter historis / rule — ditandai jelas sebagai simulasi, BUKAN klaim kausal", ukuran=14), garis="dashed", isi_bg=ISI)}
  </div>
</div>'''
    cor = catatan("tahap lanjut: causal inference<br>bila data outcome sudah cukup", x=1120, y=640, w=250, panah="atas")
    return kerangka("06  What-if Policy Simulator", 5, isi, cor)


def sketsa_copilot() -> str:
    isi = f'''
<div style="display:grid;grid-template-columns:1fr 300px;gap:16px;height:100%">
  {kotak(f'<div style="display:flex;flex-direction:column;gap:12px;height:520px">'
           f'<div style="align-self:flex-end;max-width:60%;border:2px solid {TINTA};{GORES_KECIL}padding:8px 12px;font-size:15px">"mengapa wilayah X meningkat risikonya?"</div>'
           f'<div style="align-self:flex-start;max-width:75%;border:2px solid {TINTA};{GORES_KECIL}padding:8px 12px;background:{ISI}">{garis_teks(4)}<div style="font-size:12px;color:#666;margin-top:4px">sumber: [potongan 1] [potongan 2]</div></div>'
           f'<div style="align-self:flex-end;max-width:60%;border:2px solid {TINTA};{GORES_KECIL}padding:8px 12px;font-size:15px">"program apa yang relevan untuk faktor risiko dominan?"</div>'
           f'<div style="align-self:flex-start;max-width:75%;border:2px solid {TINTA};{GORES_KECIL}padding:8px 12px;background:{ISI}">{garis_teks(3)}</div>'
           f'</div><div style="display:flex;gap:8px;margin-top:12px">{kotak("tulis pertanyaan…", h="42px", style="flex:1;color:#888")}{kotak("KIRIM", h="42px", w="90px", isi_bg=ISI, style="text-align:center;font-weight:700")}</div>', style="padding:14px")}
  <div style="display:flex;flex-direction:column;gap:12px">
    {kotak(teks("Knowledge base (RAG)", ukuran=16, tebal=True) + teks("katalog program · faktor risiko · statistik wilayah · metrik model", ukuran=14, warna="#666"), garis="dashed")}
    {kotak(teks("Penghalang privasi", ukuran=16, tebal=True) + teks("NIK / data mentah keluarga TIDAK PERNAH dikirim ke LLM eksternal", ukuran=14, warna="#666"), garis="dashed", isi_bg=ISI)}
    {kotak(teks("Yang tidak dijawab", ukuran=16, tebal=True) + teks("kelayakan bantuan · identitas seseorang · keputusan final", ukuran=14, warna="#666"), garis="dashed")}
  </div>
</div>'''
    cor = catatan("generative AI hanya MENJELASKAN<br>hasil terstruktur — tidak<br>menentukan kelayakan", x=760, y=600, w=280, panah="atas")
    return kerangka("07  AI Policy Copilot", 6, isi, cor)


def sketsa_outcome() -> str:
    tiles = "".join(kotak(teks(l, ukuran=13, warna="#666") + '<div style="font-size:28px;font-weight:700">####</div>', h="84px")
                    for l in ("kasus terverifikasi", "intervensi dicatat", "outcome dinilai", "umpan balik ke model"))
    isi = f'''
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px">{tiles}</div>
<div style="display:grid;grid-template-columns:1.3fr 1fr;gap:16px;margin-bottom:16px">
  {kotak(teks("Before – After state", ukuran=17, tebal=True) + teks("kondisi keluarga sebelum vs sesudah intervensi", ukuran=14, warna="#666") + silang("grafik sebelum / sesudah", h="190px"), h="270px")}
  {kotak(teks("Status alur", ukuran=17, tebal=True) + "".join(f'<div style="display:flex;align-items:center;gap:10px;margin:10px 0"><span style="width:26px;height:26px;border:2px solid {TINTA};border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:14px;font-weight:700">{i}</span><span style="font-size:15px">{t}</span></div>' for i,t in enumerate(("kasus terdeteksi","petugas verifikasi","OPD catat intervensi","outcome dinilai","digital twin diperbarui"),1)), h="270px")}
</div>
{kotak(teks("Feedback loop → evaluasi & perbaikan model", ukuran=17, tebal=True) + silang("daftar intervensi + hasilnya", h="120px"), h="190px", garis="dashed")}'''
    cor = (catatan("penilaian outcome jangan<br>diketik manusia — dihitung<br>dari data gelombang berikutnya", x=1130, y=130, w=260, panah="kiri")
           + catatan("perubahan ≠ sebab!<br>perlu pembanding", x=330, y=590, w=200, panah="atas"))
    return kerangka("08  Outcome Monitoring", 7, isi, cor)


SEMUA = {
    "SketsaMasuk": ("Masuk", sketsa_masuk, None),
    "SketsaCommandCenter": ("01 Executive Command Center", sketsa_command_center, "Ringkasan tren kerentanan, prioritas wilayah, indikator risiko, status intervensi, dan alert baru."),
    "SketsaDigitalTwin": ("02 Household Digital Twin", sketsa_digital_twin, "Profil keluarga dinamis, riwayat perubahan, program diterima, NADI Score, dan top risk drivers."),
    "SketsaGeoAI": ("03 GeoAI Poverty Radar", sketsa_geoai, "Peta cluster risiko sampai tingkat wilayah yang aman ditampilkan; drill-down sesuai hak akses."),
    "SketsaMismatch": ("04 Mismatch & Anomaly Queue", sketsa_mismatch, "Daftar kasus prioritas untuk verifikasi, lengkap dengan alasan flag dan status tindak lanjut."),
    "SketsaRecommender": ("05 Intervention Recommender", sketsa_recommender, "Rekomendasi program/OPD berdasarkan kebutuhan, beserta alasan dan rule/kriteria yang dirujuk."),
    "SketsaSimulator": ("06 What-if Policy Simulator", sketsa_simulator, "Perbandingan skenario intervensi, cakupan sasaran, kebutuhan sumber daya, dan proyeksi indikatif."),
    "SketsaCopilot": ("07 AI Policy Copilot", sketsa_copilot, "Tanya-jawab berbasis knowledge base untuk menjelaskan kondisi, tren, faktor risiko, dan program."),
    "SketsaOutcome": ("08 Outcome Monitoring", sketsa_outcome, "Before-after state, status verifikasi, intervensi, outcome, serta feedback untuk evaluasi model."),
}

__all__ = ["SEMUA"]
