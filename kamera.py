import cv2
from ultralytics import YOLO
from datetime import datetime
import os
from db import insert_record, create_table, is_mahasiswa_terdaftar, is_code_valid  # Import is_code_valid
import signal
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk 

# Global variable to control camera running state
camera_running = True

# Load custom YOLOv8 model
model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
model = YOLO(model_path)

# Create database table if it doesn't exist
create_table()

def stop_camera(signum, frame):
    global camera_running
    camera_running = False

# Set up signal handler to stop camera
signal.signal(signal.SIGINT, stop_camera)

# Function to process and display video frames
def run_video_stream(nama, nim, kelas, code, mata_kuliah):
    global camera_running
    cap = cv2.VideoCapture(0)  # Use the default camera
    while cap.isOpened() and camera_running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Perform inference
        results = model(frame)

        detected = False
        bentuk_kecurangan = None
        bukti_kecurangan = None

        # Check if more than one object is detected
        if len(results[0].boxes) > 1:
            bentuk_kecurangan = "Terdapat lebih dari 1 orang"
            detected = True
            bukti_kecurangan = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(os.path.join("dist/static/captures", bukti_kecurangan), frame)

        # Draw bounding boxes and labels on the frame
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])  # Get bounding box coordinates
            conf = result.conf[0]                     # Get confidence score
            cls = int(result.cls[0])                  # Get class index

            # Set bounding box color based on object class
            if model.names[cls] == "Smartphone":
                box_color = (255, 0, 0)  # Blue for "Smartphone"
                bentuk_kecurangan = "Smartphone"
                detected = True
            elif model.names[cls] == "Kertas":
                box_color = (0, 0, 255)  # Red for "Kertas"
                bentuk_kecurangan = "Kertas"
                detected = True
            elif model.names[cls] == "Tidak Mencontek":
                box_color = (0, 255, 0)  # Green for "Tidak Mencontek"
            elif model.names[cls] == "Menoleh":
                box_color = (0, 255, 255)  # Yellow for "Menoleh"
                bentuk_kecurangan = "Menoleh"
                detected = True
            else:
                continue

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

            # Label with confidence and class
            label = f"{model.names[cls]} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Capture evidence if cheating is detected
            if detected and bentuk_kecurangan != "Lebih dari 1 orang":
                bukti_kecurangan = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(os.path.join("dist/static/captures", bukti_kecurangan), frame)

        # If cheating is detected, save data to the database
        if detected:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_record(nama, nim, kelas, mata_kuliah, code, current_time, bentuk_kecurangan, bukti_kecurangan)

        # Display the generated frame
        cv2.imshow('Video Stream', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_running = False  # Update camera status after exiting
    cap.release()
    cv2.destroyAllWindows()

# Function to start the camera after input
def start_camera():
    nama = entry_nama.get()
    nim = entry_nim.get()
    kelas = entry_kelas.get()  # Get class from input form
    code = entry_code.get()
    mata_kuliah = entry_mata_kuliah.get()

    if not nama or not nim or not kelas or not code or not mata_kuliah:
        messagebox.showerror("Error", "All fields must be filled!")
    else:
        if not is_mahasiswa_terdaftar(nim):  # Validate if the student is registered
            messagebox.showerror("Error", "Student not registered!")
        elif not is_code_valid(nim, code):  # Validate if the code matches for the given NIM
            messagebox.showerror("Error", "Invalid code! Use your own registered code.")
        else:
            root.destroy()  # Close input form
            run_video_stream(nama, nim, kelas, code, mata_kuliah)  # Ensure class is also passed

def create_rounded_style():
    style = ttk.Style()
    style.configure("RoundedEntry.TEntry",
                    relief="solid",
                    padding=(10, 5),
                    fieldbackground="#f5f5f5",
                    background="#f5f5f5",
                    font=("Helvetica", 12),
                    borderwidth=2)
    return style

# Tkinter GUI setup
root = tk.Tk()
root.title("Proctoring")
root.geometry("750x500")  # Increased height for more space
root.config(bg="#f5f5f5")

# Create rounded corner style
rounded_style = create_rounded_style()

# Main container for dividing image and form (half and half)
main_frame = tk.Frame(root, bg="#f5f5f5")
main_frame.pack(fill="both", expand=True)

# Left Frame for Image (50% of root width)
left_frame = tk.Frame(main_frame, width=375, bg="#f5f5f5")
left_frame.pack(side="left", fill="both", expand=True)

# Right Frame for Form (50% of root width)
right_frame = tk.Frame(main_frame, width=375, bg="#f5f5f5")
right_frame.pack(side="right", fill="both", expand=True)

# Load and resize the image
image_path = "static/assets/bg.jpg"  # Replace with your image path
img = Image.open(image_path)
img = img.resize((375, 550), Image.Resampling.LANCZOS)  # Resize image to fit left frame
photo = ImageTk.PhotoImage(img)

# Add image to the left frame
image_label = tk.Label(left_frame, image=photo, bg="#f5f5f5")
image_label.pack(fill="both", expand=True)

# Enhanced Form Card Design
form_card = tk.Frame(right_frame, bg="#ffffff", bd=2, relief="raised", highlightbackground="#cccccc", highlightthickness=1)
form_card.place(relx=0.5, rely=0.5, anchor="center", width=375, height=500)  # Adjust form card height

form_card.grid_rowconfigure(0, weight=1)  # Atur baris 0 untuk mendukung proporsi
form_card.grid_columnconfigure(0, weight=1)  # Atur kolom 0 untuk mendukung proporsi
form_card.grid_columnconfigure(1, weight=1)  # Tambahkan jika ada 2 kolom

header = tk.Label(form_card, text="Proctoring Input Form", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333", anchor="center", justify="center")
header.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=10, sticky="nsew")

# Form Fields with normal text labels (non-bold)
tk.Label(form_card, text="Nama:", font=("Helvetica", 12), bg="#ffffff", fg="#333333").grid(row=1, column=0, columnspan=2, pady=5, padx=(64, 10), sticky="w")

entry_nama = ttk.Entry(form_card, style="RoundedEntry.TEntry", width=35)
entry_nama.grid(row=2, column=0, columnspan=2, pady=5, padx=10)

tk.Label(form_card, text="NIM:", font=("Helvetica", 12), bg="#ffffff", fg="#333333").grid(row=3, column=0, columnspan=2, pady=5, padx=(64, 10), sticky="w")
entry_nim = ttk.Entry(form_card, style="RoundedEntry.TEntry", width=35)
entry_nim.grid(row=4, column=0, columnspan=2, pady=5, padx=10)

tk.Label(form_card, text="Kelas:", font=("Helvetica", 12), bg="#ffffff", fg="#333333").grid(row=5, column=0, columnspan=2, pady=5, padx=(64, 10), sticky="w")
entry_kelas = ttk.Entry(form_card, style="RoundedEntry.TEntry", width=35)
entry_kelas.grid(row=6, column=0, columnspan=2, pady=5, padx=10)

tk.Label(form_card, text="Kode Akses:", font=("Helvetica", 12), bg="#ffffff", fg="#333333").grid(row=9, column=0, columnspan=2, pady=5, padx=(64, 10), sticky="w")
entry_code = ttk.Entry(form_card, style="RoundedEntry.TEntry", width=35)
entry_code.grid(row=10, column=0, columnspan=2, pady=5, padx=10)

tk.Label(form_card, text="Mata Kuliah:", font=("Helvetica", 12), bg="#ffffff", fg="#333333").grid(row=7, column=0, columnspan=2, pady=5, padx=(64, 10), sticky="w")
entry_mata_kuliah = ttk.Entry(form_card, style="RoundedEntry.TEntry", width=35)
entry_mata_kuliah.grid(row=8, column=0, columnspan=2, pady=5, padx=10)

# Start Button
start_button = tk.Button(form_card, text="Start Camera", font=("Helvetica", 12), bg="#039be5", fg="white", relief="flat", bd=0, width=20, command=start_camera)

start_button.grid(row=11, column=0, columnspan=2, pady=20)

root.mainloop()