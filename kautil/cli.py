"""CLI entry point for kautil."""

import click
import sys
from pathlib import Path


@click.group()
@click.version_option()
def main():
    """Kautil - Audio analysis CLI toolkit."""
    pass


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory (default: input dir)",
)
@click.option(
    "--silence-threshold", type=float, default=-40.0, help="Silence threshold in dB"
)
@click.option(
    "--sensitivity", type=float, default=0.5, help="Detection sensitivity 0.0-1.0"
)
@click.option("--json-only", is_flag=True, help="Skip visualization image")
@click.option("--json", "-j", type=click.Path(), help="Custom JSON output path")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def fingerprint(
    file, output_dir, silence_threshold, sensitivity, json_only, json, verbose
):
    """Generate audio fingerprint with analysis and visualization."""
    click.echo(f"Processing: {file}")
    click.echo(f"Silence threshold: {silence_threshold} dB")
    click.echo(f"Sensitivity: {sensitivity}")
    # TODO: Implement fingerprint analysis
    click.echo("Fingerprint generation not yet implemented.")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def info(file, verbose):
    """Show audio file information."""
    click.echo(f"File: {file}")
    # TODO: Implement info command
    click.echo("Info command not yet implemented.")


if __name__ == "__main__":
    main()
