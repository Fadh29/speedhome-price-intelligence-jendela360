# SPEEDHOME Price Intelligence 🏠📊

Aplikasi web analitik cerdas berbasis **Streamlit** untuk memantau, meriset, dan membandingkan harga sewa properti secara *real-time* dari platform **SPEEDHOME Malaysia**.

Aplikasi ini dideploy secara publik dan dapat diakses langsung pada tautan berikut:
👉 **[Live App SPEEDHOME Price Intelligence](https://raihan-fadhlurahman-jendela360-speedhome.streamlit.app/)**

---

## 📂 Panduan Dokumentasi Proyek

Untuk mempermudah penilai (reviewer) maupun pengembang (developer) memahami seluruh aspek aplikasi ini, kami menyediakan tiga berkas dokumentasi utama yang terstruktur rapi:

### 1. [📘 Panduan Pengguna (User Manual)](panduan_pengguna.md)
Panduan lengkap mengenai cara menggunakan aplikasi dari sisi pengguna akhir.
*   **Isi Dokumen**: Cara melakukan pencarian area (Autocomplete vs URL), pemahaman indikator KPI, visualisasi tren pasar, kalkulator ROI tahunan (Gross & Net Yield), serta analisis segmentasi pasar sewa.
*   **Fokus Metrik**: Membedah detail rumus matematika di balik penentuan **Harga Wajar (Fair Price)**, persentase deviasi, dan status kompetisi harga.

### 2. [⚙️ Dokumentasi Kode (Developer Guide)](code_documentation.md)
Panduan teknis mengenai struktur program, dependensi, dan logika kerja kode.
*   **Isi Dokumen**: Stack teknologi (Streamlit, BeautifulSoup, `curl_cffi`, dll.), sitemap compiler (`build_locations.py`), arsitektur diagram aliran data (data flow), cara instalasi lokal (local setup), dan penjelasan fungsi baris demi baris pada berkas Python (`app.py`, `scraper.py`, `build_locations.py`).

### 3. [✅ Laporan Audit & Penjaminan Mutu (QA Report)](audit_report.md)
Laporan pengujian kualitas aplikasi secara menyeluruh sebelum dideploy.
*   **Isi Dokumen**: Tabel kecocokan kriteria wajib & nilai tambah (compliance checklist), hasil pengujian Blackbox (kecepatan load, handling input salah), verifikasi Whitebox (Cloudflare bypass, weighted formulas), rincian unit testing otomatis (`test_app.py`), serta kebijakan Pre-Push QA.

---

## 🛠️ Cara Menjalankan Aplikasi Secara Lokal (Quick Start)

Jika Anda ingin menjalankan aplikasi ini di komputer lokal Anda, pastikan Python 3.9+ sudah terinstal, lalu jalankan perintah berikut:

```bash
# 1. Klon repositori
git clone https://github.com/Fadh29/speedhome-price-intelligence-jendela360.git
cd speedhome-price-intelligence-jendela360

# 2. Instal seluruh pustaka dependensi
pip install -r requirements.txt

# 3. Jalankan pengujian unit otomatis untuk memastikan semua logika aman
python test_app.py

# 4. Luncurkan aplikasi Streamlit
streamlit run app.py
```

Aplikasi Anda akan segera terbuka secara otomatis di browser di alamat lokal `http://localhost:8501`.
