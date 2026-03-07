"""Audio analysis orchestrator."""

from pathlib import Path
from typing import Any, Dict, Optional


def format_summary(results: Dict[str, Any]) -> str:
    """Format results as human-readable summary.

    Args:
        results: Analysis results.

    Returns:
        Formatted summary string.
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"File: {results['file']}")
    lines.append(f"Duration: {results['duration_seconds']}s")
    lines.append(f"Sample Rate: {results['sample_rate']} Hz")
    lines.append(f"Channels: {results['channels']}")
    lines.append("=" * 60)

    # Loudness
    loudness = results["loudness"]
    lines.append(f"\nLoudness:")
    lines.append(f"  Integrated: {loudness['integrated_lufs']} LUFS")
    lines.append(f"  LRA: {loudness['loudness_range_lra']} LU")
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
    silence = results["silence"]
    lines.append(f"\nSilence: {len(silence)} regions")
    if silence:
        for i, region in enumerate(silence[:5]):
            lines.append(
                f"  {region['start']}s - {region['end']}s ({region['duration']}s)"
            )
        if len(silence) > 5:
            lines.append(f"  +{len(silence) - 5} more")

    # Speaker changes
    speakers = results["speaker_changes"]
    lines.append(f"\nSpeaker Changes: {len(speakers)} detected")
    if speakers:
        for change in speakers[:5]:
            lines.append(
                f"  {change['time']}s (confidence: {round(change['confidence'], 2)})"
            )
        if len(speakers) > 5:
            lines.append(f"  +{len(speakers) - 5} more")

    # Solo regions
    solos = results["solo_regions"]
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
