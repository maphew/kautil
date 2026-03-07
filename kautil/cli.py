"""CLI entry point for kautil."""

import sys
from pathlib import Path

import click
import numpy as np
import soundfile as sf

from kautil import analyzer


@click.group(invoke_without_command=True)
@click.option("--help", is_flag=True, help="Show full help including all subcommands.")
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx, help):
    """Kautil - Audio analysis CLI toolkit."""
    if ctx.invoked_subcommand is None or help:
        click.echo(ctx.get_help())
        click.echo("\nCommands:")
        for name, cmd in ctx.command.commands.items():
            cmd_ctx = click.Context(cmd, info_name=name)
            click.echo(f"\n{name}:")
            click.echo(cmd_ctx.get_help())
        ctx.exit()


def load_audio(file_path):
    """Load audio file and return data and sample rate.

    Tries soundfile first, falls back to audioread+ffmpeg on failure.
    """
    try:
        audio_data, sample_rate = sf.read(file_path, dtype="float32")
        return audio_data, sample_rate
    except sf.SoundFileError:
        import audioread

        with audioread.audio_open(file_path) as f:
            sample_rate = f.samplerate
            channels = f.channels
            chunks = []
            for chunk in f:
                if chunk.dtype == np.int16:
                    int_data = np.frombuffer(chunk, dtype=np.int16)
                    float_data = int_data.astype(np.float32) / 32768.0
                elif chunk.dtype == np.int8:
                    int_data = np.frombuffer(chunk, dtype=np.int8)
                    float_data = int_data.astype(np.float32) / 128.0
                elif chunk.dtype == np.int32:
                    int_data = np.frombuffer(chunk, dtype=np.int32)
                    float_data = int_data.astype(np.float32) / 2147483648.0
                elif chunk.dtype == np.float32:
                    float_data = np.frombuffer(chunk, dtype=np.float32)
                else:
                    int_data = np.frombuffer(chunk, dtype=np.int16)
                    float_data = int_data.astype(np.float32) / 32768.0
                chunks.append(float_data)

        audio = np.concatenate(chunks)

        if channels > 1:
            audio = audio.reshape((-1, channels))

        return audio, sample_rate


def get_audio_info(file_path, audio_data, sample_rate):
    """Extract basic audio file info.

    Tries soundfile first, falls back to calculated values from audio data.
    """
    try:
        info = sf.info(file_path)
        return {
            "duration_seconds": info.duration,
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "codec": info.format,
            "frames": info.frames,
        }
    except sf.SoundFileError:
        duration = len(audio_data) / sample_rate if sample_rate > 0 else 0
        channels = audio_data.shape[1] if audio_data.ndim > 1 else 1
        return {
            "duration_seconds": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "codec": "unknown",
            "frames": len(audio_data) if audio_data.ndim == 1 else audio_data.shape[0],
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

    if output_dir is None:
        output_dir = file_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    if json_path:
        json_path = Path(json_path)
    else:
        json_path = output_dir / f"{file_path.stem}_fingerprint.json"

    results = analyzer.analyze_audio(
        str(file_path),
        silence_threshold_db=silence_threshold,
        sensitivity=sensitivity,
        create_viz=not json_only,
        output_dir=str(output_dir) if output_dir != file_path.parent else None,
    )

    analyzer.save_results(results, str(json_path))

    if verbose:
        click.echo(f"JSON saved to: {json_path}")

    click.echo(analyzer.format_summary(results))


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
