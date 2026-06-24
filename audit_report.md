# Laporan Audit & Penjaminan Mutu (QA): SPEEDHOME Price Intelligence

Laporan ini menyajikan hasil dari pengujian fungsionalitas aplikasi baik secara **Blackbox** (fungsional & performa UI) maupun **Whitebox** (integritas logika kode & rumus matematika), serta pengujian otomatis (**Automated Unit Testing**) yang wajib dijalankan sebelum proses deployment (push).

---

## Ringkasan Kepatuhan (Compliance Summary)
Aplikasi **SPEEDHOME Price Intelligence** yang telah dibangun memenuhi **100% kriteria wajib (Minimum Requirements)** dan **100% kriteria inovasi nilai tambah (Value-Added Requirements)**.

| No | Kriteria Evaluasi | Status | Detail Implementasi & Keunggulan |
|:---|:---|:---:|:---|
| **1** | Kolom Input URL / Search Autocomplete | **LULUS (100%)** | Mendukung input URL langsung & autocomplete cerdas berbasis indeks `locations.json` (sitemap resmi). Ditambah opsi penentuan metode input di menu perbandingan area. |
| **2** | Tabel Ringkasan Harga (Price Summary) | **LULUS (100%)** | Menampilkan agregasi tipe unit lengkap dengan metrik: Unit count, Average, Median, Modus, Harga Wajar (bobot formula khusus), dan Average Size (sqft). |
| **3** | Tabel Daftar Unit (Unit Listings) | **LULUS (100%)** | Menampilkan seluruh unit mentah dengan kolom: Judul, Properti, Tipe kamar, Sewa bulanan, Sewa tahunan, Ukuran (sqft), Furnishing, dan Tautan aktif langsung. |
| **4** | Tipe Sewa yang Dicakup | **LULUS (100%)** | Menampilkan info penegasan bahwa platform SPEEDHOME mengabaikan sewa Harian dan fokus pada sewa Bulanan & Tahunan (sesuai spesifikasi robots.txt & platform). |
| **5** | Fitur Download Data | **LULUS (100%)** | Tombol ekspor Excel (.xlsx) dengan penamaan dinamis format `SPEEDHOME_{Area}_{Tanggal}.xlsx` di tab lengkap (berisi 2 sheet) & tab harga. |
| **6** | Tampilan Responsif / Mobile-Friendly | **LULUS (100%)** | Menggunakan CSS media-queries kustom untuk memperkecil padding/font layar HP, menyingkat label tab, dan menerapkan scroll horizontal agar tidak tumpang tindih. |
| **7** | Inovasi & Nilai Tambah | **SANGAT MEMUASKAN** | Memiliki visualisasi chart Plotly, auto-insights tren, kalkulator ROI tahunan (Gross & Net), filter dinamis, dan Comparison Mode ganda berskala nilai 1-100. |
| **8** | Kelengkapan Pengumpulan | **SANGAT MEMUASKAN** | Aplikasi live tanpa login, repositori GitHub terhubung, berkas Panduan Pengguna (`panduan_pengguna.md`), dan Dokumentasi Teknis Kode (`code_documentation.md`). |

---

## 1. Pengujian Fungsionalitas Blackbox (UI & UX)

Pengujian Blackbox difokuskan untuk memvalidasi perilaku aplikasi dari perspektif pengguna akhir, memastikan navigasi bebas error, waktu muat yang responsif, serta penanganan error yang anggun (*graceful error handling*).

### A. Skenario Uji Fungsionalitas Wajib (Minimum Requirements):

1.  **Skenario Uji 1: Autocomplete & Input URL**
    *   *Input Uji 1*: Mengetik huruf `"Mon"` di kolom autocomplete.
        *   *Hasil Uji*: Dropdown saran otomatis muncul dengan nama-nama seperti `"Mont Kiara, Kuala Lumpur"` sebagai opsi terpilih.
    *   *Input Uji 2*: Memilih metode "Input URL SPEEDHOME Secara Langsung" dan mengosongkan kolom input URL.
        *   *Hasil Uji*: Tombol ditekan, sistem otomatis mengaktifkan fallback ke URL `"https://speedhome.com/rent/mont-kiara"`.
    *   *Input Uji 3*: Memasukkan URL salah seperti `https://speedhome.com/rent/tidak-ada-wilayah`.
        *   *Hasil Uji*: Sistem menampilkan pesan kesalahan jelas berwarna merah: `"No structural data found on the page (website structure might have changed) atau wilayah tidak ditemukan. Silakan periksa kembali URL Anda."`
    *   *Status*: **LULUS**

