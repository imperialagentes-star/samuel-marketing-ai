import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "samuel.db"


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            niche TEXT,
            description TEXT,
            instagram TEXT,
            tiktok TEXT,
            facebook TEXT,
            youtube TEXT,
            website TEXT,
            brand_tone TEXT,
            target_audience TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT,
            content TEXT,
            client_id INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)

    defaults = [
        ("report_hour", "8"),
        ("report_minute", "0"),
        ("monitor_active", "true"),
        ("monitor_keywords", "marketing digital,redes sociales,publicidad,ventas,contenido viral"),
    ]
    for key, val in defaults:
        conn.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()
