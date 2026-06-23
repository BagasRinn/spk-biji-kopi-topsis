from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime
import time
from engine import run_topsis

app = Flask(__name__)
DB_PATH = 'database.db'


def get_db_connection():
    """Helper function untuk membuka koneksi database secara modular."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Halaman Master Data
@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    kriteria = conn.execute('SELECT * FROM D1_kriteria').fetchall()
    supplier = conn.execute('SELECT * FROM D2_supplier').fetchall()
    conn.close()

    return render_template('index.html', kriteria=kriteria, supplier=supplier)


# Halaman Matriks Penawaran
@app.route('/penawaran', methods=['GET'])
def penawaran():
    conn = get_db_connection()
    query = """
        SELECT s.nama_supplier, k.nama_kriteria, p.nilai
        FROM D3_penawaran p
        JOIN D2_supplier s ON p.id_supplier = s.id_supplier
        JOIN D1_kriteria k ON p.id_kriteria = k.id_kriteria
        ORDER BY p.id_supplier, p.id_kriteria
    """
    data_penawaran = conn.execute(query).fetchall()
    conn.close()

    return render_template('penawaran.html', penawaran=data_penawaran)


# Halaman SPK & Laporan
@app.route('/spk', methods=['GET', 'POST'])
def spk():
    # tombol "JALANKAN KALKULASI TOPSIS"
    if request.method == 'POST':
        kode_batch = "BATCH-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        run_topsis(kode_batch)

        return redirect(url_for('spk'))

    conn = get_db_connection()

    query_latest_batch = "SELECT kode_batch FROM D4_hasil_kalkulasi ORDER BY id_kalkulasi DESC LIMIT 1"
    latest_batch_row = conn.execute(query_latest_batch).fetchone()

    hasil_spk = []
    if latest_batch_row:
        latest_batch = latest_batch_row['kode_batch']

        query_hasil = """
            SELECT s.nama_supplier, h.skor_akhir, h.keputusan
            FROM D4_hasil_kalkulasi h
            JOIN D2_supplier s ON h.id_supplier = s.id_supplier
            WHERE h.kode_batch = ?
            ORDER BY h.skor_akhir DESC
        """
        hasil_spk = conn.execute(query_hasil, (latest_batch,)).fetchall()

    conn.close()

    return render_template('spk.html', hasil_spk=hasil_spk)


# Halaman Kelola
@app.route('/kelola', methods=['GET', 'POST'])
def kelola():
    with get_db_connection() as conn:
        # form submission
        if request.method == 'POST':
            id_supplier_baru = f"S-{int(time.time())}"
            nama_supplier = request.form.get('nama_supplier')

            conn.execute(
                "INSERT INTO D2_supplier (id_supplier, nama_supplier) VALUES (?, ?)",
                (id_supplier_baru, nama_supplier)
            )

            kriteria_list = conn.execute("SELECT id_kriteria FROM D1_kriteria").fetchall()
            for k in kriteria_list:
                id_k = k['id_kriteria']
                nilai_input = request.form.get(f"nilai_{id_k}")
                conn.execute(
                    "INSERT INTO D3_penawaran (id_supplier, id_kriteria, nilai) VALUES (?, ?, ?)",
                    (id_supplier_baru, id_k, float(nilai_input))
                )
            conn.commit()
            return redirect(url_for('kelola'))

        # Menangani tampilan halaman
        kriteria = conn.execute("SELECT * FROM D1_kriteria").fetchall()
        suppliers_raw = conn.execute("SELECT * FROM D2_supplier ORDER BY id_supplier DESC").fetchall()

        suppliers_detail = []
        for s in suppliers_raw:
            penawaran_raw = conn.execute(
                "SELECT id_kriteria, nilai FROM D3_penawaran WHERE id_supplier = ?",
                (s['id_supplier'],)
            ).fetchall()

            # Ubah dari list ke dictionary (Pivot) agar mudah dibaca oleh Jinja2
            penawaran_dict = {p['id_kriteria']: p['nilai'] for p in penawaran_raw}

            suppliers_detail.append({
                'id_supplier': s['id_supplier'],
                'nama_supplier': s['nama_supplier'],
                'penawaran': penawaran_dict
            })

    return render_template('kelola.html', kriteria=kriteria, supplier=suppliers_detail)


# Endpoint Edit Supplier
@app.route('/edit/<id_supplier>', methods=['POST'])
def edit(id_supplier):
    with get_db_connection() as conn:
        nama_supplier = request.form.get('nama_supplier')

        conn.execute(
            "UPDATE D2_supplier SET nama_supplier = ? WHERE id_supplier = ?",
            (nama_supplier, id_supplier)
        )

        kriteria_list = conn.execute("SELECT id_kriteria FROM D1_kriteria").fetchall()
        for k in kriteria_list:
            id_k = k['id_kriteria']
            nilai_input = request.form.get(f"nilai_{id_k}")

            conn.execute("""
                UPDATE D3_penawaran
                SET nilai = ?
                WHERE id_supplier = ? AND id_kriteria = ?
            """, (float(nilai_input), id_supplier, id_k))

        conn.commit()
    return redirect(url_for('kelola'))


# Endpoint Hapus Supplier
@app.route('/hapus/<id_supplier>', methods=['POST'])
def hapus(id_supplier):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM D2_supplier WHERE id_supplier = ?", (id_supplier,))
        conn.commit()

    return redirect(url_for('kelola'))


if __name__ == '__main__':
    app.run(debug=True)
