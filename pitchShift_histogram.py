from collections import Counter
import argparse
import sqlite3
import tempfile
import os

import librosa
import soundfile as sf
import matplotlib.pyplot as plt

from fingerprint import generate_fingerprint, generate_hashes

DATABASE = "database/fingerprints.db"


def plot_pitch_shift_histogram(
    input_file,
    pitch_shift,
    output_image="offset_histogram.png",
):
    print(f"Pitch shifting by {pitch_shift} semitones...")

    # ------------------------------------------------------------
    # Pitch shift
    # ------------------------------------------------------------
    audio, sr = librosa.load(input_file, sr=None, mono=True)

    shifted_audio = librosa.effects.pitch_shift(
        audio,
        sr=sr,
        n_steps=pitch_shift,
    )

    # Save to a temporary wav for fingerprinting
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_file = tmp.name

    sf.write(temp_file, shifted_audio, sr)

    # ------------------------------------------------------------
    # Fingerprint
    # ------------------------------------------------------------
    peaks = generate_fingerprint(
        temp_file,
        window_size=2048,
        max_freq=3500,
        neighborhood_size=10,
        min_db=-50,
    )

    query_hashes = generate_hashes(
        peaks,
        fan_value=5,
        max_time_delta=5.0,
    )

    os.remove(temp_file)

    # ------------------------------------------------------------
    # Database matching
    # ------------------------------------------------------------
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
        print("No matches found.")
        conn.close()
        return

    # ------------------------------------------------------------
    # Determine best song
    # ------------------------------------------------------------
    song_scores = Counter()

    for (song_id, offset), count in votes.items():
        song_scores[song_id] += count

    best_song_id = song_scores.most_common(1)[0][0]

    cursor.execute(
        "SELECT name FROM songs WHERE id=?",
        (best_song_id,),
    )

    song_name = cursor.fetchone()[0]

    # ------------------------------------------------------------
    # Collect histogram
    # ------------------------------------------------------------
    histogram = Counter()

    for (song_id, offset), count in votes.items():
        if song_id == best_song_id:
            histogram[offset] += count

    conn.close()

    offsets = sorted(histogram.keys())
    counts = [histogram[o] for o in offsets]

    # ------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------
    plt.figure(figsize=(12, 5))

    plt.bar(offsets, counts, width=0.05)

    plt.xlabel("Offset (seconds)")
    plt.ylabel("Votes")
    plt.title(
        f"Offset Histogram\n"
        f"Song: {song_name}\n"
        f"Pitch Shift: {pitch_shift:+.1f} semitones"
    )

    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_image, dpi=300)
    plt.close()

    print(f"Best match : {song_name}")
    print(f"Histogram saved to {output_image}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "audio_file",
        help="Input audio file",
    )

    parser.add_argument(
        "--shift",
        type=float,
        default=2,
        help="Pitch shift in semitones",
    )

    parser.add_argument(
        "--output", "-o",
        default="offset_histogram.png",
        help="Output histogram image",
    )

    args = parser.parse_args()

    plot_pitch_shift_histogram(
        args.audio_file,
        args.shift,
        args.output,
    )