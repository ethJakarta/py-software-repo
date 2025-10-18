import sqlite3
import os

# ==========================
# KONFIGURASI DASAR
# ==========================
BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "software.db")
IMG_DIR = os.path.join(BASE_DIR, "static", "images")

def init_db():
    """Inisialisasi database SQLite untuk software repository"""
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    # Hapus database lama jika ada (opsional)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🧹 Database lama dihapus.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ==========================
    # TABEL SOFTWARE
    # ==========================
    c.execute("""
    CREATE TABLE software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        version TEXT,
        category TEXT,
        description TEXT,
        image_path TEXT,
        file_path TEXT,
        size TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ==========================
    # TABEL TAGS
    # ==========================
    c.execute("""
    CREATE TABLE tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)

    # ==========================
    # TABEL RELASI SOFTWARE ↔ TAGS
    # ==========================
    c.execute("""
    CREATE TABLE software_tags (
        software_id INTEGER,
        tag_id INTEGER,
        FOREIGN KEY (software_id) REFERENCES software(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (software_id, tag_id)
    );
    """)

    # ==========================
    # DATA CONTOH SOFTWARE
    # ==========================
    softwares = [
        ("Google Chrome", "121.0", "Browser",
         "Peramban cepat dan aman dari Google.",
         "/static/images/chrome.png", "/repo/browser/chrome_121.exe", "95 MB"),

        ("WPS Office", "12.1", "Office",
         "Alternatif Microsoft Office dengan fitur lengkap.",
         "/static/images/wps.png", "/repo/office/wps_12.1.exe", "180 MB"),

        ("Visual Studio Code", "1.90", "Development",
         "Editor kode ringan dan powerful.",
         "/static/images/vscode.png", "/repo/dev/vscode_1.90.exe", "85 MB"),
    ]
    c.executemany("""
    INSERT INTO software (name, version, category, description, image_path, file_path, size)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, softwares)

    # ==========================
    # DATA CONTOH TAGS
    # ==========================
    tags = [
        ("browser",),
        ("office",),
        ("productivity",),
        ("editor",),
        ("development",),
        ("open-source",),
    ]
    c.executemany("INSERT INTO tags (name) VALUES (?);", tags)

    # ==========================
    # RELASI SOFTWARE ↔ TAGS
    # ==========================
    relations = [
        (1, 1), (1, 3),        # Chrome → browser, productivity
        (2, 2), (2, 3),        # WPS Office → office, productivity
        (3, 4), (3, 5), (3, 6) # VSCode → editor, development, open-source
    ]
    c.executemany("""
    INSERT INTO software_tags (software_id, tag_id) VALUES (?, ?);
    """, relations)

    conn.commit()
    conn.close()

    print("✅ Database berhasil dibuat di:", DB_PATH)

if __name__ == "__main__":
    init_db()

