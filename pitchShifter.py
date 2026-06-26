import librosa
import soundfile as sf

# Input/output files
input_file = "songs/Never Gonna Give You Up.mp3"
output_file = "songs/pitchy.mp3"

# Load audio
audio, sr = librosa.load(input_file, sr=None, mono=True)

# Pitch shift in semitones
# Positive = higher pitch
# Negative = lower pitch
n_steps = 2

# Shift pitch
shifted_audio = librosa.effects.pitch_shift(
    audio,
    sr=sr,
    n_steps=n_steps
)

# Save
sf.write(output_file, shifted_audio, sr)

print(f"Saved pitch-shifted audio to {output_file}")