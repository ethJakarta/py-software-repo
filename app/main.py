from flask import Flask, render_template, send_from_directory, abort, jsonify, request
import os, time

app = Flask(__name__)
BASE_DIR = "/mnt/repo"  # ubah jika repositori-mu di lokasi lain

# Cache sederhana (10 detik)
_cache = {"data": None, "timestamp": 0}

def get_software_list():
    if _cache["data"] and time.time() - _cache["timestamp"] < 10:
        return _cache["data"]

    software_list = []
    def format_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.startswith('.'):
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, BASE_DIR)
            category = os.path.relpath(root, BASE_DIR).split(os.sep)[0] or "Uncategorized"

            name, ext = os.path.splitext(file)
            parts = name.split('_')
            name = parts[0]
            version = parts[1] if len(parts) > 1 else "Unknown"

            try:
                file_size = format_size(os.path.getsize(file_path))
            except OSError:
                file_size = "Unknown"

            software_list.append({
                "name": name,
                "version": version,
                "category": category,
                "relative_path": relative_path.replace("\\", "/"),
                "size": file_size,
            })

    _cache["data"] = software_list
    _cache["timestamp"] = time.time()
    return software_list


@app.route('/')
def index():
    categories = sorted(set(sw["category"] for sw in get_software_list()))
    return render_template('index.html', categories=categories)


@app.route('/api/softwares')
def api_softwares():
    softwares = get_software_list()
    search = request.args.get("search", "").lower()
    category = request.args.get("category", "").lower()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 9))

    filtered = [
        sw for sw in softwares
        if (search in sw["name"].lower()) and (not category or sw["category"].lower() == category)
    ]

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "softwares": paginated
    })


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
    app.run(host='0.0.0.0', port=5000, debug=True)
