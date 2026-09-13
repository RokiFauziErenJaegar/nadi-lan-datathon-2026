"""Perkakas penyusun salindia presentasi.

Sama seperti ``dokumen.py``, modul ini memisahkan isi dari bentuk: naskah
presentasi ditulis sebagai pemanggilan blok, dan modul ini yang menetapkan
huruf, warna, dan tata letaknya.

Satu keputusan rancangan menentukan seluruh gaya di sini: **satu salindia,
satu gagasan**. Dewan juri membaca puluhan presentasi; yang bertahan di ingatan
bukan salindia yang memuat paling banyak keterangan, melainkan yang dapat
dipahami dalam tiga detik lalu ditinggalkan. Karena itu tidak ada satu pun
salindia pada berkas ini yang memuat lebih dari satu tabel, satu grafik, atau
satu daftar - dan angka yang penting selalu ditulis besar, bukan diselipkan di
tengah kalimat.

Grafik dibangkitkan dari basis data yang sesungguhnya lewat matplotlib, lalu
disisipkan sebagai gambar. Tidak ada angka pada presentasi ini yang diketik
tangan.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

# ---------------------------------------------------------------------------
# Palet
# ---------------------------------------------------------------------------
BIRU = RGBColor(0x1E, 0x5A, 0x8F)
BIRU_MUDA = RGBColor(0x2A, 0x78, 0xD6)
TINTA = RGBColor(0x0F, 0x17, 0x2A)
TINTA_KEDUA = RGBColor(0x47, 0x55, 0x69)
TINTA_REDUP = RGBColor(0x94, 0xA3, 0xB8)
PUTIH = RGBColor(0xFF, 0xFF, 0xFF)
LATAR = RGBColor(0xFF, 0xFF, 0xFF)
LATAR_LEMBUT = RGBColor(0xF1, 0xF5, 0xF9)
HIJAU = RGBColor(0x0C, 0xA3, 0x0C)
MERAH = RGBColor(0xD0, 0x3B, 0x3B)
KUNING = RGBColor(0xFA, 0xB2, 0x19)
KELABU = RGBColor(0xCB, 0xD5, 0xE1)

HURUF = "Segoe UI"
HURUF_TEBAL = "Segoe UI Semibold"

LEBAR = Inches(13.333)
TINGGI = Inches(7.5)
TEPI = Inches(0.85)


def hx(w: RGBColor) -> str:
    """RGBColor menjadi untai warna yang dikenali matplotlib."""
    return "#" + str(w)


class Dek:
    """Penyusun presentasi dengan gaya tetap."""

    def __init__(self, folder_gambar: pathlib.Path) -> None:
        self.prs = Presentation()
        self.prs.slide_width = LEBAR
        self.prs.slide_height = TINGGI
        self.gambar = folder_gambar
        self.gambar.mkdir(parents=True, exist_ok=True)
        self.catatan_bicara: list[str] = []

    # -- dasar ------------------------------------------------------------
    def _kosong(self, latar: RGBColor = LATAR):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        f = s.background.fill
        f.solid()
        f.fore_color.rgb = latar
        return s

    def _teks(self, s, kiri, atas, lebar, tinggi, isi, *, ukuran=18, warna=TINTA,
              tebal=False, rata=PP_ALIGN.LEFT, huruf=HURUF, spasi=1.15, jangkar=MSO_ANCHOR.TOP):
        kotak = s.shapes.add_textbox(kiri, atas, lebar, tinggi)
        tf = kotak.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = jangkar
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        baris = isi.split("\n")
        for i, b in enumerate(baris):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = rata
            p.line_spacing = spasi
            for potongan, tbl in _pecah_tebal(b):
                r = p.add_run()
                r.text = potongan
                r.font.size = Pt(ukuran)
                r.font.name = HURUF_TEBAL if (tebal or tbl) else huruf
                r.font.bold = tebal or tbl
                r.font.color.rgb = warna
        return kotak

    def _pita(self, s, warna=BIRU, tinggi=Inches(0.11)):
        b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, LEBAR, tinggi)
        b.fill.solid()
        b.fill.fore_color.rgb = warna
        b.line.fill.background()
        b.shadow.inherit = False

    def _nomor(self, s) -> None:
        n = len(self.prs.slides._sldIdLst)
        if n <= 1:
            return
        self._teks(s, LEBAR - Inches(1.2), TINGGI - Inches(0.55), Inches(0.6), Inches(0.3),
                   str(n), ukuran=10, warna=TINTA_REDUP, rata=PP_ALIGN.RIGHT)

    def _catat(self, s, teks: str) -> None:
        """Catatan pembicara - tidak tampil di layar, hanya di tampilan penyaji."""
        s.notes_slide.notes_text_frame.text = teks

    # -- jenis salindia ---------------------------------------------------
    def sampul(self, judul, anak, baris: list[str], catatan: str = "") -> None:
        s = self._kosong()
        b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.42), TINGGI)
        b.fill.solid()
        b.fill.fore_color.rgb = BIRU
        b.line.fill.background()
        b.shadow.inherit = False

        self._teks(s, Inches(1.5), Inches(2.15), Inches(10.5), Inches(1.5),
                   judul, ukuran=64, warna=BIRU, tebal=True)
        self._teks(s, Inches(1.55), Inches(3.35), Inches(10.5), Inches(0.8),
                   anak, ukuran=22, warna=TINTA_KEDUA)
        self._teks(s, Inches(1.55), Inches(4.9), Inches(10.5), Inches(1.6),
                   "\n".join(baris), ukuran=13, warna=TINTA_REDUP, spasi=1.5)
        if catatan:
            self._catat(s, catatan)

    def bagian(self, nomor: str, judul: str, anak: str = "", catatan: str = "") -> None:
        """Salindia pemisah bagian."""
        s = self._kosong(BIRU)
        self._teks(s, TEPI, Inches(2.6), Inches(1.5), Inches(0.9),
                   nomor, ukuran=54, warna=RGBColor(0x7F, 0xA8, 0xCC), tebal=True)
        self._teks(s, TEPI, Inches(3.5), Inches(11.5), Inches(1.2),
                   judul, ukuran=40, warna=PUTIH, tebal=True)
        if anak:
            self._teks(s, TEPI, Inches(4.75), Inches(10.5), Inches(0.8),
                       anak, ukuran=17, warna=RGBColor(0xC7, 0xDA, 0xEE))
        self._nomor(s)
        if catatan:
            self._catat(s, catatan)

    def judul_isi(self, judul: str, anak: str = "") -> tuple:
        """Kerangka salindia biasa. Kembalikan (salindia, ordinat isi)."""
        s = self._kosong()
        self._pita(s)
        self._teks(s, TEPI, Inches(0.62), Inches(11.6), Inches(0.7),
                   judul, ukuran=28, warna=BIRU, tebal=True)
        y = Inches(1.42)
        if anak:
            self._teks(s, TEPI, Inches(1.32), Inches(11.6), Inches(0.5),
                       anak, ukuran=14, warna=TINTA_KEDUA)
            y = Inches(2.0)
        self._nomor(s)
        return s, y

    def angka_besar(self, judul: str, angka: list[tuple[str, str, str]], catatan: str = "") -> None:
        """Salindia berisi beberapa angka besar. Tiap butir: (angka, label, keterangan)."""
        s, y = self.judul_isi(judul)
        n = len(angka)
        lebar_kolom = (LEBAR - 2 * TEPI - Inches(0.4) * (n - 1)) / n
        for i, (nilai, label, ket) in enumerate(angka):
            x = TEPI + i * (lebar_kolom + Inches(0.4))
            kotak = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, lebar_kolom, Inches(3.0))
            kotak.fill.solid()
            kotak.fill.fore_color.rgb = LATAR_LEMBUT
            kotak.line.fill.background()
            kotak.shadow.inherit = False
            kotak.adjustments[0] = 0.06
            self._teks(s, x + Inches(0.3), y + Inches(0.42), lebar_kolom - Inches(0.6), Inches(1.1),
                       nilai, ukuran=46, warna=BIRU, tebal=True)
            self._teks(s, x + Inches(0.3), y + Inches(1.5), lebar_kolom - Inches(0.6), Inches(0.4),
                       label, ukuran=14, warna=TINTA, tebal=True)
            self._teks(s, x + Inches(0.3), y + Inches(1.95), lebar_kolom - Inches(0.6), Inches(0.9),
                       ket, ukuran=11, warna=TINTA_KEDUA, spasi=1.25)
        if catatan:
            self._catat(s, catatan)

    def poin(self, judul: str, butir: list[str], anak: str = "", catatan: str = "",
             ukuran: int = 17) -> None:
        s, y = self.judul_isi(judul, anak)
        for b in butir:
            titik = s.shapes.add_shape(MSO_SHAPE.OVAL, TEPI, y + Inches(0.13),
                                       Inches(0.13), Inches(0.13))
            titik.fill.solid()
            titik.fill.fore_color.rgb = BIRU_MUDA
            titik.line.fill.background()
            titik.shadow.inherit = False
            kotak = self._teks(s, TEPI + Inches(0.38), y, LEBAR - 2 * TEPI - Inches(0.4),
                               Inches(0.6), b, ukuran=ukuran, spasi=1.25)
            y += Emu(int(kotak.text_frame.paragraphs[0].line_spacing * Pt(ukuran) *
                         (1 + len(b) // 95))) + Inches(0.42)
        if catatan:
            self._catat(s, catatan)

    def dua_kolom(self, judul: str, kiri_judul: str, kiri: list[str],
                  kanan_judul: str, kanan: list[str], catatan: str = "") -> None:
        s, y = self.judul_isi(judul)
        lebar_kolom = (LEBAR - 2 * TEPI - Inches(0.6)) / 2
        for i, (jt, isi, warna) in enumerate(
            ((kiri_judul, kiri, MERAH), (kanan_judul, kanan, HIJAU))
        ):
            x = TEPI + i * (lebar_kolom + Inches(0.6))
            kotak = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, lebar_kolom, Inches(4.2))
            kotak.fill.solid()
            kotak.fill.fore_color.rgb = LATAR_LEMBUT
            kotak.line.fill.background()
            kotak.shadow.inherit = False
            kotak.adjustments[0] = 0.04
            garis = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.07), Inches(4.2))
            garis.fill.solid()
            garis.fill.fore_color.rgb = warna
            garis.line.fill.background()
            garis.shadow.inherit = False
            self._teks(s, x + Inches(0.4), y + Inches(0.35), lebar_kolom - Inches(0.8),
                       Inches(0.5), jt, ukuran=18, warna=warna, tebal=True)
            yy = y + Inches(1.0)
            for b in isi:
                self._teks(s, x + Inches(0.4), yy, lebar_kolom - Inches(0.8), Inches(0.6),
                           b, ukuran=14, spasi=1.3)
                yy += Inches(0.5) + Inches(0.28) * (len(b) // 55)
        if catatan:
            self._catat(s, catatan)

    def gambar_penuh(self, judul: str, berkas: pathlib.Path, anak: str = "",
                     catatan: str = "", keterangan: str = "") -> None:
        s, y = self.judul_isi(judul, anak)
        tinggi_maks = TINGGI - y - Inches(0.9 if keterangan else 0.5)
        pic = s.shapes.add_picture(str(berkas), TEPI, y, height=int(tinggi_maks))
        if pic.width > LEBAR - 2 * TEPI:
            rasio = (LEBAR - 2 * TEPI) / pic.width
            pic.width = int(pic.width * rasio)
            pic.height = int(pic.height * rasio)
        pic.left = int((LEBAR - pic.width) / 2)
        if keterangan:
            self._teks(s, TEPI, TINGGI - Inches(0.78), LEBAR - 2 * TEPI, Inches(0.45),
                       keterangan, ukuran=12, warna=TINTA_KEDUA, rata=PP_ALIGN.CENTER)
        if catatan:
            self._catat(s, catatan)

    def tabel(self, judul: str, kepala: list[str], baris: list[list[str]],
              lebar_kolom: list[float] | None = None, anak: str = "", catatan: str = "",
              ukuran: int = 12) -> None:
        s, y = self.judul_isi(judul, anak)
        n_baris, n_kolom = len(baris) + 1, len(kepala)
        lebar_total = LEBAR - 2 * TEPI
        tinggi = min(Inches(0.44) * n_baris, TINGGI - y - Inches(0.5))
        bentuk = s.shapes.add_table(n_baris, n_kolom, TEPI, y, lebar_total, tinggi)
        t = bentuk.table
        if lebar_kolom:
            total = sum(lebar_kolom)
            for i, w in enumerate(lebar_kolom[:n_kolom]):
                t.columns[i].width = int(lebar_total * w / total)

        for i, judul_kolom in enumerate(kepala):
            sel = t.cell(0, i)
            sel.fill.solid()
            sel.fill.fore_color.rgb = BIRU
            p = sel.text_frame.paragraphs[0]
            # Selalu tambahkan run secara eksplisit, tidak lewat `sel.text`.
            # Judul kolom yang sengaja dikosongkan - lazim pada kolom nomor -
            # tidak menghasilkan satu run pun, sehingga penataan gayanya gagal.
            r = p.add_run()
            r.text = judul_kolom
            r.font.size = Pt(ukuran)
            r.font.bold = True
            r.font.name = HURUF_TEBAL
            r.font.color.rgb = PUTIH
            sel.vertical_anchor = MSO_ANCHOR.MIDDLE

        for r, isi in enumerate(baris, 1):
            for c, nilai in enumerate(isi[:n_kolom]):
                sel = t.cell(r, c)
                sel.fill.solid()
                sel.fill.fore_color.rgb = PUTIH if r % 2 else LATAR_LEMBUT
                tf = sel.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                for potongan, tbl in _pecah_tebal(str(nilai)):
                    run = p.add_run()
                    run.text = potongan
                    run.font.size = Pt(ukuran)
                    run.font.bold = tbl
                    run.font.name = HURUF_TEBAL if tbl else HURUF
                    run.font.color.rgb = TINTA
                sel.vertical_anchor = MSO_ANCHOR.MIDDLE
        if catatan:
            self._catat(s, catatan)

    def kutipan(self, teks: str, sumber: str = "", catatan: str = "") -> None:
        s = self._kosong(BIRU)
        self._teks(s, Inches(1.4), Inches(2.3), Inches(10.5), Inches(2.6),
                   teks, ukuran=30, warna=PUTIH, tebal=True, spasi=1.3)
        if sumber:
            self._teks(s, Inches(1.4), Inches(5.4), Inches(10.5), Inches(0.5),
                       sumber, ukuran=14, warna=RGBColor(0xC7, 0xDA, 0xEE))
        self._nomor(s)
        if catatan:
            self._catat(s, catatan)

    def tempat_layar(self, judul: str, keterangan: str, anak: str = "", catatan: str = "") -> None:
        """Bingkai kosong untuk tangkapan layar yang harus disisipkan sendiri."""
        s, y = self.judul_isi(judul, anak)
        tinggi = TINGGI - y - Inches(0.8)
        kotak = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, TEPI, y,
                                   LEBAR - 2 * TEPI, tinggi)
        kotak.fill.solid()
        kotak.fill.fore_color.rgb = LATAR_LEMBUT
        kotak.line.color.rgb = KELABU
        kotak.line.width = Pt(1.5)
        kotak.line.dash_style = 4  # putus-putus
        kotak.shadow.inherit = False
        self._teks(s, TEPI, y + tinggi / 2 - Inches(0.4), LEBAR - 2 * TEPI, Inches(0.9),
                   f"[ Sisipkan tangkapan layar: {keterangan} ]",
                   ukuran=15, warna=TINTA_REDUP, rata=PP_ALIGN.CENTER)
        if catatan:
            self._catat(s, catatan)

    def simpan(self, jalur: pathlib.Path) -> pathlib.Path:
        jalur.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(jalur))
        return jalur


def _pecah_tebal(teks: str) -> list[tuple[str, bool]]:
    bagian: list[tuple[str, bool]] = []
    sisa = teks
    while "**" in sisa:
        awal = sisa.index("**")
        if awal:
            bagian.append((sisa[:awal], False))
        sisa = sisa[awal + 2:]
        if "**" not in sisa:
            bagian.append(("**" + sisa, False))
            return bagian
        akhir = sisa.index("**")
        bagian.append((sisa[:akhir], True))
        sisa = sisa[akhir + 2:]
    if sisa:
        bagian.append((sisa, False))
    return bagian or [("", False)]


# ---------------------------------------------------------------------------
# Gaya grafik
# ---------------------------------------------------------------------------
def siapkan_matplotlib() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
        "axes.edgecolor": hx(TINTA_REDUP),
        "axes.labelcolor": hx(TINTA_KEDUA),
        "axes.titlecolor": hx(TINTA),
        "xtick.color": hx(TINTA_KEDUA),
        "ytick.color": hx(TINTA_KEDUA),
        "grid.color": "#E2E8F0",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 12,
    })


__all__ = ["BIRU", "BIRU_MUDA", "Dek", "HIJAU", "KELABU", "KUNING", "MERAH",
           "TINTA", "TINTA_KEDUA", "TINTA_REDUP", "hx", "siapkan_matplotlib"]
