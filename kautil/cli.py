"""CLI entry point for kautil."""

import json
import sys
from pathlib import Path

import click
import soundfile as sf

from kautil.audio import (
    analyze_loudness,
    detect_silence,
    detect_speaker_changes,
    detect_solo_regions,
    create_visualization,
)


@click.group(invoke_without_command=True)
@click.option("--help", is_flag=True, help="Show full help including all subcommands.")
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx, help):
    """Kautil - Audio analysis CLI toolkit."""
    # Show full help when no subcommand is given OR when --help is passed
    if ctx.invoked_subcommand is None or help:
        # Print main group help
        click.echo(ctx.get_help())
        click.echo("\nCommands:")
        # Get all registered commands and show their full help
        for name, cmd in ctx.command.commands.items():
            # Create a fresh context for each command
            cmd_ctx = click.Context(cmd, info_name=name)
            # Print the formatted help for this command
            click.echo(f"\n{name}:")
            click.echo(cmd_ctx.get_help())
        ctx.exit()


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


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory (default: input dir)",
)
@click.option(
    "--silence-threshold",
    type=float,
    default=-40.0,
    help="Silence threshold in dB",
)
@click.option(
    "--sensitivity", type=float, default=0.5, help="Detection sensitivity 0.0-1.0"
)
@click.option("--json-only", is_flag=True, help="Skip visualization image")
@click.option("--json-path", "-j", type=click.Path(), help="Custom JSON output path")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def fingerprint(
    file, output_dir, silence_threshold, sensitivity, json_only, json_path, verbose
):
    """Generate audio fingerprint with analysis and visualization."""
    file_path = Path(file)

    if verbose:
        click.echo(f"Processing: {file}")
        click.echo(f"Silence threshold: {silence_threshold} dB")
        click.echo(f"Sensitivity: {sensitivity}")

    # Load audio
    if verbose:
        click.echo("Loading audio...")
    audio_data, sample_rate = load_audio(file_path)

    # Determine output directory
    if output_dir is None:
        output_dir = file_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Run analysis
    if verbose:
        click.echo("Analyzing loudness...")
    loudness = analyze_loudness(audio_data, sample_rate)

    if verbose:
        click.echo("Detecting silence...")
    silence = detect_silence(audio_data, sample_rate, threshold_db=silence_threshold)

    if verbose:
        click.echo("Detecting speaker changes...")
    speaker_changes = detect_speaker_changes(
        audio_data, sample_rate, sensitivity=sensitivity
    )

    if verbose:
        click.echo("Detecting solo/activity regions...")
    solo_regions = detect_solo_regions(
        audio_data, sample_rate, threshold_db=silence_threshold
    )

    # Build result
    audio_info = get_audio_info(file_path, audio_data, sample_rate)

    result = {
        "file": str(file_path),
        **audio_info,
        "loudness": loudness,
        "silence": silence,
        "speaker_changes": speaker_changes,
        "solo_regions": solo_regions,
    }

    # Save JSON
    if json_path:
        json_path = Path(json_path)
    else:
        json_path = output_dir / f"{file_path.stem}_fingerprint.json"

    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    if verbose:
        click.echo(f"JSON saved to: {json_path}")

    # Create visualization
    if not json_only:
        if verbose:
            click.echo("Creating visualization...")
        viz_path = output_dir / f"{file_path.stem}_fingerprint.png"
        create_visualization(
            audio_data,
            sample_rate,
            viz_path,
            silence=silence,
            speaker_changes=speaker_changes,
            loudness=loudness,
        )
        result["visualization"] = str(viz_path)

        if verbose:
            click.echo(f"Visualization saved to: {viz_path}")

    # Print summary
    click.echo(f"\nFingerprint generated successfully!")
    click.echo(f"  Integrated loudness: {loudness['integrated_lufs']:.1f} LUFS")
    click.echo(f"  Loudness range: {loudness['loudness_range_lra']:.1f} LU")
    click.echo(f"  Silence regions: {len(silence)}")
    click.echo(f"  Speaker changes: {len(speaker_changes)}")
    click.echo(f"  Solo/active regions: {len(solo_regions)}")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def info(file, verbose):
    """Show audio file information."""
    file_path = Path(file)

    if verbose:
        click.echo(f"Reading: {file}")

    audio_data, sample_rate = load_audio(file_path)
    audio_info = get_audio_info(file_path, audio_data, sample_rate)

    click.echo(f"File: {file}")
    click.echo(f"Duration: {audio_info['duration_seconds']:.2f} seconds")
    click.echo(f"Sample rate: {audio_info['sample_rate']} Hz")
    click.echo(f"Channels: {audio_info['channels']}")
    click.echo(f"Codec: {audio_info['codec']}")


if __name__ == "__main__":
    main()
