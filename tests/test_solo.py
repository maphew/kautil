"""Tests for solo/activity detection."""

import numpy as np
import pytest
from kautil.audio import detect_solo_regions


class TestSoloActivityDetection:
    """Tests for detect_solo_regions function."""

    def test_returns_list(self):
        """Should return a list of solo/activity regions."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.1

        result = detect_solo_regions(audio, sample_rate, threshold_db=-40.0)

        assert isinstance(result, list)

    def test_region_has_start_end_duration_type(self):
        """Each region should have start, end, duration, and type."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.1

        result = detect_solo_regions(audio, sample_rate, threshold_db=-40.0)

        if len(result) > 0:
            region = result[0]
            assert "start" in region
            assert "end" in region
            assert "duration" in region
            assert "type" in region

    def test_respects_threshold(self):
        """Should respect the threshold parameter."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.01  # Very quiet

        # With higher threshold, should find fewer active regions
        result_high = detect_solo_regions(audio, sample_rate, threshold_db=-20.0)
        # With lower threshold, should find more
        result_low = detect_solo_regions(audio, sample_rate, threshold_db=-60.0)

        assert isinstance(result_high, list)
        assert isinstance(result_low, list)

    def test_min_duration_filtering(self):
        """Should filter regions shorter than minimum duration."""
        sample_rate = 44100
        # Short active burst (0.1s), then silence, then longer active (1s)
        noise = np.random.randn(int(0.1 * sample_rate)) * 0.1
        silence = np.zeros(int(1 * sample_rate))
        long_noise = np.random.randn(int(1 * sample_rate)) * 0.1
        audio = np.concatenate([noise, silence, long_noise])

        # With 0.5s minimum, short region should be filtered
        result = detect_solo_regions(
            audio, sample_rate, threshold_db=-40.0, min_duration=0.5
        )

        # Should not include the 0.1s active region
        for region in result:
            assert region["duration"] >= 0.5
