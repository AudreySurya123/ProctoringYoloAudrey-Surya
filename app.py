import cv2
from ultralytics import YOLO
from datetime import datetime
from flask import Flask, render_template, Response, request, redirect, url_for
import os
from db import insert_record, fetch_all_records, connect_db, insert_mahasiswa, fetch_all_mahasiswa
from kamera import run_video_stream
import subprocess
from flask import send_from_directory

app = Flask(__name__)

# Flask routes
@app.route("/")
def main():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/dashboard")
def dashboard():
    return render_template('index.html')

@app.route("/data_admin")
def admin():
    return render_template('dataAdmin.html')

@app.route("/data_mahasiswa")
def mahasiswa():
    # Fetch all mahasiswa records from the database
    records = fetch_all_mahasiswa()
    return render_template('dataMahasiswa.html', mahasiswa=records)

@app.route('/add_mahasiswa', methods=['POST'])
def add_mahasiswa():
    nama = request.form['nama']
    nim = request.form['nim']
    kelas = request.form['kelas']
    whatsapp = request.form['whatsapp']
    code = request.form['code']  # Capture generated code
    
    insert_mahasiswa(nama, nim, kelas, whatsapp, code)
    return redirect(url_for('mahasiswa'))

@app.route("/edit_mahasiswa", methods=["POST"])
def edit_mahasiswa():
    id = request.form['id']
    nama = request.form['nama']
    nim = request.form['nim']
    kelas = request.form['kelas']
    whatsapp = request.form['whatsapp']
    code = request.form['code']  # Get the updated code from the form

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE mahasiswa SET nama=?, nim=?, kelas=?, whatsapp=?, code=?
        WHERE id=?
    ''', (nama, nim, kelas, whatsapp, code, id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('mahasiswa'))

@app.route("/delete_mahasiswa", methods=["POST"])
def delete_mahasiswa():
    id = request.form['id']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mahasiswa WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('mahasiswa'))

@app.route("/proctoring")
def proctoring():
    # Fetch all proctoring records
    records = fetch_all_records()
    return render_template('proctoring.html', records=records)

@app.route("/delete_all_records", methods=["POST"])
def delete_all_records():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proctoring')
    conn.commit()
    conn.close()
    return redirect(url_for('proctoring'))

@app.route("/kamera")
def kamera():
    subprocess.Popen(["dist/kamera.exe"])
    # return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response("Kamera process started", mimetype='text/plain')

@app.route('/dist/static/<path:filename>')
def serve_dist_static(filename):
    return send_from_directory('dist/static', filename)

if __name__ == "__main__":
    app.run(debug=True)
