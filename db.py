import sqlite3

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('ujian.db')
    return conn

# Create or modify the proctoring table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Modify proctoring table to include new columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proctoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nim TEXT NOT NULL,
            kelas TEXT NOT NULL,
            mata_kuliah TEXT NOT NULL,
            code TEXT NOT NULL,
            waktu TEXT NOT NULL,
            bentuk_kecurangan TEXT NOT NULL,
            bukti_kecurangan TEXT NOT NULL
        )
    ''')

    # Create the mahasiswa table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nim TEXT NOT NULL,
            kelas TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            code TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
# Check if mahasiswa exists in the mahasiswa table
def is_mahasiswa_terdaftar(nim):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM mahasiswa WHERE nim = ?', (nim,))
    result = cursor.fetchone()[0]
    
    conn.close()
    return result > 0

# Check if the code is valid for the given mahasiswa
def is_code_valid(nim, code):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM mahasiswa WHERE nim = ? AND code = ?', (nim, code))
    result = cursor.fetchone()[0]
    
    conn.close()
    return result > 0

# Insert a new record into the proctoring table
def insert_record(nama, nim, kelas, mata_kuliah, code, waktu, bentuk_kecurangan, bukti_kecurangan):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO proctoring (nama, nim, kelas, mata_kuliah, code, waktu, bentuk_kecurangan, bukti_kecurangan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nama, nim, kelas, mata_kuliah, code, waktu, bentuk_kecurangan, bukti_kecurangan))
    
    conn.commit()
    conn.close()

# Fetch all records from the proctoring table
def fetch_all_records():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM proctoring')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# Insert mahasiswa data into the mahasiswa table
def insert_mahasiswa(nama, nim, kelas, whatsapp, code):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO mahasiswa (nama, nim, kelas, whatsapp, code)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, nim, kelas, whatsapp, code))
    
    conn.commit()
    conn.close()

# Fetch all records from the mahasiswa table
def fetch_all_mahasiswa():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM mahasiswa')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# Call create_table when this script is run
if __name__ == '__main__':
    create_table()
