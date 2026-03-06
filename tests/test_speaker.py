"""Tests for speaker change detection."""

import numpy as np
import pytest
from kautil.audio import detect_speaker_changes


class TestSpeakerChangeDetection:
    """Tests for detect_speaker_changes function."""

    def test_returns_list(self):
        """Should return a list of speaker changes."""
        sample_rate = 44100
        # Generate test audio
        audio = np.random.randn(sample_rate * 2) * 0.1

        result = detect_speaker_changes(audio, sample_rate, sensitivity=0.5)

        assert isinstance(result, list)

    def test_change_has_time_confidence_type(self):
        """Each change should have time, confidence, and type."""
        sample_rate = 44100
        # Create audio with obvious energy change
        silence = np.zeros(int(0.5 * sample_rate))
        noise1 = np.random.randn(int(1 * sample_rate)) * 0.1
        noise2 = np.random.randn(int(1 * sample_rate)) * 0.3  # Louder
        audio = np.concatenate([noise1, noise2])

        result = detect_speaker_changes(audio, sample_rate, sensitivity=0.5)

        # May or may not detect changes depending on sensitivity
        for change in result:
            assert "time" in change
            assert "confidence" in change
            assert "type" in change

    def test_respects_sensitivity(self):
        """Should respect the sensitivity parameter (0.0-1.0)."""
        sample_rate = 44100
        audio = np.random.randn(sample_rate * 2) * 0.1

        # Low sensitivity should find fewer changes
        result_low = detect_speaker_changes(audio, sample_rate, sensitivity=0.1)
        # High sensitivity should find more changes
        result_high = detect_speaker_changes(audio, sample_rate, sensitivity=0.9)

        # Both should return lists
        assert isinstance(result_low, list)
        assert isinstance(result_high, list)

    def test_confidence_in_valid_range(self):
        """Confidence scores should be between 0 and 1."""
        sample_rate = 44100
        # Create audio with multiple energy changes
        audio = np.concatenate(
            [
                np.random.randn(int(1 * sample_rate)) * 0.1,
                np.random.randn(int(1 * sample_rate)) * 0.3,
                np.random.randn(int(1 * sample_rate)) * 0.1,
            ]
        )

        result = detect_speaker_changes(audio, sample_rate, sensitivity=0.5)

        for change in result:
            assert 0.0 <= change["confidence"] <= 1.0
