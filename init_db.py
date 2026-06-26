import sqlite3
import logging
from werkzeug.security import generate_password_hash

# Konfigurasi basic logging untuk standard output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def init_database():
    db_path = 'database.db'

    try:
        # Membuka koneksi ke database
        conn = sqlite3.connect(db_path)

        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        logging.info("Berhasil terhubung ke database SQLite.")

        # 1. DROP TABLES
        tables_to_drop = [
            "users",
            "D4_hasil_kalkulasi",
            "D3_penawaran",
            "D2_supplier",
            "D1_kriteria"
        ]
        for table in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        logging.info("Tabel lama berhasil di-drop (jika ada).")

        # 2. CREATE TABLES
        # Tabel Users
        cursor.execute('''
            CREATE TABLE users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Admin Logistik', 'Manajer Kedai')),
                nama_lengkap TEXT NOT NULL
            );
        ''')
        
        # D1: Tabel Kriteria
        cursor.execute('''
            CREATE TABLE D1_kriteria (
                id_kriteria TEXT PRIMARY KEY,
                nama_kriteria TEXT NOT NULL,
                sifat TEXT NOT NULL CHECK(sifat IN ('Cost', 'Benefit')),
                bobot_desimal REAL NOT NULL
            );
        ''')

        # D2: Tabel Supplier
        cursor.execute('''
            CREATE TABLE D2_supplier (
                id_supplier TEXT PRIMARY KEY,
                nama_supplier TEXT NOT NULL
            );
        ''')

        # D3: Tabel Penawaran (Strictly Normalized)
        cursor.execute('''
            CREATE TABLE D3_penawaran (
                id_penawaran INTEGER PRIMARY KEY AUTOINCREMENT,
                id_supplier TEXT NOT NULL,
                id_kriteria TEXT NOT NULL,
                nilai REAL NOT NULL,
                FOREIGN KEY (id_supplier) REFERENCES D2_supplier (id_supplier) ON DELETE CASCADE,
                FOREIGN KEY (id_kriteria) REFERENCES D1_kriteria (id_kriteria) ON DELETE CASCADE
            );
        ''')

        # D4: Hasil Kalkulasi
        cursor.execute('''
            CREATE TABLE D4_hasil_kalkulasi (
                id_kalkulasi INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_batch TEXT NOT NULL,
                id_supplier TEXT NOT NULL,
                skor_akhir REAL NOT NULL,
                keputusan TEXT NOT NULL,
                tanggal_proses DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_supplier) REFERENCES D2_supplier (id_supplier) ON DELETE CASCADE
            );
        ''')
        logging.info("Struktur tabel (D1, D2, D3, D4) berhasil dibuat.")

        # 3. SEEDING DATA
        data_users = [
            ('admin', generate_password_hash('admin123'), 'Admin Logistik', 'Administrator'),
            ('manager', generate_password_hash('manager123'), 'Manajer Kedai', 'Manajer Kedai')
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", data_users)
        
        # D1: Kriteria
        data_kriteria = [
            ('C1', 'Harga per Kg', 'Cost', 0.30),
            ('C2', 'Kualitas Biji (Cupping Score)', 'Benefit', 0.30),
            ('C3', 'Waktu Pengiriman', 'Cost', 0.20),
            ('C4', 'Kelengkapan Varian', 'Benefit', 0.20)
        ]
        cursor.executemany(
            "INSERT INTO D1_kriteria (id_kriteria, nama_kriteria, sifat, bobot_desimal) VALUES (?, ?, ?, ?)",
            data_kriteria
        )

        # D2: Supplier
        data_supplier = [
            ('A1', 'Banua Roastery'),
            ('A2', 'Borneo Beans'),
            ('A3', 'Kopi Nusantara')
        ]
        cursor.executemany(
            "INSERT INTO D2_supplier (id_supplier, nama_supplier) VALUES (?, ?)",
            data_supplier
        )

        # D3: Penawaran (Format Long-Table)
        data_penawaran = [
            # Entri Penawaran Banua Roastery (A1)
            ('A1', 'C1', 150.0), ('A1', 'C2', 82.0), ('A1', 'C3', 2.0), ('A1', 'C4', 5.0),
            # Entri Penawaran Borneo Beans (A2)
            ('A2', 'C1', 180.0), ('A2', 'C2', 85.0), ('A2', 'C3', 1.0), ('A2', 'C4', 8.0),
            # Entri Penawaran Kopi Nusantara (A3)
            ('A3', 'C1', 140.0), ('A3', 'C2', 80.0), ('A3', 'C3', 3.0), ('A3', 'C4', 4.0)
        ]
        cursor.executemany(
            "INSERT INTO D3_penawaran (id_supplier, id_kriteria, nilai) VALUES (?, ?, ?)",
            data_penawaran
        )

        logging.info("Data dummy berhasil di-seed ke dalam database.")

        conn.commit()
        logging.info("Database initialization selesai. Database siap digunakan untuk engine TOPSIS.")

    except sqlite3.Error as e:
        logging.exception(f"Terjadi kesalahan operasional pada SQLite: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()  # Rollback transaksi untuk mencegah partial insert
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logging.info("Koneksi database ditutup.")


if __name__ == '__main__':
    init_database()
