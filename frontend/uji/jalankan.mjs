/**
 * Pemasang lingkungan untuk uji asap antarmuka.
 *
 * Berkas ini menyiapkan peramban tiruan lebih dahulu, baru memuat berkas uji.
 * Urutannya tidak boleh terbalik: react-dom membaca `window` dan `document`
 * pada saat modulnya dimuat, sehingga memuatnya sebelum jsdom siap akan gagal
 * dengan galat yang tidak menyebut sebab sesungguhnya.
 *
 * Peladen NADI harus sudah berjalan. Uji ini sengaja memanggil API yang
 * sungguhan - lihat alasannya pada docstring uji/asap.tsx.
 */

import { JSDOM } from "jsdom";

const ASAL = process.env.NADI_ASAL ?? "http://127.0.0.1:8000";
const AKUN = {
  nama_pengguna: process.env.NADI_UJI_AKUN ?? "admin",
  sandi: process.env.NADI_UJI_SANDI ?? "NadiAdmin#2026",
};

const HIJAU = "\x1b[92m";
const MERAH = "\x1b[91m";
const ABU = "\x1b[90m";
const PADAM = "\x1b[0m";

// --- 1. Peramban tiruan ----------------------------------------------------
const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: ASAL,
  pretendToBeVisual: true,
});

// Node 22 menyediakan `navigator` sebagai properti hanya-baca, sehingga
// penugasan biasa gagal. defineProperty menimpanya tanpa keberatan.
function pasangGlobal(nama, nilai) {
  Object.defineProperty(globalThis, nama, {
    value: nilai,
    writable: true,
    configurable: true,
  });
}

for (const nama of [
  "window",
  "document",
  "navigator",
  "location",
  "localStorage",
  "sessionStorage",
  "HTMLElement",
  "SVGElement",
  "Element",
  "Node",
  "Event",
  "CustomEvent",
  "MouseEvent",
  "KeyboardEvent",
  "DOMRect",
  "getComputedStyle",
  "matchMedia",
]) {
  const nilai = nama === "window" ? dom.window : dom.window[nama];
  if (nilai !== undefined) pasangGlobal(nama, nilai);
}
pasangGlobal("requestAnimationFrame", (f) => setTimeout(() => f(Date.now()), 16));
pasangGlobal("cancelAnimationFrame", (id) => clearTimeout(id));
pasangGlobal("ResizeObserver", class {
  observe() {}
  unobserve() {}
  disconnect() {}
});
// Recharts mengukur wadahnya sebelum menggambar. Di dalam jsdom setiap elemen
// berukuran nol, sehingga grafiknya tidak pernah tergambar dan halaman tampak
// kosong padahal sehat. Ukuran ditetapkan supaya pengukuran itu masuk akal.
Object.defineProperties(dom.window.HTMLElement.prototype, {
  offsetWidth: { get: () => 1024 },
  offsetHeight: { get: () => 768 },
  clientWidth: { get: () => 1024 },
  clientHeight: { get: () => 768 },
});
dom.window.SVGElement.prototype.getBBox = () => ({ x: 0, y: 0, width: 100, height: 20 });
pasangGlobal("IS_REACT_ACT_ENVIRONMENT", true);

// --- 2. fetch dengan alamat relatif ---------------------------------------
const fetchAsli = globalThis.fetch;
pasangGlobal("fetch", (masukan, opsi) => {
  const jalur = typeof masukan === "string" ? masukan : masukan.url;
  return fetchAsli(jalur.startsWith("/") ? `${ASAL}${jalur}` : jalur, opsi);
});

// --- 3. Masuk lebih dahulu -------------------------------------------------
async function siapkanSesi() {
  const r = await fetchAsli(`${ASAL}/api/masuk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(AKUN),
  });
  if (!r.ok) throw new Error(`Gagal masuk sebagai ${AKUN.nama_pengguna}: HTTP ${r.status}`);
  const d = await r.json();
  localStorage.setItem("nadi.token", d.token);
  localStorage.setItem("nadi.pengguna", JSON.stringify(d.pengguna));
  return d.token;
}

async function ambilKodeKeluarga(token) {
  const r = await fetchAsli(`${ASAL}/api/keluarga/cari?batas=1`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) return "KLG-0000-0000";
  const d = await r.json();
  const butir = d.keluarga ?? d.hasil ?? d.data ?? [];
  return butir[0]?.kode ?? butir[0]?.kode_semu ?? "KLG-0000-0000";
}

// --- 4. Jalankan -----------------------------------------------------------
const token = await siapkanSesi();
const kode = await ambilKodeKeluarga(token);
console.log(`\n  Peladen : ${ASAL}`);
console.log(`  Akun    : ${AKUN.nama_pengguna}`);
console.log(`  Keluarga contoh: ${kode}\n`);

const { jalankan } = await import("./dist/asap.js");
const hasil = await jalankan(kode);

let gagal = 0;
for (const h of hasil) {
  if (h.lulus) {
    console.log(`  ${HIJAU}LULUS${PADAM}  ${h.nama.padEnd(22)} ${ABU}${h.panjangTeks} karakter${PADAM}`);
  } else {
    gagal += 1;
    console.log(`  ${MERAH}GAGAL${PADAM}  ${h.nama.padEnd(22)} ${h.sebab}`);
    if (h.cuplikan) console.log(`         ${ABU}tergambar: "${h.cuplikan}"${PADAM}`);
    for (const g of h.galat.slice(0, 2)) console.log(`         ${ABU}${g}${PADAM}`);
  }
}

console.log(`\n  ${hasil.length - gagal}/${hasil.length} halaman tergambar dengan isi.\n`);
dom.window.close();
process.exit(gagal ? 1 : 0);
