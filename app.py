from flask import Flask, request, send_file, jsonify
import os
import time
import pyperclip

app = Flask(__name__)
UPLOAD_FOLDER = "received"
MAX_FILE_SIZE_MB = 1024 #May cause issues with very large files and timeouts
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Log every request
@app.before_request
def log_request():
    print(f"[{request.method}] {request.path} - From {request.remote_addr}")

# Get clipboard text (to phone)
@app.route("/clipboard", methods=["GET"])
def get_clipboard():
    try:
        text = pyperclip.paste()
        return jsonify({"clipboard": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Set clipboard text (from phone)
@app.route("/clipboard", methods=["POST"])
def set_clipboard():
    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing clipboard text"}), 400
        pyperclip.copy(data["text"])
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Receive file from phone
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    print(f"[UPLOAD] {file.filename} saved to {save_path}")
    return jsonify({"status": "uploaded", "filename": file.filename})

# Serve file to phone
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle large file error
@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": f"File exceeds {MAX_FILE_SIZE_MB}MB limit"}), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