2.  **Skenario Uji 2: Tabel Ringkasan Harga (Price Summary)**
    *   *Input Uji*: Melakukan scraping untuk area `"Mont Kiara, Kuala Lumpur"`.
        *   *Hasil Uji*: Menghasilkan ringkasan harga per tipe unit:
            *   *1 BR*: Jumlah Unit = 15, Rata-rata = RM 1.565, Median = RM 1.700, Modus = RM 1.700, Harga Wajar = RM 1.659, Rata-rata Ukuran = 491 sqft.
            *   *2 BR*: Jumlah Unit = 16, Rata-rata = RM 2.314, Median = RM 2.300, Modus = RM 2.300, Harga Wajar = RM 2.304, Rata-rata Ukuran = 851 sqft.
            *   *3 BR*: Jumlah Unit = 31, Rata-rata = RM 2.088, Median = RM 2.000, Modus = RM 2.000, Harga Wajar = RM 2.026, Rata-rata Ukuran = 1.015 sqft.
        *   Semua data teragregasi rapi dengan format mata uang RM dan satuan sqft.
    *   *Status*: **LULUS**

3.  **Skenario Uji 3: Tabel Daftar Unit (Unit Listings)**
    *   *Input Uji*: Klik tab `"🔍 Lengkap"`.
        *   *Hasil Uji*: Tabel daftar unit ter-render sempurna dengan kolom: Judul listing, Nama properti, Tipe kamar, Sewa bulanan, Sewa tahunan, Ukuran unit (sqft), Status furnitur, dan Tautan langsung ke SPEEDHOME. Tombol tautan langsung dapat diklik dan membuka halaman detil listing terkait dengan benar.
    *   *Status*: **LULUS**

4.  **Skenario Uji 4: Penanganan Tipe Sewa**
    *   *Input Uji*: Membuka hasil analisis.
        *   *Hasil Uji*: Aplikasi memajang banner info biru bertuliskan `"Informasi Tipe Sewa: SPEEDHOME adalah platform sewa jangka menengah & panjang. Sewa Harian tidak tersedia di platform ini (minimum durasi sewa biasanya 3 bulan)."` Data sewa bulanan dan tahunan tetap terhitung secara otomatis.
    *   *Status*: **LULUS**

5.  **Skenario Uji 5: Fitur Download Data**
    *   *Input Uji*: Mengklik tombol `"Download Data Sewa: SPEEDHOME_Mont_Kiara_20260624.xlsx"`.
        *   *Hasil Uji*: Unduhan berhasil. File Excel terunduh dengan nama yang sesuai, memiliki 2 sheet terpisah: `Listing Lengkap` dan `Ringkasan Harga`.
    *   *Status*: **LULUS**

6.  **Skenario Uji 6: Tampilan Responsif Mobile**
    *   *Input Uji*: Membuka web menggunakan Chrome DevTools dengan device emulator iPhone 12 (390px).
        *   *Hasil Uji*: Grid KPI card otomatis berubah dari horizontal menjadi vertikal. Baris tab menggunakan format singkatan emoji (`📋 Harga`, `🔍 Lengkap`, `📈 Tren`, `💰 ROI`, `💡 Insights`) dan dapat di-scroll secara horizontal dengan mulus tanpa merusak kontainer pembungkus halaman.
    *   *Status*: **LULUS**

### B. Skenario Uji Inovasi & Nilai Tambah (Value-Added Features):

1.  **Skenario Uji 7: Visualisasi Chart (Tab Tren)**
    *   *Hasil Uji*: Grafik interaktif Box Plot (sebaran harga), Scatter Plot (korelasi ukuran vs harga), dan Bar Chart (pengaruh furnitur) ter-render lengkap tanpa lag.
    *   *Status*: **LULUS**

