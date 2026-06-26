import numpy as np
import librosa
import soundfile as sf

# Input/output files
input_file = "songs/Never Gonna Give You Up.mp3"
output_file = "songs/noisy.mp3"

# Load audio
audio, sr = librosa.load(input_file, sr=None, mono=True)

# Noise level (increase for more noise)
noise_std = 0.02

# Generate Gaussian noise
noise = np.random.normal(0, noise_std, len(audio))

# Add noise
noisy_audio = audio + noise

# Prevent clipping
noisy_audio = np.clip(noisy_audio, -1.0, 1.0)

# Save
sf.write(output_file, noisy_audio, sr)

print(f"Saved noisy audio to {output_file}")