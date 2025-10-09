from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

BASE_DIR = "/mnt/repo"

def get_software_list():
    software_list = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.startswith('.'):
                continue
            relative_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
            category = os.path.relpath(root, BASE_DIR).split(os.sep)[0] or "Uncategorized"
            name, ext = os.path.splitext(file)
            parts = name.split('_')
            name = parts[0]
            version = parts[1] if len(parts) > 1 else "1.0.0"
            software_list.append({
                "name": name,
                "version": version,
                "category": category,
                "description": f"{name}",
                "relative_path": relative_path.replace("\\", "/")
            })
    return software_list

@app.route('/')
def index():
    softwares = get_software_list()
    categories = sorted(set(sw["category"] for sw in softwares))
    return render_template('index.html', softwares=softwares, categories=categories)

@app.route('/download/<path:filename>')
def download(filename):
    safe_path = os.path.normpath(filename)
    full_path = os.path.join(BASE_DIR, safe_path)
    if not full_path.startswith(BASE_DIR):
        abort(403)
    if not os.path.exists(full_path):
        abort(404)
    return send_from_directory(BASE_DIR, safe_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
