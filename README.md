# Kautil

Audio analysis CLI toolkit - a drop-in replacement for autil (Audio Utilities) written from ground up using Kilocode CLI.

> **autil** (Audio Utilities) is a CLI-first audio analysis toolkit. It produces an audio "fingerprint" — a JSON report and PNG visualization — containing loudness analysis, silence detection, speaker-change detection, and solo/activity region detection.

## Installation

```bash
# Run from source
git clone https://github.com/maphew/kautil.git
cd kautil
uv run kautil <command> [options] <file>

# Run without installing
uvx kautil <command> [options] <file>

# Install and run
uv tool install kautil
kautil <command> [options] <file>
```

## Usage

```bash
kautil fingerprint "audio.mp3"
kautil info "audio.mp3"

kautil --help
Usage: kautil [OPTIONS] COMMAND [ARGS]...

  Kautil - Audio analysis CLI toolkit.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  fingerprint  Generate audio fingerprint with analysis and visualization.
  info         Show audio file information.

Commands:

fingerprint:
Usage: fingerprint [OPTIONS] FILE

  Generate audio fingerprint with analysis and visualization.

Options:
  -o, --output-dir PATH      Output directory (default: input dir)
  --silence-threshold FLOAT  Silence threshold in dB
  --sensitivity FLOAT        Detection sensitivity 0.0-1.0
  --json-only                Skip visualization image
  -j, --json-path PATH       Custom JSON output path
  -v, --verbose              Show detailed output
  --help                     Show this message and exit.
```

## Sample output

Pop music:
![Carsie Blanton sample](samples/Smoke%20Alarm%20-%20Carsie%20Blanton_fingerprint.png)

Classical music:
![Night on Bald Mtn sample](samples/Mussorgsky%20-%20Night%20on%20Bald%20Mountain%20(Skidmore%20College%20Orchestra)_fingerprint.png)

Spoken word:
![Carl Sagan sample](samples/Carl%20Sagan%20-%20Commencement%20Address%201990_fingerprint.png)

```json
{
  "file": "samples\\test.wav",
  "duration_seconds": 2.0,
  "sample_rate": 44100,
  "channels": 1,
  "codec": "WAV",
  "loudness": {
    "integrated_lufs": -16.326465691686668,
    "loudness_range_lra": 0.1881371139571435,
    "moments": [
      {
        "time": 0.0,
        "lufs": -23.740039825439453
      },
      {
        "time": 1.0,
        "lufs": -14.171149253845215
      }
    ],
    "loudest": {
      "time": 1.0,
      "lufs": -14.171149253845215
    },
    "softest": {
      "time": 0.0,
      "lufs": -23.740039825439453
    }
  },
  "silence": [],
  "speaker_changes": [
    {
      "time": 0.9745578231292517,
      "confidence": 0.8003793358802795,
      "type": "amplitude_change"
    }
  ],
  "solo_regions": [
    {
      "start": 0.0,
      "end": 1.9954875283446711,
      "duration": 1.9954875283446711,
      "type": "possible_solo"
    }
  ]
}
```

## License

MIT License - Copyright 2026 Matt Wilkie
