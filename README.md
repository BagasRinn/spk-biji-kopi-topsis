# Supply Chain & SPK TOPSIS - Coffee Shop

Sistem Informasi Manajemen Supply Chain Kedai Kopi terintegrasi dengan Sistem Penunjang Keputusan (SPK) penentuan Supplier Biji Kopi terbaik menggunakan metode TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).

Proyek ini dibangun sebagai implementasi praktis dari perancangan Data Flow Diagram (DFD) Level 0 dan Level 1 pada domain manajemen logistik F&B.

---

## Fitur Utama (MVP)

1. **Master Data Read-Only**: Visualisasi kriteria penilaian (Cost/Benefit) beserta pembobotan desimal, dan daftar alternatif supplier mitra.
2. **Matriks Penawaran Terpusat**: Representasi *Strictly Normalized* (3NF) dari data penawaran harga, kualitas (cupping score), waktu pengiriman, dan varian dari masing-masing roastery.
3. **TOPSIS Decision Engine**: Modul kalkulasi matematis murni (tanpa dependensi komputasi berat) yang memproses:
   - Pembentukan Matriks Keputusan ($X$)
   - Normalisasi Matriks ($R$)
   - Normalisasi Terbobot ($Y$)
   - Penentuan Solusi Ideal Positif ($A^+$) dan Negatif ($A^-$)
   - Perhitungan Jarak Euclidean ($D^+$ / $D^-$) dan Nilai Preferensi ($V_i$)
4. **Auto-Healing Database**: Sistem dilengkapi *startup-hook* yang otomatis menciptakan dan mengisi skema database SQLite saat pertama kali dijalankan.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **Database**: SQLite3 (Native `sqlite3` driver)
- **Frontend**: HTML5, Jinja2 Templating, Bootstrap 5 (CDN)
- **Architecture**: Monolithic, PRG (*Post-Redirect-Get*) Pattern

---

## Cara Instalasi & Menjalankan (Lokal)

1. **Kloning Repositori**
   `git clone https://github.com/BagasRinn/spk-biji-kopi-topsis.git`
   `cd spk-kopi-topsis`

2. **Ciptakan & Aktifkan Virtual Environment**
   * **Windows**: `python -m venv venv && venv\Scripts\activate`
   * **Linux / Mac**: `python3 -m venv venv && source venv/bin/activate`

3. **Instalasi Dependensi**
   `pip install -r requirements.txt`

4. **Jalankan Aplikasi**
   `python app.py`
   *(Catatan: Jika file `database.db` belum tersedia di dalam folder, sistem akan melakukan auto-initialization dan seeding data secara otomatis).*

5. **Akses Peramban (Browser)**
   Buka alamat: `http://localhost:5000`