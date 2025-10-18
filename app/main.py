from flask import Flask, render_template, jsonify, request, send_from_directory, abort
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------------------------
# 🔹 Konfigurasi dasar
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "software.db")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
UPLOAD_FOLDER = IMAGES_DIR
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------
# 🔹 Helper
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------
# 🔹 Halaman utama
# ---------------------------
@app.route('/')
def index():
    conn = get_db_connection()
    categories = [row['category'] for row in conn.execute("SELECT DISTINCT category FROM software ORDER BY category").fetchall()]
    tags = [row['tag'] for row in conn.execute("SELECT DISTINCT tag FROM software WHERE tag != ''").fetchall()]
    conn.close()

    unique_tags = sorted(set(t.strip() for tag in tags for t in tag.split(',') if t.strip()))
    return render_template('index.html', categories=categories, tags=unique_tags)


# ---------------------------
# 🔹 API Software List (AJAX)
# ---------------------------
@app.route('/api/software')
def api_software():
    search = request.args.get("search", "").lower()
    category = request.args.get("category", "").lower()
    tag = request.args.get("tag", "").lower()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 9))

    conn = get_db_connection()
    query = "SELECT * FROM software WHERE 1=1"
    params = []

    if search:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{search}%")

    if category:
        query += " AND LOWER(category) = ?"
        params.append(category)

    if tag:
        query += " AND LOWER(tag) LIKE ?"
        params.append(f"%{tag}%")

    total = conn.execute(f"SELECT COUNT(*) FROM ({query})", params).fetchone()[0]
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    rows = conn.execute(query, params).fetchall()
    conn.close()

    softwares = [dict(row) for row in rows]
    total_pages = max(1, (total + per_page - 1) // per_page)

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": total_pages,
        "items": softwares
    })


# ---------------------------
# 🔹 Download file
# ---------------------------
@app.route('/download/<path:filename>')
def download(filename):
    safe_path = os.path.normpath(filename)
    base_path = "/mnt/repo"
    full_path = os.path.join(base_path, safe_path)

    if not full_path.startswith(base_path):
        abort(403)
    if not os.path.exists(full_path):
        abort(404)
    return send_from_directory(base_path, safe_path, as_attachment=True)


# ---------------------------
# 🔹 Static Images
# ---------------------------
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


# ====================================================
# 🔸 ADMIN ROUTES
# ====================================================

@app.route('/admin')
def admin_page():
    """Halaman admin untuk CRUD software"""
    return render_template('admin.html')


@app.route('/api/admin/software', methods=['GET'])
def get_software_admin():
    """Tampilkan semua software di panel admin"""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM software ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/api/admin/software', methods=['POST'])
def add_software():
    """Tambah software baru"""
    data = request.form
    file = request.files.get('image')

    name = data.get('name')
    version = data.get('version')
    category = data.get('category')
    description = data.get('description')
    file_path = data.get('file_path')
    size = data.get('size')
    tag = data.get('tags', '')

    # Upload gambar
    image_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        image_path = f"/static/images/{filename}"

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO software (name, version, category, description, image_path, file_path, size, tag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, version, category, description, image_path, file_path, size, tag))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


@app.route('/api/admin/software/<int:id>', methods=['DELETE'])
def delete_software(id):
    """Hapus software berdasarkan ID"""
    conn = get_db_connection()
    conn.execute("DELETE FROM software WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


# ---------------------------
# 🔹 Run server
# ---------------------------
if __name__ == '__main__':
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
