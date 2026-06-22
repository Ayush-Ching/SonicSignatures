from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter

from fingerprint import generate_fingerprint

SONGS_DIR = Path("songs")
OUTPUT_DIR = Path("fingerprint_images")

OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
    ".aac",
}


def save_fingerprint_image(
    song_path,
    output_path,
    window_size=2048,
    max_freq=3500,
    neighborhood_size=10,
    min_db=-50,
):
    """
    Generate a fingerprint image with:
      - no title
      - no axes
      - no ticks
      - no labels
      - no whitespace
      - only spectrogram + fingerprint dots
    """

    signal_data, sr = librosa.load(song_path, sr=None, mono=True)

    frequencies, times, Sxx = signal.spectrogram(
        signal_data,
        fs=sr,
        nperseg=window_size,
        noverlap=window_size // 2,
        mode="magnitude",
    )

    Sxx_db = 20 * np.log10(Sxx + 1e-10)

    mask = frequencies <= max_freq
    frequencies = frequencies[mask]
    Sxx_db = Sxx_db[mask]

    local_max = maximum_filter(
        Sxx_db,
        size=neighborhood_size,
    )

    peaks = (
        (Sxx_db == local_max)
        & (Sxx_db > min_db)
    )

    y, x = np.where(peaks)

    fig = plt.figure(figsize=(8, 4), frameon=False)
    ax = plt.Axes(fig, [0, 0, 1, 1])
    ax.set_axis_off()
    fig.add_axes(ax)

    ax.imshow(
        Sxx_db,
        origin="lower",
        aspect="auto",
        extent=[
            times[0],
            times[-1],
            frequencies[0],
            frequencies[-1],
        ],
        cmap="magma",
        vmin=-100,
        vmax=0,
    )

    ax.scatter(
        times[x],
        frequencies[y],
        s=8,
        facecolors="none",
        edgecolors="cyan",
        linewidths=0.5,
    )

    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0, max_freq)

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0,
    )

    plt.close(fig)


def main():
    songs = sorted(
        p
        for p in SONGS_DIR.iterdir()
        if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not songs:
        print("No songs found.")
        return

    print(f"Found {len(songs)} songs.\n")

    for song in songs:
        output_file = OUTPUT_DIR / f"{song.stem}.png"

        print(f"Generating {output_file.name}...")

        save_fingerprint_image(
            song,
            output_file,
            window_size=2048,
            max_freq=3500,
            neighborhood_size=10,
            min_db=-50,
        )

    print("\nDone.")


if __name__ == "__main__":
    main()