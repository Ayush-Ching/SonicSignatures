import argparse
import librosa
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import signal
from scipy.ndimage import maximum_filter


def plot_dft(song_path, db=False, output_file=None):
    if not db:
        print("Plotting DFT...")
    else:
        print("Plotting DFT in dB scale...")

    signal, sr = librosa.load(song_path, sr=None, mono=True)
    song_name = Path(song_path).stem

    X = np.fft.fft(signal)
    magnitude = np.abs(X)

    freq = np.fft.fftfreq(len(signal), d=1 / sr)
    half = len(signal) // 2

    plt.figure(figsize=(12, 5))

    if db:
        magnitude = 20 * np.log10(magnitude[:half] + 1e-10)
        plt.ylabel("Magnitude (dB)")
        plt.title(f"DFT Magnitude Spectrum (in dB) of {song_name}")
    else:
        magnitude = magnitude[:half]
        plt.ylabel("Magnitude")
        plt.title(f"DFT Magnitude Spectrum of {song_name}")

    plt.plot(freq[:half], magnitude)
    plt.xlabel("Frequency (Hz)")
    plt.grid(True)
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Saved plot to '{output_file}'")
    else:
        plt.show()

    plt.close()


def plot_spectrogram(song_path, window_size=20000, max_freq=3500, output_file=None):
    print("Plotting spectrogram...")

    signal, sr = librosa.load(song_path, sr=None, mono=True)
    song_name = Path(song_path).stem

    plt.figure(figsize=(12, 5))

    plt.specgram(
        signal,
        NFFT=window_size,
        Fs=sr,
        noverlap=window_size // 2,  # 50% overlap
        cmap="magma"
    )

    plt.ylim(0, max_freq)

    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title(f"Spectrogram of {song_name}\nWindow Size = {window_size}")
    plt.colorbar(label="Intensity (dB)")
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Saved plot to '{output_file}'")
    else:
        plt.show()

    plt.close()


def plot_fingerprint(song_path, window_size=20000, max_freq=3500, neighborhood_size=15, min_db=-40, output_file=None):

    print("Generating fingerprint...")

    signal_data, sr = librosa.load(song_path, sr=None, mono=True)
    song_name = Path(song_path).stem

    frequencies, times, Sxx = signal.spectrogram(
        signal_data,
        fs=sr,
        nperseg=window_size,
        noverlap=window_size // 2,
        mode="magnitude"
    )

    Sxx_db = 20 * np.log10(Sxx + 1e-10)

    mask = frequencies <= max_freq
    frequencies = frequencies[mask]
    Sxx_db = Sxx_db[mask]

    local_max = maximum_filter(
        Sxx_db,
        size=neighborhood_size
    )

    peaks = (
        (Sxx_db == local_max) &
        (Sxx_db > min_db)
    )

    y, x = np.where(peaks)

    plt.figure(figsize=(12, 5))

    plt.imshow(
        Sxx_db,
        origin="lower",
        aspect="auto",
        extent=[times[0], times[-1], frequencies[0], frequencies[-1]],
        cmap="magma"
    )

    plt.scatter(
        times[x],
        frequencies[y],
        s=20,
        facecolors="none",
        edgecolors="cyan",
        linewidths=0.8
    )

    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title(f"Audio Fingerprint of {song_name}")
    plt.colorbar(label="Intensity (dB)")
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Saved plot to '{output_file}'")
    else:
        plt.show()

    plt.close()



def main():
    parser = argparse.ArgumentParser(description="Audio Fingerprint stuff")

    parser.add_argument(
        "song_file_path",
        help="Path to the MP3 (or other supported audio) file."
    )

    parser.add_argument(
        "--dft",
        action="store_true",
        help="Plot the DFT magnitude spectrum."
    )

    parser.add_argument(
        "--dft_db",
        action="store_true",
        help="Plot the DFT magnitude spectrum in decibels."
    )

    parser.add_argument(
        "--spectrogram", "--spgm",
        dest="spectrogram",
        action="store_true",
        help="Plot a spectrogram of the song."
    )

    parser.add_argument(
        "--window",
        type=int,
        default=2048,
        metavar="N",
        help="Spectrogram window size (NFFT). Default: 2048."
    )

    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save the generated plot to a PNG file instead of displaying it."
    )

    parser.add_argument(
        "--max_freq",
        type=float,
        default=3500,
        metavar="FREQ",
        help="Maximum frequency (Hz) shown in the spectrogram. Default: 3500."
    )

    parser.add_argument(
        "--fingerprint",
        action="store_true",
        help="Plot the spectrogram with local spectral peaks (audio fingerprint)."
    )

    parser.add_argument(
        "--neighborhood",
        type=int,
        default=15,
        metavar="N",
        help="Neighborhood size used for local peak detection. Larger values produce fewer peaks. Default: 15."
    )

    parser.add_argument(
        "--min_db",
        type=float,
        default=-40,
        metavar="DB",
        help="Minimum peak magnitude (dB) for the fingerprint. Higher values produce fewer peaks. Default: -40."
    )

    args = parser.parse_args()

    selected = sum([
        args.dft,
        args.dft_db,
        args.spectrogram,
        args.fingerprint
    ])

    if selected > 1:
        parser.error("Choose only one of --dft, --dft_db, or --spectrogram.")

    if args.dft:
        plot_dft(
            args.song_file_path,
            db=False,
            output_file=args.output
        )
    elif args.dft_db:
        plot_dft(
            args.song_file_path,
            db=True,
            output_file=args.output
        )
    elif args.spectrogram:
        plot_spectrogram(
            args.song_file_path,
            window_size=args.window,
            max_freq=args.max_freq,
            output_file=args.output
        )
    elif args.fingerprint:
        plot_fingerprint(
            args.song_file_path,
            window_size=args.window,
            max_freq=args.max_freq,
            neighborhood_size=args.neighborhood,
            min_db=args.min_db,
            output_file=args.output
        )


if __name__ == "__main__":
    main()