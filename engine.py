import sqlite3
import math
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def run_topsis(kode_batch: str):
    db_path = 'database.db'

    conn = None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Tarik & Transformasi Data (Query)
        query = """
            SELECT p.id_supplier, s.nama_supplier, p.id_kriteria, p.nilai, k.bobot_desimal, k.sifat
            FROM D3_penawaran p
            JOIN D1_kriteria k ON p.id_kriteria = k.id_kriteria
            JOIN D2_supplier s ON p.id_supplier = s.id_supplier
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        matrix_x = {}
        criteria_info = {}
        supplier_names = {}

        for row in rows:
            supplier = row['id_supplier']
            kriteria = row['id_kriteria']

            if supplier not in supplier_names:
                supplier_names[supplier] = row['nama_supplier']

            if supplier not in matrix_x:
                matrix_x[supplier] = {}
            matrix_x[supplier][kriteria] = row['nilai']

            if kriteria not in criteria_info:
                criteria_info[kriteria] = {
                    'bobot': row['bobot_desimal'],
                    'sifat': row['sifat']
                }

        if not matrix_x:
            logging.error("Data penawaran kosong. Pastikan seeding data berhasil.")
            return

        # Normalisasi Matriks (R)
        pembagi_kriteria = {}
        for kriteria in criteria_info.keys():
            sum_squares = sum(math.pow(matrix_x[sup][kriteria], 2) for sup in matrix_x)
            pembagi_kriteria[kriteria] = math.sqrt(sum_squares)

        matrix_r = {}
        for sup in matrix_x:
            matrix_r[sup] = {}
            for kriteria in matrix_x[sup]:
                matrix_r[sup][kriteria] = matrix_x[sup][kriteria] / pembagi_kriteria[kriteria]

        # Normalisasi Terbobot (Y)
        matrix_y = {}
        for sup in matrix_r:
            matrix_y[sup] = {}
            for kriteria in matrix_r[sup]:
                matrix_y[sup][kriteria] = matrix_r[sup][kriteria] * criteria_info[kriteria]['bobot']

        # Solusi Ideal Positif (A+) & Negatif (A-)
        a_plus = {}
        a_minus = {}

        for kriteria, info in criteria_info.items():
            nilai_terbobot = [matrix_y[sup][kriteria] for sup in matrix_y]

            if info['sifat'] == 'Benefit':
                a_plus[kriteria] = max(nilai_terbobot)
                a_minus[kriteria] = min(nilai_terbobot)
            elif info['sifat'] == 'Cost':
                a_plus[kriteria] = min(nilai_terbobot)
                a_minus[kriteria] = max(nilai_terbobot)

        # Menghitung Jarak (D+ dan D-) & Nilai Preferensi (V)
        hasil_akhir = []

        for sup in matrix_y:
            sum_d_plus = 0
            sum_d_minus = 0

            for kriteria in matrix_y[sup]:
                y_val = matrix_y[sup][kriteria]
                sum_d_plus += math.pow(y_val - a_plus[kriteria], 2)
                sum_d_minus += math.pow(y_val - a_minus[kriteria], 2)

            d_plus = math.sqrt(sum_d_plus)
            d_minus = math.sqrt(sum_d_minus)

            V = d_minus / (d_minus + d_plus)
            hasil_akhir.append({'id_supplier': sup, 'skor': V})

        hasil_akhir.sort(key=lambda x: x['skor'], reverse=True)

        keputusan_map = {
            0: 'Terpilih (Penerima PO)',
            1: 'Alternatif Cadangan',
            2: 'Ditolak'
        }

        # Insert ke D4 & Output Terminal
        insert_data = []
        print("\n=== HASIL KALKULASI TOPSIS ===")
        for index, item in enumerate(hasil_akhir):
            keputusan = keputusan_map.get(index, 'Ditolak')

            nama_sup = supplier_names[item['id_supplier']]

            print(f"{nama_sup} ({item['id_supplier']}) -> Skor: {item['skor']:.3f} | Status: {keputusan}")

            insert_data.append((
                kode_batch,
                item['id_supplier'],
                item['skor'],
                keputusan
            ))

        cursor.executemany("""
            INSERT INTO D4_hasil_kalkulasi (kode_batch, id_supplier, skor_akhir, keputusan)
            VALUES (?, ?, ?, ?)
        """, insert_data)

        conn.commit()
        logging.info("Hasil kalkulasi berhasil disimpan ke tabel D4_hasil_kalkulasi.")

    except sqlite3.Error as e:
        logging.exception(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logging.exception(f"Terjadi kesalahan logika program: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    run_topsis("BATCH-20260621-01")
