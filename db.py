import sqlite3
from pathlib import Path

DB_PATH = Path("database") / "fingerprints.db"


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    return conn


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            anchor_time REAL NOT NULL,
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hash
        ON fingerprints(hash)
    """)

    conn.commit()


def insert_song(conn, song_name):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO songs(name)
        VALUES(?)
    """, (song_name,))

    conn.commit()

    cursor.execute("""
        SELECT id
        FROM songs
        WHERE name = ?
    """, (song_name,))

    return cursor.fetchone()[0]


def insert_hashes(conn, song_id, hashes):
    """
    hashes:
    [
        ("523-610-93", 0.418),
        ("610-820-120", 0.511),
        ...
    ]
    """

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO fingerprints(hash, song_id, anchor_time)
        VALUES (?, ?, ?)
    """, [
        (hash_value, song_id, anchor_time)
        for hash_value, anchor_time in hashes
    ])

    conn.commit()


def get_song_name(conn, song_id):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM songs
        WHERE id = ?
    """, (song_id,))

    result = cursor.fetchone()

    if result is None:
        return None

    return result[0]


def find_hash(conn, hash_value):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT song_id, anchor_time
        FROM fingerprints
        WHERE hash = ?
    """, (hash_value,))

    return cursor.fetchall()


def clear_database(conn):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM fingerprints")
    cursor.execute("DELETE FROM songs")

    conn.commit()


if __name__ == "__main__":
    conn = connect()
    create_tables(conn)
    conn.close()

    print("Database initialized.")