"""Tests for visualization."""

import numpy as np
import pytest
from pathlib import Path
from kautil.audio import create_visualization


class TestVisualization:
    """Tests for create_visualization function."""

    def test_returns_path(self):
        """Should return path to generated image."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.1
        output_path = Path("test_output.png")

        result = create_visualization(
            audio, sample_rate, output_path, silence=[], speaker_changes=[], loudness={}
        )

        assert isinstance(result, (str, Path))

    def test_creates_file(self):
        """Should create the output PNG file."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.1
        output_path = Path("test_visualization.png")

        # Clean up if exists
        if output_path.exists():
            output_path.unlink()

        result = create_visualization(
            audio, sample_rate, output_path, silence=[], speaker_changes=[], loudness={}
        )

        assert output_path.exists()

    def test_accepts_metadata(self):
        """Should accept silence, speaker_changes, and loudness data."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.1
        output_path = Path("test_viz_with_data.png")

        silence = [{"start": 0.0, "end": 1.0, "duration": 1.0}]
        speaker_changes = [{"time": 1.5, "confidence": 0.8, "type": "amplitude_change"}]
        loudness = {
            "moments": [{"time": 0.0, "lufs": -20.0}],
            "loudest": {"time": 1.0, "lufs": -10.0},
            "softest": {"time": 0.5, "lufs": -30.0},
        }

        result = create_visualization(
            audio,
            sample_rate,
            output_path,
            silence=silence,
            speaker_changes=speaker_changes,
            loudness=loudness,
        )

        assert isinstance(result, (str, Path))
