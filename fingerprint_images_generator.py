from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter


SONGS_DIR = Path("songs")
OUTPUT_DIR = Path("fingerprint_images")

OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
}


def generate_fingerprint_plot(
    song_path,
    window_size=2048,
    max_freq=3500,
    neighborhood_size=10,
    min_db=-50,
):
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

    fig = plt.figure(figsize=(12, 5), frameon=False)
    ax = plt.Axes(fig, [0, 0, 1, 1])
    ax.set_axis_off()
    fig.add_axes(ax)

    ax.imshow(
        Sxx_db,
        origin="lower",
        aspect="auto",
        extent=[times[0], times[-1], frequencies[0], frequencies[-1]],
        cmap="magma",
    )

    ax.scatter(
        times[x],
        frequencies[y],
        s=20,
        facecolors="none",
        edgecolors="cyan",
        linewidths=0.8,
    )

    output_path = OUTPUT_DIR / f"{Path(song_path).stem}.png"

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0,
    )

    plt.close(fig)

    print(f"✓ Saved {output_path.name}")


def main():
    songs = [
        f
        for f in SONGS_DIR.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not songs:
        print("No songs found.")
        return

    print(f"Found {len(songs)} songs.\n")

    for song in songs:
        print(f"Generating fingerprint for {song.name}...")
        generate_fingerprint_plot(song)

    print("\nDone!")


if __name__ == "__main__":
    main()