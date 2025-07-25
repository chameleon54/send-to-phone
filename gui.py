from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from config import SERVER_IP
import qrcode
from PIL import Image, ImageTk
import pyperclip
import os
from tkinter import ttk
import os
# ---------------- FUNCTIONS ---------------- #
class ProgressFile:
    def __init__(self, file_path, callback):
        self.file = open(file_path, 'rb')
        self.callback = callback
        self.length = os.path.getsize(file_path)
        self.read_bytes = 0

    def __len__(self):
        return self.length

    def read(self, size):
        if cancel_flag.get():
            return b'' 
        chunk = self.file.read(size)
        if chunk:
            self.read_bytes += len(chunk)
            self.callback(self.read_bytes, self.length)
        return chunk

    def close(self):
        self.file.close()


def send_file_path(file_path):
    filename = os.path.basename(file_path)
    try:
        cancel_flag.set(False)
        cancel_button.config(state="normal")
        cancel_button.pack(pady=5)
        progress["value"] = 0
        progress.pack(pady=5)
        upload_status.config(text=f"⬆️ Uploading: {filename}", fg="#444")
        root.update_idletasks()


        def update_progress(current, total):
            percent = (current / total) * 100
            progress["value"] = percent
            root.update_idletasks()

        pf = ProgressFile(file_path, update_progress)
        headers = {'Content-Length': str(len(pf))}
        r = requests.post(SERVER_IP + "/upload", data=pf, headers=headers, files={'file': (filename, pf)})

        pf.close()

        if cancel_flag.get():
            upload_status.config(text=f"⚠️ Canceled: {filename}", fg="orange")
            progress["value"] = 0
        else:
            upload_status.config(text=f"✅ Uploaded: {filename}", fg="green")
            progress["value"] = 100

        progress.pack_forget()  # Hide progress bar after upload is done

    except Exception as e:
        upload_status.config(text=f"❌ Failed: {filename}", fg="red")
        progress["value"] = 0
        print(str(e))
        progress.pack_forget()  # Hide progress bar on error
    finally:
        cancel_button.config(state="disabled")
        cancel_flag.set(False)
        progress.pack_forget()
        cancel_flag.set(False)


def on_drop(event):
    files = root.tk.splitlist(event.data)
    for file_path in files:
        if os.path.isfile(file_path):
            send_file_path(file_path)

def send_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file_path(file_path)

def send_clipboard():
    text = pyperclip.paste()
    try:
        r = requests.post(SERVER_IP + "/clipboard", json={"text": text})
        messagebox.showinfo("✅ Clipboard", "Text sent to phone!")
    except Exception as e:
        messagebox.showerror("❌ Error", str(e))

def get_clipboard():
    try:
        r = requests.get(SERVER_IP + "/clipboard")
        pyperclip.copy(r.json().get("clipboard", ""))
        messagebox.showinfo("✅ Clipboard", "Text copied from phone!")
    except Exception as e:
        messagebox.showerror("❌ Error", str(e))


# ---------------- GUI DESIGN ---------------- #
root = TkinterDnD.Tk()
cancel_flag = tk.BooleanVar(value=False)
root.title("📱 Send to Phone")
root.configure(bg="#f2f2f2")
root.geometry("420x620")
root.resizable(False, False)

# Setup modern ttk style
style = ttk.Style()
style.theme_use("clam")

# --- BUTTON STYLE ---
style.configure("TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(10, 8),
    background="#e0e0e0",
    foreground="#000",
    relief="flat")

style.map("TButton",
    background=[("active", "#d0d0d0")],
    foreground=[("active", "#000")])

# --- PROGRESS BAR STYLE ---
style.configure("TProgressbar",
    thickness=10,
    troughcolor="#e6e6e6",
    background="#4CAF50",
    bordercolor="#f2f2f2")

# --- Title & IP Display ---
tk.Label(root, text="📡 Send to Phone", font=("Segoe UI", 18, "bold"), bg="#f2f2f2").pack(pady=(15, 5))
tk.Label(root, text="Your Local IP (scan from phone):", bg="#f2f2f2", font=("Segoe UI", 10)).pack()
tk.Label(root, text=SERVER_IP, font=("Courier", 12, "bold"), bg="#f2f2f2", fg="#333").pack(pady=(5, 10))

# --- QR Code ---
qr = qrcode.make(SERVER_IP)
qr = qr.resize((180, 180))
qr_img = ImageTk.PhotoImage(qr)
tk.Label(root, image=qr_img, bg="#f2f2f2").pack(pady=5)

# --- Drag & Drop Label ---
drop_label = tk.Label(root, text="📥 Drag files here to send to phone",
                      relief="ridge", borderwidth=2,
                      bg="#ffffff", fg="#444",
                      width=40, height=4,
                      font=("Segoe UI", 10), highlightthickness=1, highlightbackground="#ccc")
drop_label.pack(pady=(15, 10))
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', on_drop)

# --- Upload Status ---
upload_status = tk.Label(root, text="", bg="#f2f2f2", fg="#444", font=("Segoe UI", 10))
upload_status.pack(pady=(0, 5))

# --- Progress Bar (Hidden initially) ---
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=5)
progress.pack_forget()

# --- Cancel Button (Hidden initially) ---
cancel_button = ttk.Button(root, text="❌ Cancel Upload", state="disabled", command=lambda: cancel_flag.set(True))
cancel_button.pack(pady=5)
cancel_button.pack_forget()

# --- Action Buttons ---
ttk.Button(root, text="📁 Send File", command=send_file).pack(pady=6)
ttk.Button(root, text="📋 Send Clipboard Text", command=send_clipboard).pack(pady=6)
ttk.Button(root, text="📥 Get Clipboard from Phone", command=get_clipboard).pack(pady=6)

# --- Footer ---
tk.Label(root, text="Made with ❤️ over LAN", font=("Segoe UI", 8), bg="#f2f2f2", fg="#888").pack(side="bottom", pady=12)

root.mainloop()
# ---------------- END OF GUI DESIGN ---------------- #
# Note: Ensure you have the required packages installed: Flask, pyperclip, requests, qrcode[pil], tkinterdnd2
# You can install them using pip:
