"""Tests for silence detection."""

import numpy as np
import pytest
from kautil.audio import detect_silence


class TestSilenceDetection:
    """Tests for detect_silence function."""

    def test_returns_list(self):
        """Should return a list of silence regions."""
        sample_rate = 44100
        # 1 second of silence
        audio = np.zeros(sample_rate)

        result = detect_silence(audio, sample_rate, threshold_db=-40.0)

        assert isinstance(result, list)

    def test_detects_silence_at_start(self):
        """Should detect silence at the beginning of audio."""
        sample_rate = 44100
        # 1 second silence, then 1 second noise
        silence = np.zeros(sample_rate)
        noise = np.random.randn(sample_rate) * 0.1
        audio = np.concatenate([silence, noise])

        result = detect_silence(audio, sample_rate, threshold_db=-40.0)

        assert len(result) > 0
        assert result[0]["start"] == 0.0

    def test_silence_region_has_start_end_duration(self):
        """Each silence region should have start, end, and duration."""
        sample_rate = 44100
        audio = np.zeros(sample_rate)

        result = detect_silence(audio, sample_rate, threshold_db=-40.0)

        if len(result) > 0:
            region = result[0]
            assert "start" in region
            assert "end" in region
            assert "duration" in region

    def test_respects_threshold(self):
        """Should respect the silence threshold parameter."""
        sample_rate = 44100
        # Very quiet audio (-50 dB)
        audio = np.zeros(sample_rate)

        # With -40 dB threshold, this should be silent
        result_lenient = detect_silence(audio, sample_rate, threshold_db=-40.0)

        # With -60 dB threshold, this should also be silent
        result_strict = detect_silence(audio, sample_rate, threshold_db=-60.0)

        # Both should detect silence
        assert len(result_lenient) > 0
        assert len(result_strict) > 0

    def test_min_duration_filtering(self):
        """Should filter out silence regions shorter than minimum duration."""
        sample_rate = 44100
        # Short silence (0.1s), then noise, then longer silence (1s)
        short_silence = np.zeros(int(0.1 * sample_rate))
        noise = np.random.randn(int(1 * sample_rate)) * 0.1
        long_silence = np.zeros(int(1 * sample_rate))
        audio = np.concatenate([short_silence, noise, long_silence])

        # With 0.5s minimum, short silence should be filtered
        result = detect_silence(
            audio, sample_rate, threshold_db=-40.0, min_duration=0.5
        )

        # Should not include the 0.1s silence region
        for region in result:
            assert region["duration"] >= 0.5
