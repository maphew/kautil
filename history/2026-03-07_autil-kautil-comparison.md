# Dev Log: autil to kautil Feature Comparison

**Date:** 2026-03-08  
**Author:** matt wilkie (kilo-auto/free)  
**Activity:** Compared autil and kautil projects to identify features to bring from autil to kautil

## Context

Both autil (Audio Utilities) and kautil are CLI audio analysis toolkits written by Matt Wilkie. kautil was created as a "drop-in replacement" for autil. The goal is to eventually collapse them together and only take the best ideas forward.

## Exploration Summary

### Project Structures

**autil** (original):
```
autil/
├── autil/
│   ├── __init__.py
│   ├── cli.py          (Typer + Rich)
│   ├── analyzer.py     (orchestrator)
│   ├── audio_loader.py (dual-backend: soundfile + audioread)
│   ├── loudness.py
│   ├── silence.py
│   ├── segments.py
│   └── viz.py
├── tests/
│   ├── conftest.py    (pytest fixtures)
│   └── ...
└── samples/
```

**kautil** (clone/replacement):
```
kautil/
├── kautil/
│   ├── __init__.py
│   ├── cli.py        (Click - all logic here)
│   └── audio.py      (all analysis functions)
├── tests/
│   └── ... (no conftest.py)
└── samples/
```

### Key Findings

1. **Dual-backend audio loading** - autil has fallback to audioread for MP3/OGG/WebM, kautil only uses soundfile
2. **CLI framework** - autil uses Typer + Rich for pretty output, kautil uses basic Click
3. **Code organization** - autil has separate modules (analyzer.py, audio_loader.py, etc.), kautil has everything in two files
4. **Human-readable output** - autil has `format_summary()` for nice terminal reports
5. **Test fixtures** - autil has conftest.py with reusable test audio fixtures
6. **Speaker detection** - autil uses two-stage verification, kautil uses single threshold
7. **Silence detection** - autil uses relative dB (to max RMS), kautil uses absolute dB

## Issues Created

| ID | Priority | Title |
|----|----------|-------|
| kautil-egb | P1 | Add audioread fallback for audio loading |
| kautil-9xn | P2 | Add two-stage speaker change verification |
| kautil-0ng | P2 | Add format_summary() for human-readable output |
| kautil-hjk | P2 | Extract orchestrator module (analyzer.py) |
| kautil-rpv | P3 | Add relative silence threshold |
| kautil-30r | P3 | Add test fixtures (conftest.py) |
| kautil-ang | P4 | Add frames to info output |

## Files Examined

- `../autil/autil/__init__.py`
- `../autil/autil/cli.py`
- `../autil/autil/analyzer.py`
- `../autil/autil/audio_loader.py`
- `../autil/autil/segments.py`
- `../autil/autil/viz.py`
- `../autil/autil/silence.py`
- `../autil/autil/loudness.py`
- `../autil/tests/conftest.py`
- `A:/dev/kautil/kautil/cli.py`
- `A:/dev/kautil/kautil/audio.py`
- `A:/dev/kautil/pyproject.toml`

## Recommendations

The highest priority items to bring over:
1. **Audioread fallback** - biggest functional gap, enables more audio formats
2. **Orchestrator module** - cleaner architecture, better testability
3. **format_summary()** - significantly improves user experience

These are tracked as bd issues and ready to be worked on.
