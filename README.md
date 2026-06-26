# Supply Chain & SPK TOPSIS - Coffee Shop

Sistem Informasi Manajemen Supply Chain Kedai Kopi terintegrasi dengan Sistem Penunjang Keputusan (SPK) penentuan Supplier Biji Kopi terbaik menggunakan metode TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).

Proyek ini dibangun sebagai implementasi praktis dari perancangan Data Flow Diagram (DFD) Level 0 dan Level 1 pada domain manajemen logistik F&B.

---

## Fitur Utama

* **Enterprise Auth & RBAC**: Sistem otentikasi terotentikasi berlapis yang memisahkan wewenang kerja antara Staf Logistik dengan Manajer Kedai (*Separation of Duties*).
* **Defense in Depth Security**: Pengamanan ganda menggunakan visualisasi bersyarat pada antarmuka (*Frontend*) dan pemblokiran rute paksa pada tingkat pengontrol (*Backend Route Guard*).
* **Master Data Read-Only**: Visualisasi kriteria penilaian (*Cost/Benefit*) beserta pembobotan desimal, dan daftar alternatif supplier mitra.
* **Matriks Penawaran Terpusat**: Representasi *Strictly Normalized* (3NF) dari data penawaran harga, kualitas (*cupping score*), waktu pengiriman, dan varian biji kopi.
* **TOPSIS Decision Engine**: Modul kalkulasi matematis murni yang memproses pembentukan matriks keputusan hingga nilai preferensi akhir (V).
* **Auto-Healing Database**: Sistem dilengkapi *startup-hook* yang otomatis menciptakan dan mengisi skema database SQLite beserta akun pengguna saat pertama kali dijalankan.

---

## Kredensial Pengujian (Demo Accounts)

Sistem telah di-seed dengan 2 hak akses berdaulat:

| Role (Jabatan) | Username | Password | Wewenang Akses |
| :--- | :---: | :---: | :--- |
| **Admin Logistik** | `admin` | `admin123` | Mengelola Master Data & melihat Matriks Penawaran |
| **Manajer Kedai** | `manajer` | `manajer123` | Menjalankan enjin SPK TOPSIS & melegitimasi PO |

*(Catatan Security: Seluruh sandi di atas disimpan di dalam database dalam format terenkripsi menggunakan algoritma `PBKDF2 SHA-256`).*

---

## Tech Stack

* **Backend**: Python 3.10+, Flask
* **Database**: SQLite3 (Native `sqlite3` driver)
* **Security**: Werkzeug Security (Password Hashing), Flask HTTP Session
* **Frontend**: HTML5, Jinja2 Templating, Bootstrap 5 (CDN)
* **Arsitektur**: Monolithic, PRG (*Post-Redirect-Get*) Pattern

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