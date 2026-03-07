"""Pytest fixtures for audio testing."""

import numpy as np
import pytest


@pytest.fixture
def sample_rate():
    """Standard sample rate for tests."""
    return 44100


@pytest.fixture
def mono_audio(sample_rate):
    """Mono audio - single channel."""
    return np.random.randn(sample_rate) * 0.1


@pytest.fixture
def stereo_audio(sample_rate):
    """Stereo audio - two channels."""
    left = np.random.randn(sample_rate) * 0.1
    right = np.random.randn(sample_rate) * 0.1
    return np.stack([left, right], axis=-1)


@pytest.fixture
def silence_audio(sample_rate):
    """Silent audio (zeros)."""
    return np.zeros(sample_rate)


@pytest.fixture
def mixed_audio(sample_rate):
    """Audio with both silence and noise segments."""
    silence = np.zeros(int(0.5 * sample_rate))
    noise = np.random.randn(int(1.0 * sample_rate)) * 0.1
    silence2 = np.zeros(int(0.5 * sample_rate))
    return np.concatenate([silence, noise, silence2])


@pytest.fixture
def short_audio(sample_rate):
    """Short audio clip (0.1 seconds)."""
    return np.random.randn(int(0.1 * sample_rate)) * 0.1
