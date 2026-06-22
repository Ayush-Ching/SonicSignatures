import sqlite3
from pathlib import Path

DATABASE = Path("database") / "single.db"


def connect():
    DATABASE.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DATABASE)


def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            anchor_time REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_hash
        ON fingerprints(hash)
    """)

    conn.commit()


def insert_song(conn, song_name):
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO songs(name) VALUES (?)",
        (song_name,)
    )

    conn.commit()

    cur.execute(
        "SELECT id FROM songs WHERE name = ?",
        (song_name,)
    )

    return cur.fetchone()[0]


def insert_hashes(conn, song_id, hashes):
    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO fingerprints(hash, song_id, anchor_time)
        VALUES (?, ?, ?)
        """,
        [
            (hash_value, song_id, anchor_time)
            for hash_value, anchor_time in hashes
        ]
    )

    conn.commit()