from collections import Counter
import sqlite3
import sys

from fingerprint import generate_fingerprint, generate_single_hashes

DATABASE = "database/single.db"


def find_song(audio_file):

    peaks = generate_fingerprint(
        str(audio_file),
        window_size=2048,
        max_freq=3500,
        neighborhood_size=10,
        min_db=-50,
    )

    query_hashes = generate_single_hashes(peaks)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    votes = Counter()

    for hash_value, query_anchor_time in query_hashes:

        cursor.execute(
            """
            SELECT song_id, anchor_time
            FROM fingerprints
            WHERE hash = ?
            """,
            (hash_value,),
        )

        matches = cursor.fetchall()

        for song_id, db_anchor_time in matches:
            offset = round(db_anchor_time - query_anchor_time, 2)
            votes[(song_id, offset)] += 1

    if not votes:
        print("No matching song found.")
        conn.close()
        return

    (best_song_id, best_offset), best_votes = votes.most_common(1)[0]

    cursor.execute(
        "SELECT name FROM songs WHERE id = ?",
        (best_song_id,),
    )

    result = cursor.fetchone()

    if result is None:
        print("Song ID not found.")
        conn.close()
        return

    print("\n========== MATCH ==========")
    print(f"Song   : {result[0]}")
    print(f"Votes  : {best_votes}")
    print(f"Offset : {best_offset:.2f} s")

    conn.close()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python match_song_single.py <audio_file>")
        sys.exit(1)

    find_song(sys.argv[1])