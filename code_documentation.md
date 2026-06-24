# Dokumentasi Kode & Panduan Arsitektur: SPEEDHOME Price Intelligence

Berkas ini menyediakan dokumentasi teknis yang komprehensif bagi pengembang (developer) maupun orang awam mengenai arsitektur aplikasi, teknologi yang digunakan, alur scraping data, dan rincian fungsi baris demi baris pada kode **SPEEDHOME Price Intelligence**.

---

## 1. Teknologi & Lokasi Deployment (Tech Stack)

### Stack Teknologi yang Digunakan:
*   **Streamlit (v1.x)**: Framework aplikasi Python berbasis web yang digunakan untuk merancang antarmuka pengguna (UI) yang interaktif tanpa memerlukan backend terpisah.
*   **BeautifulSoup4 (bs4)**: Pustaka parsing dokumen HTML/XML yang digunakan untuk meramban struktur DOM (Document Object Model) dan mengekstrak data dari tag-tag HTML.
*   **Pandas & NumPy**: Digunakan untuk manajemen data tabular (`DataFrame`), pembersihan tipe data, dan komputasi agregasi statistik (seperti rata-rata, median, modus, standar deviasi, dan penentuan deviasi).
*   **Plotly Express**: Library visualisasi data interaktif untuk merender grafik Box Plot, Scatter Plot, dan Bar Chart.
*   **curl_cffi (Chrome Impersonation)**: HTTP Client canggih yang mampu memanipulasi TLS fingerprint (sidik jari TLS) agar terdeteksi sebagai browser Google Chrome asli, krusial untuk menembus proteksi Cloudflare.
*   **OpenPyXL**: Mesin penulisan berkas Excel (`.xlsx`) dalam memori untuk fitur ekspor data.

