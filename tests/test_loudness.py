"""Tests for loudness analysis."""

import numpy as np
import pytest
from kautil.audio import analyze_loudness


class TestLoudnessAnalysis:
    """Tests for analyze_loudness function."""

    def test_returns_dict_with_lufs(self):
        """Should return integrated_lufs in result."""
        sample_rate = 44100
        audio = np.zeros(sample_rate)

        result = analyze_loudness(audio, sample_rate)

        assert "integrated_lufs" in result
        assert isinstance(result["integrated_lufs"], float)

    def test_returns_loudness_range(self):
        """Should return loudness_range_lra in result."""
        sample_rate = 44100
        audio = np.zeros(sample_rate)

        result = analyze_loudness(audio, sample_rate)

        assert "loudness_range_lra" in result
        assert isinstance(result["loudness_range_lra"], float)

    def test_returns_moments(self):
        """Should return momentary loudness moments."""
        sample_rate = 44100
        audio = np.zeros(sample_rate)

        result = analyze_loudness(audio, sample_rate)

        assert "moments" in result
        assert isinstance(result["moments"], list)

    def test_returns_loudest_point(self):
        """Should return loudest point with time and lufs."""
        sample_rate = 44100
        audio = np.zeros(sample_rate)

        result = analyze_loudness(audio, sample_rate)

        assert "loudest" in result
        assert "time" in result["loudest"]
        assert "lufs" in result["loudest"]

    def test_returns_softest_point(self):
        """Should return softest point with time and lufs."""
        sample_rate = 44100
        audio = np.zeros(sample_rate)

        result = analyze_loudness(audio, sample_rate)

        assert "softest" in result
        assert "time" in result["softest"]
        assert "lufs" in result["softest"]