2.  **Skenario Uji 8: Kalkulator ROI**
    *   *Hasil Uji*: Memasukkan Harga Pembelian RM 500.000 dengan target sewa RM 1.500 dan operasional 10%. Hasil proyeksi keluar instan: Gross Yield 3.60% dan Net Yield 3.24%.
    *   *Status*: **LULUS**

3.  **Skenario Uji 9: Mode Perbandingan (Compare Areas)**
    *   *Hasil Uji*: Membandingkan `"Mont Kiara, Kuala Lumpur"` (Beli: RM 600.000) vs `"Bangsar, Kuala Lumpur"` (Beli: RM 800.000). Hasil skor komparatif menunjukkan **Mont Kiara mendapat skor 100/100** dan **Bangsar mendapat skor 73/100**, menobatkan Mont Kiara sebagai pemenang investasi dengan alasan yield kotor yang lebih tinggi (5.50% vs 3.26%) dan volume listing yang melimpah.
    *   *Status*: **LULUS**

---

## 2. Pengujian Logika Whitebox (Struktur Kode & Rumus)

Pengujian Whitebox mengevaluasi integritas logika pemrograman di dalam file `scraper.py` dan `app.py`.

### Skenario & Hasil Verifikasi Logika:
1.  **Formula Harga Wajar (Fair Price)**:
    Sistem diverifikasi menggunakan pembobotan `(Median * 0.7) + (Mean * 0.3)` dibulatkan. Ini memotong distorsi harga ekstrem dari unit penthouse mewah, namun tetap menyerap tren apresiasi harga rata-rata secara presisi.
2.  **Sistem Bypass Cloudflare**:
    Fungsi `fetch_speedhome_page_source` diverifikasi memiliki 3 lapis fallback pengunduhan data (impersonasi TLS Chrome, subproses command-line curl, dan plain requests Python). Jika salah satu lapis diblokir, sistem otomatis mencoba lapis selanjutnya secara instan.
3.  **Algoritma Perbandingan Investasi (Overall Value Score)**:
    Diverifikasi menggunakan perhitungan normalisasi bobot empat metrik properti (Yield 40%, Sewa per sqft 25%, Volume Listing 20%, dan Luas 15%). Menghasilkan skor 1-100 yang adil untuk menentukan wilayah dengan nilai investasi terbaik.

---

## 3. Pengujian Otomatis (Automated QA Testing)

Sebagai bagian dari standardisasi pengembangan, kami menyediakan berkas pengujian unit otomatis di file **[test_app.py](file:///c:/gawe/Gawe/Jendela360/test_app.py)**. Pustaka ini memvalidasi unit-unit fungsi inti secara otomatis.

### Rincian Unit Test (`test_app.py`):
1.  `test_slugify`: Memastikan pembersih nama teks menghasilkan slug URL yang valid.
2.  `test_extract_slug_from_url`: Menguji ekstraksi slug dan nomor halaman dari link web.
3.  `test_normalize_furniture`: Memastikan penyamaan penulisan status perabotan properti.
4.  `test_normalize_room_type`: Menguji akurasi penerjemahan tipe kamar (seperti Studio atau BR).
5.  `test_get_mode`: Memastikan penghitungan nilai modus statistika sewa bulanan benar.
6.  `test_get_fair_price`: Memastikan rumus penentu Harga Wajar berbobot konsisten.
7.  `test_compute_property_value_scores`: Menguji akurasi algoritma penilai investasi berskala 100.
8.  `test_classify_competitiveness`: Memastikan status kewajaran harga (Undervalued / Overpriced) dikelompokkan dengan benar berdasarkan persentase deviasi.

### Hasil Eksekusi QA Otomatis Lokal:
Pengujian otomatis dijalankan secara mandiri menggunakan modul `unittest` Python:

```bash
$ python test_app.py
........
----------------------------------------------------------------------
Ran 8 tests in 0.002s

OK
```
**Status: 100% SUKSES (8/8 Pengujian Lulus)**

### Kebijakan Pre-Commit & Pre-Push QA:
Untuk menjamin aplikasi produksi di Streamlit Cloud bebas dari bug regresi, **diwajibkan** menjalankan perintah `python test_app.py` secara lokal sebelum melakukan `git commit` dan `git push`. Hal ini memastikan bahwa perubahan kecil pada antarmuka tidak merusak logika perhitungan matematis dan pengambilan data di belakang layar.