### Lokasi & Mekanisme Deployment:
*   **Platform**: Streamlit Community Cloud.
*   **Alamat Live**: **[SPEEDHOME Price Intelligence](https://raihan-fadhlurahman-jendela360-speedhome.streamlit.app/)**
*   **Sistem Sinkronisasi (CI/CD)**: Terkoneksi ke repositori GitHub `Fadh29/speedhome-price-intelligence-jendela360`. Setiap kali Anda melakukan git commit dan `git push origin main`, platform Streamlit Cloud akan mendeteksi perubahan berkas tersebut secara otomatis dan langsung melakukan deploy pembaruan secara *real-time* dalam waktu ~1-2 menit.

---

## 2. Metodologi Web Scraping & Konsep Pengambilan Data

Bagi Anda yang baru mempelajari pemrograman, *Web Scraping* adalah teknik otomatisasi untuk membaca halaman web eksternal dan mengambil informasi spesifik darinya untuk disimpan dalam basis data terstruktur.

Berikut adalah tahapan metodologi scraping yang digunakan oleh aplikasi ini:

```
[Pengguna Input URL/Area] 
          │
          ▼
[HTTP Request dengan curl_cffi] ──► (Bypass Cloudflare: Meniru sidik jari TLS Chrome)
          │
          ▼
    [Dapatkan HTML]
          │
          ▼
[BeautifulSoup Parsing]
          ├─► Lapis 1: Parsing tag <script type="application/ld+json"> (Data JSON-LD Resmi)
          └─► Lapis 2 (Fallback): Cari tag <div> dengan CSS class "anchor-rent-card"
          │
          ▼
[Normalisasi Data Properti] ──► (BR Kategori, Furnitur fully/partially/unfurnished)
          │
          ▼
[Hasil Tersimpan di Session State]
```

### Penjelasan Konsep Detil:

1.  **Menghindari Proteksi Bot (Bypass Cloudflare)**:
    Situs web besar seperti SPEEDHOME dilindungi oleh Cloudflare untuk mencegah bot membebani server mereka. Bot standar (seperti pustaka `requests` Python) mengirimkan pola jabat tangan TLS (TLS handshake) yang sangat kaku dan berbeda dari browser manusia, sehingga langsung diblokir dengan halaman tantangan (challenge page).
    *   *Solusi Kita*: Kita menggunakan **`curl_cffi`** yang meminjam konfigurasi TLS asli milik Chrome. Server Cloudflare akan melihat request kita sebagai manusia biasa yang menggunakan browser Google Chrome di sistem operasi Windows/Mac, sehingga data dapat lolos diunduh.
    
2.  **Mengambil Data Terstruktur dari JSON-LD**:
    Halaman modern biasanya memuat metadata SEO terstruktur dalam format JSON-LD di dalam tag `<script type="application/ld+json">`. Format ini sangat disukai karena datanya sangat rapi (berupa kamus/dictionary Python) dan tidak mudah rusak jika pemilik web mengubah desain visual HTML mereka.
    *   *Solusi Kita*: Pertama-tama scraper akan mencari tag skema `ItemList` ini. Jika ada, data nama unit, harga, tipe sewa, dan URL langsung dibaca dalam hitungan milidetik.

3.  **Mekanisme Cadangan (DOM Fallback Parsing)**:
    Jika pemilik web mematikan fitur JSON-LD pada halaman tertentu, scraper tidak boleh mati.
    *   *Solusi Kita*: Kita mengimplementasikan *parser DOM* cadangan. Menggunakan BeautifulSoup untuk menyisir seluruh dokumen HTML, mencari elemen kotak kartu sewa (`div.anchor-rent-card`), lalu membongkar judul (`h2` atau `h3`), harga sewa bulanan, ukuran, dan tautan sewa dari atribut link (`href`).

4.  **Normalisasi Kategori**:
    Data dari internet seringkali tidak rapi. Ada pemilik yang menulis perabotan sebagai "Fully", "Fully Furnished", atau "Fully-Furnished". Fungsi normalisasi bertugas merapikan variasi teks acak tersebut ke dalam kategori baku (`Fully Furnished`, `Partially Furnished`, `Unfurnished`) agar analisis statistik di chart visualisasi akurat.

---

## 3. Struktur Berkas Proyek (Project Directory Tree)

```
Jendela360/
├── app.py                  # Antarmuka web Streamlit & kalkulasi metrik finansial
├── scraper.py              # Logika pengambilan data & bypass Cloudflare
├── build_locations.py      # Script pembuat/kompilasi data autocomplete
├── locations.json          # File referensi nama wilayah & slug URL (dihasilkan otomatis)
├── requirements.txt        # Daftar dependency pustaka Python yang wajib diinstal
├── packages.txt            # Dependency OS Linux untuk Streamlit Cloud (install curl)
├── panduan_pengguna.md     # Panduan cara memakai aplikasi untuk user umum
└── code_documentation.md   # Dokumen ini (panduan teknis arsitektur kode)
```

---

## 4. Cara Menjalankan Aplikasi Secara Lokal (Local Setup)

Untuk menjalankan dan mengembangkan aplikasi ini di komputer lokal Anda, ikuti langkah berikut:

1.  **Klon Repositori**:
    ```bash
    git clone https://github.com/Fadh29/speedhome-price-intelligence-jendela360.git
    cd speedhome-price-intelligence-jendela360
    ```
2.  **Instal Pustaka Dependensi**:
    Pastikan Anda telah menginstal Python 3.9 atau versi di atasnya. Jalankan perintah:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Jalankan Server Streamlit**:
    ```bash
    streamlit run app.py
    ```
    Aplikasi akan terbuka secara otomatis di browser Anda di alamat lokal `http://localhost:8501`.

---

## 5. Penjelasan Kode Baris demi Baris & Logika Kerja

### A. scraper.py (Modul Web Scraper)

Modul ini bertanggung jawab mengumpulkan data HTML dari SPEEDHOME dan mengekstrak data JSON terstruktur.

#### 1. Fungsi `slugify` (Baris 7 - 18)
*   **Baris 11**: `.lower().strip()` mengubah seluruh teks input menjadi huruf kecil dan membuang spasi di awal/akhir teks.
*   **Baris 13**: `re.sub(r'[^\w\s-]', '', text)` menghapus semua karakter yang bukan huruf, angka, spasi, atau tanda hubung.
*   **Baris 15**: `re.sub(r'[\s_]+', '-', text)` mengubah spasi dan garis bawah menjadi satu buah tanda hubung.
*   **Baris 17**: `re.sub(r'-+', '-', text)` mengubah beberapa tanda hubung beruntun menjadi satu tanda hubung tunggal.
*   **Logika**: Memastikan nama area masukan pengguna aman untuk disematkan sebagai slug URL web pencarian.

#### 2. Fungsi `extract_slug_from_url` (Baris 20 - 40)
*   **Baris 26**: `.strip().rstrip('/')` membersihkan spasi dan garis miring di akhir string URL.
*   **Baris 29**: Regex mencocokkan pola alamat URL sewa SPEEDHOME (`/rent/`, `/sewa/`, `/zh/rent/`, `/my/sewa/`) untuk mengambil bagian slug nama wilayah.
*   **Baris 37**: Mencari query string pagination `?page=X` atau `&page=X` untuk menentukan halaman mulai scraping.
*   **Logika**: Mengurai tautan web jika pengguna memilih metode input URL langsung di UI.

#### 3. Fungsi `normalize_furniture` (Baris 42 - 51)
*   **Baris 43-44**: Jika nilai furnitur kosong/null, kembalikan `"Unfurnished"`.
*   **Baris 45-50**: Melakukan pencocokan substring bersandar pada huruf kapital (`.upper()`). Jika mengandung kata `"FULL"`, dinormalisasi ke `"Fully Furnished"`. Jika mengandung kata `"PART"`, ke `"Partially Furnished"`. Selain itu, ke `"Unfurnished"`.
*   **Logika**: Menjamin data status kelengkapan perabot seragam untuk visualisasi grafik.

#### 4. Fungsi `normalize_room_type` (Baris 53 - 60)
*   **Baris 54-55**: Jika tipe aslinya berupa kata `"STUDIO"` atau `"ROOM"`, maka kembalikan kata tersebut dengan huruf kapital di awal (`.capitalize()`).
*   **Baris 56-57**: Jika jumlah kasur bernilai kosong/null, kembalikan `"N/A"`.
*   **Baris 58-59**: Jika jumlah kasur bernilai `0`, maka itu dikelompokkan sebagai tipe `"Studio"`.
*   **Baris 60**: Jika kasur lebih dari 0, kembalikan format jumlah kamar seperti `"1 BR"`, `"2 BR"`, dst.
*   **Logika**: Menerjemahkan data tipe kamar dari platform eksternal ke format standar industri properti.

#### 5. Fungsi `fetch_speedhome_page_source` (Baris 62 - 113)
*   **Baris 70-77 (Lapis 1)**: Mengimpor `curl_cffi` secara lokal. Mengirimkan HTTP GET request dengan parameter `impersonate="chrome"`. Jika sukses (status 200) dan panjang konten > 1000 byte, kembalikan HTML mentah.
*   **Baris 79-98 (Lapis 2)**: Jika Lapis 1 gagal, gunakan `subprocess.run` untuk memanggil perintah sistem `curl` bawaan OS. Mengatur parameter User-Agent browser Chrome modern (`-A`) dan flag `--compressed`. Jika sukses (returncode 0), kembalikan output stdout.
*   **Baris 100-111 (Lapis 3)**: Sebagai fallback darurat terakhir, gunakan library `requests` Python biasa dengan menyematkan header dasar.
*   **Logika**: Menghindari proteksi web scraper dari Cloudflare agar aplikasi tidak mengalami pemblokiran IP/bot.

#### 6. Fungsi `scrape_speedhome_listings` (Baris 115 - 230)
*   **Baris 121-125**: Menentukan apakah `search_input` berupa URL penuh atau sekadar nama slug teks biasa.
*   **Baris 135**: Memulai perulangan tanpa batas (`while True`) untuk mengambil halaman web satu per satu.
*   **Baris 140-142**: Menerapkan jeda `time.sleep(delay)` (default 1 detik) sebelum mengambil halaman baru jika halaman saat ini > halaman mulai, untuk mematuhi etika crawler dan menghindari overload server.
*   **Baris 153**: Mem-parsing HTML menggunakan BeautifulSoup dengan parser HTML bawaan (`html.parser`).
*   **Baris 154**: Mencari tag `<script id="__NEXT_DATA__" type="application/json">` tempat Next.js menaruh data server-side rendered.
*   **Baris 162**: Membaca teks string di dalam tag script tersebut menggunakan parser `json.loads`.
*   **Baris 163-171**: Mengambil data terstruktur properti di bawah navigasi objek `props -> pageProps -> propertyList -> content`.
*   **Baris 177-204**: Melakukan iterasi di setiap item listing properti, memanggil fungsi normalisasi, mengalkulasi sewa tahunan (`price_monthly * 12`), menyusun tautan langsung `/details/{slug}`, dan menyimpannya dalam dictionary.
*   **Baris 207-222**: Memeriksa keberadaan tautan halaman selanjutnya (`nextUrl`). Jika ada, ekstrak angka halaman berikutnya menggunakan regex. Jika tidak ada, hentikan perulangan pencarian.
*   **Logika**: Mengambil semua data properti di wilayah tersebut secara efisien halaman demi halaman.

---

### B. app.py (Modul Web Aplikasi Streamlit)

Berkas utama penampil antarmuka dasbor investasi.

#### 1. Inisialisasi & Gaya CSS (Baris 14 - 241)
*   **Baris 14-25**: Menyetel konfigurasi layout lebar aplikasi (`layout="wide"`) dan judul dasbor.
*   **Baris 27-241**: Menyisipkan kode CSS kustom ke dalam container HTML web Streamlit (`st.markdown(..., unsafe_allow_html=True)`). Gaya ini memberikan tampilan kartu KPI melayang, efek transparansi, warna dinamis, dan scroll horizontal responsif pada menu tab agar optimal saat dibuka melalui ponsel.

#### 2. Fungsi `load_locations` (Baris 242 - 265)
*   **Baris 243-259**: Mencoba membaca file database autocomplete `locations.json` secara lokal menggunakan encoding UTF-8.
*   **Baris 260-265**: Jika file tidak ditemukan, ia akan memuat array hardcoded statis berisi 10 wilayah populer di Malaysia sebagai fallback agar aplikasi tetap dapat berjalan.

#### 3. Panel Masukan Pengguna (Baris 267 - 312)
*   **Baris 272-277**: Radio button horizontal untuk memilih mode `Single Area Analysis` atau `Compare Areas`.
*   **Baris 287-291**: Opsi pemilihan metode pencarian wilayah (Autocomplete vs Input URL).
*   **Baris 293-300**: Jika metode Autocomplete dipilih, merender selectbox dropdown berisi nama daerah yang terindeks dan mencari padanan nama slug-nya dari map lokasi.
*   **Baris 301-305**: Jika metode Input URL dipilih, merender input teks dengan `placeholder` abu-abu.
*   **Baris 307-311**: Merender tombol submit untuk memicu penarikan data scraper.

#### 4. Utilitas Perhitungan Matematika (Baris 313 - 338)
*   **Baris 314-319 (`get_mode`)**: Memfilter data kosong (`.dropna()`), kemudian memanggil fungsi `.mode()` milik Pandas untuk mencari nilai sewa yang paling sering muncul di data.
*   **Baris 321-328 (`get_fair_price`)**: Formula berbobot penentu harga wajar pasar:
    $$\text{Harga Wajar} = (\text{Median Harga} \times 0.7) + (\text{Rata-rata Harga} \times 0.3)$$
    *Logika*: Melindungi harga pasaran agar tidak rusak akibat data pencilan sewa penthouse mewah (yang merusak nilai rata-rata) tapi tetap menyerap bias tren premium wilayah tersebut.

#### 5. Skor Perbandingan `compute_property_value_scores` (Baris 340 - 379)
*   Fungsi inti penentu peringkat investasi (Overall Winner) antara dua wilayah berbeda berdasarkan 4 variabel:
    *   **Baris 341-347 (Yield - Bobot 40%)**: Normalisasi performa yield kotor kearah nilai tertinggi.
    *   **Baris 349-357 (Sewa/sqft - Bobot 25%)**: Mengukur efisiensi tarif per sqft. Nilai yang terkecil dianggap terbaik (efisiensi tertinggi), lalu dinormalisasi secara terbalik.
    *   **Baris 359-365 (Volume - Bobot 20%)**: Normalisasi ketersediaan jumlah listing aktif (menunjukkan likuiditas pasar sewa).
    *   **Baris 367-373 (Ukuran - Bobot 15%)**: Normalisasi rata-rata luas bangunan unit properti.
    *   **Baris 375-376**: Mengalikan masing-masing skor normalisasi (skala 100) dengan persentase bobotnya lalu menjumlahkannya menjadi skor akhir terbulat.

#### 6. Klasifikasi Kompetisi `classify_competitiveness` (Baris 380 - 393)
*   Mengukur deviasi persentase harga aktual terhadap Harga Wajar.
*   Mengembalikan tag warna CSS kustom untuk menunjukkan kondisi properti (`Undervalued`, `Slightly Undervalued`, `Fairly Priced`, `Slightly Overpriced`, atau `Overpriced`).

#### 7. Eksekusi Scraping & Agregasi Data (Baris 436 - 525)
*   **Baris 437-448**: Memicu spinner pemuatan data sewa. Memanggil modul `scrape_speedhome_listings(target_input)` dan menyimpan hasilnya di dalam Session State Streamlit agar data tidak hilang ketika UI diinteraksi kembali oleh pengguna.
*   **Baris 456-465**: Konversi list listing menjadi Pandas `DataFrame`, membersihkan tipe data kolom harga bulanan, tahunan, dan ukuran bangunan dari format string menjadi numeric.
*   **Baris 475-520**: Menampilkan KPI cards di atas layar.

#### 8. Layout Tab Interaktif (Baris 527 - 854)
*   **Baris 536-601 (Tab 📋 Harga)**: Mengelompokkan statistik menggunakan `.groupby("room_type")`. Menghitung agregat, membuat tombol download ringkasan Excel di atas tabel, disusul oleh render tabel dataframe interaktif.
*   **Baris 603-740 (Tab 🔍 Lengkap)**: Menyajikan filter tipe kamar dan furnitur. Membuat berkas Excel multi-sheet (Sheet 1: Listing lengkap, Sheet 2: Agregasi summary) menggunakan `pd.ExcelWriter` di dalam memori, membuat tombol download Excel, dan merender dataframe detail.
*   **Baris 741-805 (Tab 💰 ROI)**: Merender masukan harga beli properti dan persentase biaya operasional tahunan. Melakukan kalkulasi proyeksi yield sewa tahunan:
    $$\text{Gross ROI} = \frac{\text{Sewa Bulanan} \times 12}{\text{Harga Beli}} \times 100$$
    $$\text{Net ROI} = \frac{\text{Sewa Bulanan} \times 12 \times (1 - \text{Beban Operasional})}{\text{Harga Beli}} \times 100$$
*   **Baris 806-855 (Tab 💡 Insights)**: Melakukan analisis komparatif sewa unit Fully Furnished vs Unfurnished untuk mengukur nilai tambah perabotan (*furniture premium*).

#### 9. Implementasi Mode Compare Areas (Baris 856 - 1300)
*   **Baris 872-908**: Merender kolom masukan berdampingan untuk Area A & Area B. Masing-masing kolom memiliki radio button pemilihan metode autocomplete vs URL, kolom teks masukan URL dengan `placeholder`, dan input numerik harga beli properti.
*   **Baris 910-931**: Memicu proses penarikan data scraping ganda untuk Area A dan Area B secara paralel saat tombol diklik.
*   **Baris 941-995**: Melakukan pembersihan data statistik dasar untuk kedua dataframe.
*   **Baris 996-1017**: Menghitung rata-rata sewa, ukuran, sewa per sqft, volume listing, dan tingkat rental yield kotor untuk kedua wilayah.
*   **Baris 1019-1033**: Memanggil fungsi `compute_property_value_scores` untuk mendapatkan skor akhir Area A & B.
*   **Baris 1035-1080**: Menampilkan banner visual pengumuman wilayah pemenang beserta poin keunggulan utamanya secara dinamis.
*   **Baris 1133-1180**: Merender tabel perbandingan KPI bersisian dengan sel tabel pemenang yang disorot warna hijau khusus (`class="winner-cell"`).
*   **Baris 1182-1265**: Merender grafik perbandingan kemajuan (*progress bar comparison*) untuk mempermudah pencernaan data secara visual.

---

### C. build_locations.py (Script Utilitas Pemelihara Wilayah)

File utilitas mandiri untuk mengompilasi data referensi autocomplete secara berkala.

#### 1. Fungsi `clean_slug_to_display_name` (Baris 19 - 46)
*   **Baris 25-28**: Memeriksa apakah slug diakhiri oleh nama wilayah bagian dari Malaysia (seperti `-kuala-lumpur`, `-selangor`, dll.).
*   **Baris 30-36**: Memisahkan kata depan slug dengan wilayah induknya, mengubahnya menjadi huruf kapital di awal kata (`.capitalize()`), dan menggabungkannya kembali menggunakan koma. Contoh: `mont-kiara-kuala-lumpur` -> `"Mont Kiara, Kuala Lumpur"`.
*   **Baris 38-39**: Mengoreksi kapitalisasi singkatan transportasi umum seperti `Lrt` -> `LRT` dan `Mrt` -> `MRT`.

#### 2. Fungsi `build_locations_json` (Baris 48 - 122)
*   **Baris 50-53**: Mendefinisikan URL sitemap XML resmi SPEEDHOME yang berisi seluruh indeks URL wilayah mereka.
*   **Baris 78**: Mengunduh konten XML menggunakan perintah CLI `curl.exe` secara aman via subproses Python.
*   **Baris 83-94**: Mem-parsing XML sitemap menggunakan parser pohon elemen `xml.etree.ElementTree`. Melakukan pencarian tag lokasi `<loc>` di bawah namespace skema sitemap standar.
*   **Baris 100-104**: Mengambil slug URL, memanggil fungsi pembersih display name cantik, dan mengumpulkannya dalam dictionary unik untuk membuang wilayah duplikat.
*   **Baris 109-112**: Menggabungkan data hasil sitemap dengan list wilayah fallback default untuk menjamin area penting selalu tersedia.
*   **Baris 115**: Mengurutkan seluruh objek wilayah secara alfabetis bersandarkan nama wilayah (`"name"`).
*   **Baris 118-120**: Menulis data akhir tersebut ke berkas `locations.json` menggunakan format JSON ter-indentasi rapi.
