# Kli Audio Utilies

kautil — A clone of the 'autil' utility written by Kilocode CLI.

From the information on Autil below, **write a complete drop in replacement**.

Use red-green TDD.
Manage dependencies with `uv`.
`gh` cli is installed for Github tasks.
Use `uvx` to run tools which aren't available in the system's PATH. (Record when this happens.)
Use `bd` (beads) for issue tracking. Run `bd onboard` to get started.
Sign your commits as Kilocode cli and note which mode and model was used.

Expected usage patterns:

```
# run from source
git clone https://github.com/maphew/kautil.git
cd kautil
uv run kautil <command> [options] <file>

# run from pypi without installing
uvx kautil <command> [options] <file>

# install and run
uv tool install kautil
kautil <command> [options] <file>
```

Copyright 2026 Matt Wilkie <maphew@gmail.com> MIT License

-----------------------------------------------------------------------

## Autil

`autil` Audio Utilities is a CLI-first audio analysis toolkit. It produces an audio "fingerprint" — a JSON report and PNG visualization — containing loudness analysis, silence detection, speaker-change detection, and solo/activity region detection.

### Usage

```
autil <command> [options] <file>

autil fingerprint "samples/Carl Sagan - Commencement Address 1990.mp3"
autil info "samples/Mussorgsky - Night on Bald Mountain (Skidmore College Orchestra).mp3"
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output-dir, -o` | `Optional[str]` | None (=input dir) | Output directory |
| `--silence-threshold` | `float` | -40.0 | Silence threshold in dB |
| `--sensitivity` | `float` | 0.5 | Detection sensitivity 0.0-1.0 |
| `--json-only` | `bool` | False | Skip visualization image |
| `--json, -j` | `Optional[str]` | None | Custom JSON output path |
| `--verbose, -v` | `bool` | False | Show detailed output |

### Features

- **Loudness Analysis (ITU-R BS.1770-4)**
  - Integrated loudness (LUFS)
  - Loudness range (LRA)
  - Momentary loudness over time
  - Loudest and softest points

- **Silence Detection**
  - Configurable threshold and minimum duration
  - Returns start, end, and duration of each region

- **Speaker Change Detection**
  - Energy-based change detection
  - Confidence scores for each change

- **Solo/Activity Detection**
  - Identifies active regions above threshold
  - Minimum duration filtering

- **Visualization**
  - Waveform with silence and speaker change overlays
  - Mel spectrogram
  - Loudness graph with loudest/softest markers

### Example Output

#### JSON Structure

```json
{
  "file": "/path/to/audio.mp3",
  "duration_seconds": 180.5,
  "sample_rate": 44100,
  "channels": 2,
  "codec": "MP3",
  "loudness": {
    "integrated_lufs": -20.5,
    "loudness_range_lra": 12.3,
    "moments": [
      {"time": 0.0, "lufs": -25.1},
      {"time": 1.0, "lufs": -22.3}
    ],
    "loudest": {"time": 45.2, "lufs": -10.5},
    "softest": {"time": 120.0, "lufs": -45.2}
  },
  "silence": [
    {"start": 0.0, "end": 2.5, "duration": 2.5}
  ],
  "speaker_changes": [
    {"time": 30.5, "confidence": 0.85, "type": "amplitude_change"}
  ],
  "solo_regions": [
    {"start": 5.0, "end": 15.2, "duration": 10.2, "type": "possible_solo"}
  ],
  "visualization": "/path/to/audio_fingerprint.png"
}
```

### Dependencies

- ffmpeg — required for audio decoding
- libsndfile — required by the soundfile Python package
