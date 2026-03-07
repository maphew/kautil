"""Audio analysis orchestrator."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import soundfile as sf

from kautil.audio import (
    analyze_loudness,
    detect_silence,
    detect_speaker_changes,
    detect_solo_regions,
    create_visualization,
)


def load_audio(file_path):
    """Load audio file and return data and sample rate."""
    audio_data, sample_rate = sf.read(file_path, dtype="float32")
    return audio_data, sample_rate


def get_audio_info(file_path, audio_data, sample_rate):
    """Extract basic audio file info."""
    info = sf.info(file_path)
    return {
        "duration_seconds": info.duration,
        "sample_rate": info.samplerate,
        "channels": info.channels,
        "codec": info.format,
        "frames": info.frames,
    }


def analyze_audio(
    file_path: str,
    silence_threshold_db: float = -40.0,
    sensitivity: float = 0.5,
    create_viz: bool = True,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Analyze audio file and produce fingerprint.

    Args:
        file_path: Path to audio file.
        silence_threshold_db: Silence threshold in dB.
        sensitivity: Detection sensitivity (0.0-1.0).
        create_viz: Whether to create visualization.
        output_dir: Output directory for visualization (default: input directory).

    Returns:
        Dict with analysis results.
    """
    file_path = Path(file_path)

    audio_data, sample_rate = load_audio(str(file_path))

    audio_info = get_audio_info(str(file_path), audio_data, sample_rate)

    loudness = analyze_loudness(audio_data, sample_rate)

    silence = detect_silence(audio_data, sample_rate, threshold_db=silence_threshold_db)

    speaker_changes = detect_speaker_changes(
        audio_data, sample_rate, sensitivity=sensitivity
    )

    solo_regions = detect_solo_regions(
        audio_data, sample_rate, threshold_db=silence_threshold_db
    )

    result = {
        "file": str(file_path),
        **audio_info,
        "loudness": loudness,
        "silence": silence,
        "speaker_changes": speaker_changes,
        "solo_regions": solo_regions,
    }

    if create_viz:
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = file_path.parent

        viz_path = output_path / f"{file_path.stem}_fingerprint.png"
        create_visualization(
            audio_data,
            sample_rate,
            str(viz_path),
            silence=silence,
            speaker_changes=speaker_changes,
            loudness=loudness,
        )
        result["visualization"] = str(viz_path)

    return result


def save_results(results: Dict[str, Any], output_path: str) -> None:
    """Save results to JSON file.

    Args:
        results: Analysis results.
        output_path: Path to save JSON.
    """

    def convert(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        return obj

    results = convert(results)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


def format_summary(results: Dict[str, Any]) -> str:
    """Format results as human-readable summary.

    Args:
        results: Analysis results.

    Returns:
        Formatted summary string.
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"File: {results.get('file', 'Unknown')}")
    lines.append(f"Duration: {results.get('duration_seconds', 0)}s")
    lines.append(f"Sample Rate: {results.get('sample_rate', 0)} Hz")
    lines.append(f"Channels: {results.get('channels', 0)}")
    lines.append("=" * 60)

    # Loudness
    loudness = results.get("loudness", {})
    lines.append(f"\nLoudness:")
    lines.append(f"  Integrated: {loudness.get('integrated_lufs', 0)} LUFS")
    lines.append(f"  LRA: {loudness.get('loudness_range_lra', 0)} LU")
    if loudness.get("loudest") and loudness["loudest"].get(
        "lufs", -float("inf")
    ) != -float("inf"):
        lines.append(
            f"  Loudest: {loudness['loudest']['lufs']} LUFS at {loudness['loudest']['time']}s"
        )
    if loudness.get("softest") and loudness["softest"].get(
        "lufs", -float("inf")
    ) != -float("inf"):
        lines.append(
            f"  Softest: {loudness['softest']['lufs']} LUFS at {loudness['softest']['time']}s"
        )

    # Silence
    silence = results.get("silence", [])
    lines.append(f"\nSilence: {len(silence)} regions")
    if silence:
        for i, region in enumerate(silence[:5]):
            lines.append(
                f"  {region['start']}s - {region['end']}s ({region['duration']}s)"
            )
        if len(silence) > 5:
            lines.append(f"  +{len(silence) - 5} more")

    # Speaker changes
    speakers = results.get("speaker_changes", [])
    lines.append(f"\nSpeaker Changes: {len(speakers)} detected")
    if speakers:
        for change in speakers[:5]:
            lines.append(
                f"  {change['time']}s (confidence: {round(change['confidence'], 2)})"
            )
        if len(speakers) > 5:
            lines.append(f"  +{len(speakers) - 5} more")

    # Solo regions
    solos = results.get("solo_regions", [])
    lines.append(f"\nActivity/Solo Regions: {len(solos)} detected")
    if solos:
        for region in solos[:5]:
            lines.append(
                f"  {region['start']}s - {region['end']}s ({region['duration']}s)"
            )
        if len(solos) > 5:
            lines.append(f"  +{len(solos) - 5} more")

    # Visualization
    if results.get("visualization"):
        lines.append(f"\nVisualization: {results['visualization']}")

    lines.append("=" * 60)

    return "\n".join(lines)
