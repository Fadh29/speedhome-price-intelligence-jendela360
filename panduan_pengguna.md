# Panduan Pengguna: SPEEDHOME Price Intelligence

Selamat datang di berkas Panduan Pengguna **SPEEDHOME Price Intelligence**. Dokumen ini dirancang khusus agar investor, agen properti, maupun penyewa dapat memahami cara kerja aplikasi, asal-usul data, metrik intelijen pasar yang disajikan, serta model perhitungan matematis di balik fitur analisis investasi kami.

---

## 1. Tentang Aplikasi
**SPEEDHOME Price Intelligence** adalah platform analitik cerdas yang dirancang untuk mengumpulkan, memproses, dan memvisualisasikan data sewa properti secara *real-time* dari pasar Malaysia. 

Aplikasi ini membantu pengguna melakukan riset pasar sewa secara instan untuk:
*   Menganalisis sebaran harga sewa bulanan dan tahunan di wilayah tertentu.
*   Menghitung potensi tingkat pengembalian investasi (ROI / Rental Yield) secara kotor maupun bersih.
*   Membandingkan nilai investasi (value for money) antara dua area/apartemen yang berbeda secara berdampingan dengan algoritma pembobotan otomatis.

---

## 2. Sumber Data
Seluruh data properti yang ditampilkan pada aplikasi ini didapatkan langsung melalui proses *real-time web scraping* dari situs **[SPEEDHOME Malaysia](https://speedhome.com)**.

### Proses Pengambilan Data & Teknologi
1.  **Impersonasi TLS (curl_cffi)**: Untuk melewati sistem proteksi Cloudflare yang ketat tanpa terblokir, aplikasi menggunakan pustaka `curl_cffi` yang meniru sidik jari TLS (TLS fingerprint) dari browser Google Chrome asli.
2.  **Fallback Mekanis**: Jika pustaka tersebut mengalami kendala, sistem akan otomatis beralih menggunakan pemanggilan sistem `curl` bawaan OS, lalu menggunakan pustaka `requests` Python dengan User-Agent browser modern sebagai benteng pertahanan terakhir.
3.  **Ekstraksi Atribut Properti**: Dari setiap halaman pencarian area (misal: `https://speedhome.com/rent/mont-kiara`), aplikasi mengekstrak:
    *   **Judul Listing**: Nama unit atau deskripsi promosi.
    *   **Nama Properti/Kondominium**: Lokasi spesifik apartemen.
    *   **Tipe Unit**: Diterjemahkan menjadi kategori standar (Studio, Room, atau jumlah kamar seperti 1 BR, 2 BR, 3 BR, dll.).
    *   **Harga Sewa Bulanan (Monthly Rent)**: Angka sewa dalam mata uang Ringgit Malaysia (RM).
    *   **Harga Kontrak Tahunan (Yearly Rent)**: Estimasi akumulasi kontrak sewa tahunan.
    *   **Ukuran Bangunan (sqft)**: Luas unit dalam satuan kaki persegi (square feet).
    *   **Status Furnitur (Furnishing Status)**: Dikelompokkan menjadi *Fully Furnished*, *Partially Furnished*, atau *Unfurnished*.
    *   **Tautan Langsung (Direct URL)**: Link aktif menuju listing spesifik di SPEEDHOME.

---

## 3. Fitur Utama & Penjelasan Perhitungan Metrik

Aplikasi ini dibagi menjadi dua mode analisis utama: **Single Area Analysis (Analisis Satu Wilayah)** dan **Compare Areas (Perbandingan Dua Wilayah)**.

---

### A. Single Area Analysis (Analisis Satu Wilayah)

Mode ini menyajikan tinjauan mendalam untuk satu area/apartemen tertentu melalui 5 tab fungsional.

#### 1. Panel Masukan & Metode Pencarian
Pengguna diberikan kebebasan menggunakan salah satu dari dua metode pencarian:
*   **Pencarian Autocomplete**: Memilih nama area populer dari dropdown yang disediakan (misal: *Mont Kiara*, *Bangsar*, *Petaling Jaya*).
*   **Input URL SPEEDHOME**: Memasukkan URL pencarian SPEEDHOME secara langsung.
    *   *Desain UX*: Kolom ini menggunakan `placeholder` bersih. Jika dibiarkan kosong lalu menekan tombol pencarian, sistem akan otomatis melakukan pencarian default pada area *Mont Kiara*.

#### 2. Ringkasan KPI (KPI Cards)
Di bagian atas hasil pencarian, terdapat 5 kartu indikator utama:
*   **Total Listings**: Jumlah unit aktif yang ditemukan dan di-scrape di wilayah tersebut.
*   **Rata-rata Sewa**: Rata-rata aritmatika harga sewa bulanan.
*   **Median Sewa**: Nilai tengah dari seluruh sebaran harga sewa bulanan.
*   **Harga Wajar (Fair Price)**: Estimasi nilai sewa paling representatif di pasar saat ini (Penjelasan rumus di bawah).
*   **Rata-rata Ukuran**: Luas bangunan rata-rata dalam satuan *sqft*.

---

### TAB 1: 📋 Harga (Tabel Ringkasan Segmentasi)
Menampilkan statistik harga sewa bulanan yang dikelompokkan secara spesifik berdasarkan **Tipe Unit** (seperti Studio, 1 BR, 2 BR, dst.) untuk melihat segmentasi pasar.

#### Penjelasan Metrik & Rumus Perhitungan:
1.  **Rata-rata (RM)**: Rerata nilai sewa dari semua unit dalam segmen tersebut.
2.  **Median (RM)**: Nilai sewa yang membagi segmen tepat menjadi dua bagian sama besar. Metrik ini sangat berguna karena tidak terpengaruh oleh pencilan (*outliers*) seperti unit yang terlampau mahal atau terlampau murah.
3.  **Modus (RM)**: Harga sewa yang paling sering muncul/ditawarkan oleh landlord di pasar pada segmen tersebut.
4.  **Harga Wajar (Fair Price)**:
    Untuk menghindari bias harga rata-rata akibat unit mewah/penthouse (outliers atas) namun tetap menyerap tren pasar yang realistis, kami merumuskan indeks **Harga Wajar** dengan rumus:
    
    ```
    Harga Wajar (Fair Price) = (Median Price * 0.7) + (Mean Price * 0.3)
    [Hasil dibulatkan ke bilangan bulat terdekat]
    ```
    
    *Mengapa bobot 70:30?* Median mewakili 70% stabilitas pasar kelas menengah, sedangkan Mean mewakili 30% sensitivitas terhadap variasi harga unit premium di wilayah tersebut.
5.  **Tingkat Kompetisi Harga (Price Competitiveness Status)**:
    Status kewajaran harga sewa aktual dibandingkan dengan Harga Wajar dihitung menggunakan persentase deviasi:
    
    ```
    Persentase Deviasi = ((Rata-rata Harga Aktual - Harga Wajar) / Harga Wajar) * 100
    ```
    
    *   **🟢 Undervalued**: Jika Deviasi < -5% (Sangat murah, peluang investasi/sewa bagus).
    *   **🟢 Slightly Undervalued**: Jika Deviasi antara -5% hingga < 0%.
    *   **🟡 Fairly Priced**: Jika Deviasi = 0% (Harga stabil/normal sesuai pasar).
    *   **🔴 Slightly Overpriced**: Jika Deviasi antara > 0% hingga 5%.
    *   **🔴 Overpriced**: Jika Deviasi > 5% (Harga cenderung kemahalan).

---

### TAB 2: 🔍 Lengkap (Tabel Daftar Unit & Ekspor Excel)
Menampilkan tabel interaktif seluruh listing yang ditemukan di area tersebut.
*   **Fungsi Filter**: Pengguna dapat memfilter isi tabel secara instan berdasarkan *Tipe Unit* dan *Status Furnitur*.
*   **Tombol Ekspor (Download Data Sewa)**: Memungkinkan pengguna mengunduh berkas Excel dengan penamaan sistematis: `SPEEDHOME_{Nama_Area}_{Tanggal_Scraping}.xlsx`.
    *   *Isi Berkas Excel*: Memiliki 2 sheet terpisah: sheet pertama berisi data listing mentah lengkap, dan sheet kedua berisi tabel ringkasan agregat harga sewa.

---

### TAB 3: 📈 Tren (Visualisasi Data Visual)
Mengubah angka-angka mentah menjadi grafik analitik interaktif menggunakan pustaka Plotly:
*   **Distribusi Sewa per Tipe Unit (Box Plot)**: Menampilkan rentang harga minimum, kuartil bawah, median, kuartil atas, maksimum, serta data outlier untuk setiap tipe unit.
*   **Korelasi Ukuran vs Sewa (Scatter Plot)**: Melihat apakah unit yang lebih luas berkorelasi linier dengan harga sewa yang lebih tinggi.
*   **Rata-rata Harga berdasarkan Status Furnitur (Bar Chart)**: Menunjukkan perbedaan harga rata-rata antara unit *Fully*, *Partially*, dan *Unfurnished*.

---

### TAB 4: 💰 ROI (Kalkulator Yield Investasi)
Membantu investor memproyeksikan persentase tingkat pengembalian investasi tahunan (*Rental Yield*) jika mereka membeli unit properti di area tersebut.

#### Parameter Input:
1.  **Harga Pembelian Properti (RM)**: Estimasi modal pembelian properti (Default: RM 500,000).
2.  **Target Sewa Bulanan (RM)**: Diisi secara otomatis dengan nilai median harga sewa tipe unit pilihan, namun dapat disesuaikan manual oleh pengguna.
3.  **Persentase Biaya Operasional Tahunan (%)**: Beban tahunan seperti pajak bumi bangunan, biaya pemeliharaan bulanan kondominium (*maintenance fee*), asuransi, dan dana perbaikan (Default: 10%).

#### Rumus Perhitungan ROI:
1.  **Gross Rental Yield (Yield Kotor)**:
    Persentase pendapatan kotor tahunan sebelum dipotong pengeluaran apa pun.
    
    ```
    Gross Yield (%) = (Target Sewa Bulanan * 12 / Harga Pembelian Properti) * 100
    ```
    
2.  **Net Rental Yield (Yield Bersih)**:
    Persentase pendapatan bersih tahunan setelah dikurangi biaya operasional yang diproyeksikan.
    
    ```
    Net Yield (%) = (Target Sewa Bulanan * 12 * (1 - (Persentase Biaya Operasional / 100)) / Harga Pembelian Properti) * 100
    ```

---

### TAB 5: 💡 Insights (Intelijen Otomatis Berbasis AI/Aturan)
Memberikan kesimpulan ringkas mengenai kondisi pasar properti lokal tanpa mengharuskan pengguna membaca grafik:
*   **Premium Furnitur**: Menghitung persentase kenaikan harga dari opsi unit berperabot lengkap dibandingkan kosong:
    
    ```
    Premium Furnitur (%) = ((Sewa Rata-rata Fully Furnished - Sewa Rata-rata Unfurnished) / Sewa Rata-rata Unfurnished) * 100
    ```
    
*   **Dominasi Pasar**: Menemukan tipe unit apa yang menguasai persentase listing terbanyak di area tersebut.
*   **Segmentasi Ekstrim**: Otomatis mendeteksi tipe unit dengan rata-rata harga sewa paling terjangkau (termurah) dan tipe unit paling premium (termahal).

---

---

### B. Compare Areas Mode (Perbandingan Dua Wilayah)

Mode ini memfasilitasi perbandingan *head-to-head* antara **Area A** dan **Area B** untuk menentukan wilayah mana yang memiliki nilai investasi paling optimal.

#### 1. Input Fleksibel Berdampingan
Pengguna dapat memilih metode input untuk masing-masing area secara mandiri (baik autocomplete maupun input URL langsung) serta menginput nilai estimasi harga beli properti masing-masing wilayah secara terpisah.

#### 2. Kartu Pemenang Utama (Better Value Area Winner)
Menampilkan nama area pemenang berdasarkan nilai **Overall Value Score** tertinggi yang dihitung menggunakan algoritma pembobotan multi-metrik.

#### 3. Penjelasan Algoritma "Overall Value Score" (Skala 1 - 100)
Skor dihitung dengan menormalisasi empat sub-metrik utama terhadap nilai tertinggi/terendah di antara kedua area tersebut, kemudian dikalikan dengan bobot kepentingan investasi masing-masing metrik:

```
Overall Score = (0.40 * Skor Yield) + (0.25 * Skor Efisiensi Ukuran) + (0.20 * Skor Volume) + (0.15 * Skor Ukuran)
[Hasil dibulatkan ke bilangan bulat terdekat]
```

##### Detail Normalisasi Sub-Metrik:
1.  **Skor Yield (Bobot 40%)** (Lebih Tinggi Lebih Baik):
    Mengukur persentase potensi rental yield tahunan kotor.
    
    ```
    Jika max(Yield A, Yield B) > 0:
    Skor Yield = (Yield Area / max(Yield A, Yield B)) * 100
    Jika tidak, Skor Yield = 0
    ```
    
2.  **Skor Efisiensi Ukuran (Bobot 25%)** (Lebih Rendah Lebih Baik):
    Mengukur efisiensi harga sewa per kaki persegi (RM/sqft). Wilayah yang biaya sewa per sqft-nya lebih murah dinilai memiliki efisiensi nilai lebih tinggi.
    
    ```
    Jika Rent_per_Sqft A > 0 dan Rent_per_Sqft B > 0:
    Skor Efisiensi Ukuran = (min(Rent_per_Sqft A, Rent_per_Sqft B) / Rent_per_Sqft Area) * 100
    Jika tidak, Skor Efisiensi Ukuran = 0
    ```
    
3.  **Skor Volume (Bobot 20%)** (Lebih Tinggi Lebih Baik):
    Mengukur jumlah pasokan/ketersediaan pilihan unit aktif di pasar. Volume listing yang tinggi menunjukkan pasar yang likuid dan kaya opsi bagi penyewa.
    
    ```
    Jika max(Volume A, Volume B) > 0:
    Skor Volume = (Volume Area / max(Volume A, Volume B)) * 100
    Jika tidak, Skor Volume = 0
    ```
    
4.  **Skor Ukuran (Bobot 15%)** (Lebih Tinggi Lebih Baik):
    Mengukur luas bangunan rata-rata unit yang ditawarkan. Luas area rata-rata yang lebih besar bernilai lebih baik.
    
    ```
    Jika max(Ukuran A, Ukuran B) > 0:
    Skor Ukuran = (Ukuran Area / max(Ukuran A, Ukuran B)) * 100
    Jika tidak, Skor Ukuran = 0
    ```

Area yang mengumpulkan total bobot nilai tertinggi (skor paling mendekati 100) akan dinobatkan sebagai **Overall Winner** dengan ringkasan poin-poin keunggulan spesifik yang langsung ditampilkan pada layar.
