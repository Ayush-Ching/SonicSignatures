from pathlib import Path

from fingerprint import generate_fingerprint, generate_hashes
from db import (
    connect,
    create_tables,
    insert_song,
    insert_hashes,
)

SONGS_DIR = Path("songs")


def build_database():
    conn = connect()
    create_tables(conn)

    mp3_files = sorted(SONGS_DIR.glob("*.mp3"))

    if not mp3_files:
        print("No MP3 files found.")
        conn.close()
        return

    print(f"Found {len(mp3_files)} songs.\n")

    for song_path in mp3_files:

        song_name = song_path.stem

        print(f"Processing: {song_name}")

        peaks = generate_fingerprint(
            song_path,
            window_size=2048,
            max_freq=3500,
            neighborhood_size=10,
            min_db=-50,
        )

        hashes = generate_hashes(
            peaks,
            fan_value=5,
            max_time_delta=5.0,
        )

        song_id = insert_song(conn, song_name)

        insert_hashes(conn, song_id, hashes)

        print(f"  Peaks : {len(peaks)}")
        print(f"  Hashes: {len(hashes)}\n")

    conn.close()

    print("Database build complete.")


if __name__ == "__main__":
    build_database()