from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = "received"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Get clipboard text (to phone)
@app.route("/clipboard", methods=["GET"])
def get_clipboard():
    import pyperclip
    return {"clipboard": pyperclip.paste()}

# Set clipboard (from phone)
@app.route("/clipboard", methods=["POST"])
def set_clipboard():
    import pyperclip
    data = request.json
    text = data.get("text", "")
    pyperclip.copy(text)
    return {"status": "ok"}

# Receive file from phone
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return {"status": "uploaded", "filename": file.filename}

# Serve file to phone
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
