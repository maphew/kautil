# Kautil

Audio analysis CLI toolkit - a drop-in replacement for autil (Audio Utilities).

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
```

## License

MIT License - Copyright 2026 Matt Wilkie
