"""Audio analysis functions."""

import numpy as np
import pyloudnorm as pyln
from math import ceil


def analyze_loudness(audio_data, sample_rate):
    """Analyze loudness of audio signal using ITU-R BS.1770-4.

    Args:
        audio_data: Audio samples as numpy array (can be mono or stereo)
        sample_rate: Sample rate in Hz

    Returns:
        Dictionary with loudness metrics:
            - integrated_lufs: Integrated loudness in LUFS
            - loudness_range_lra: Loudness range in LU
            - moments: List of {"time": float, "lufs": float}
            - loudest: {"time": float, "lufs": float}
            - softest: {"time": float, "lufs": float}
    """
    if audio_data.ndim == 1:
        audio_mono = audio_data.copy()
        audio_mono = audio_mono.reshape(-1, 1)
    else:
        audio_mono = audio_data.copy()

    meter = pyln.Meter(sample_rate)

    integrated_lufs = meter.integrated_loudness(audio_mono)

    try:
        loudness_range_lra = meter.loudness_range(audio_mono)
    except ValueError:
        loudness_range_lra = 0.0

    window_size = int(1.0 * sample_rate)
    hop_size = int(1.0 * sample_rate)

    num_channels = audio_mono.shape[1] if audio_mono.ndim > 1 else 1

    moments = []
    max_lufs = float("-inf")
    min_lufs = float("inf")
    loudest_time = 0.0
    softest_time = 0.0

    for start in range(0, len(audio_mono) - window_size + 1, hop_size):
        end = start + window_size
        window = audio_mono[start:end]
        time_seconds = start / sample_rate

        filtered = window.copy()
        for filter_name, filter_stage in meter._filters.items():
            for ch in range(num_channels):
                filtered[:, ch] = filter_stage.apply_filter(window[:, ch])

        G = [1.0, 1.0, 1.0, 1.41, 1.41]
        mean_square = np.mean(
            np.sum([G[i] * np.mean(filtered[:, i] ** 2) for i in range(num_channels)])
        )

        if mean_square > 0:
            lufs = -0.691 + 10.0 * np.log10(mean_square)
        else:
            lufs = -np.inf

        if np.isfinite(lufs):
            moments.append({"time": float(time_seconds), "lufs": float(lufs)})

            if lufs > max_lufs:
                max_lufs = lufs
                loudest_time = time_seconds
            if lufs < min_lufs:
                min_lufs = lufs
                softest_time = time_seconds

    if len(moments) == 0 or not np.isfinite(max_lufs):
        max_lufs = integrated_lufs
        min_lufs = integrated_lufs
        loudest_time = 0.0
        softest_time = 0.0

    return {
        "integrated_lufs": float(integrated_lufs),
        "loudness_range_lra": float(loudness_range_lra),
        "moments": moments,
        "loudest": {"time": float(loudest_time), "lufs": float(max_lufs)},
        "softest": {"time": float(softest_time), "lufs": float(min_lufs)},
    }


def detect_silence(audio_data, sample_rate, threshold_db=-40.0, min_duration=0.5):
    """Detect silence regions in audio signal.

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        threshold_db: Silence threshold in dB relative to max RMS (default: -40.0)
        min_duration: Minimum duration in seconds (default: 0.5)

    Returns:
        List of silence regions, each with:
            - start: Start time in seconds
            - end: End time in seconds
            - duration: Duration in seconds
    """
    if audio_data.ndim > 1:
        audio_mono = np.mean(audio_data, axis=1)
    else:
        audio_mono = audio_data

    frame_length = int(0.02 * sample_rate)
    hop_length = int(0.01 * sample_rate)

    frames = []
    for i in range(0, len(audio_mono) - frame_length, hop_length):
        frame = audio_mono[i : i + frame_length]
        rms = np.sqrt(np.mean(frame**2))
        frames.append(rms)

    frames = np.array(frames)

    if len(frames) == 0:
        return []

    max_rms = np.max(frames)
    if max_rms > 0:
        db_values = 20 * np.log10(frames / max_rms)
    else:
        db_values = np.full_like(frames, -np.inf)

    silent_frames = db_values < threshold_db

    silence_regions = []
    in_silence = False
    start_frame = 0

    for i, is_silent in enumerate(silent_frames):
        if is_silent and not in_silence:
            start_frame = i
            in_silence = True
        elif not is_silent and in_silence:
            start_time = start_frame * hop_length / sample_rate
            end_time = i * hop_length / sample_rate
            duration = end_time - start_time

            if duration >= min_duration:
                silence_regions.append(
                    {
                        "start": round(start_time, 3),
                        "end": round(end_time, 3),
                        "duration": round(duration, 3),
                    }
                )
            in_silence = False

    if in_silence:
        start_time = start_frame * hop_length / sample_rate
        end_time = len(audio_mono) / sample_rate
        duration = end_time - start_time

        if duration >= min_duration:
            silence_regions.append(
                {
                    "start": round(start_time, 3),
                    "end": round(end_time, 3),
                    "duration": round(duration, 3),
                }
            )

    return silence_regions


def detect_speaker_changes(
    audio_data, sample_rate, sensitivity=0.5, segment_duration=0.5
):
    """Detect speaker changes based on energy variations.

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        sensitivity: Detection sensitivity 0.0-1.0 (default: 0.5)
            Higher values = more sensitive to changes
        segment_duration: Duration of each segment in seconds (default: 0.5)

    Returns:
        List of speaker changes, each with:
            - time: Time in seconds where change occurs
            - confidence: Confidence score 0.0-1.0
            - type: Type of change (e.g., "amplitude_change")
    """
    # Ensure audio is 1D
    if audio_data.ndim > 1:
        audio_mono = np.mean(audio_data, axis=1)
    else:
        audio_mono = audio_data

    # Compute mean-squared energy in non-overlapping windows
    segment_samples = max(1, int(segment_duration * sample_rate))
    num_segments = ceil(len(audio_mono) / segment_samples)

    energies = []
    for i in range(num_segments):
        start = i * segment_samples
        end = min(len(audio_mono), (i + 1) * segment_samples)
        segment = audio_mono[start:end]
        mse = np.mean(segment**2)
        energies.append(mse)

    energies = np.array(energies)

    # Handle edge case: no segments generated (audio too short)
    if len(energies) == 0:
        return []

    # Normalize to [0, 1]
    max_energy = np.max(energies)
    if max_energy > 0:
        normalized = energies / max_energy
    else:
        normalized = energies

    # Compute absolute differences between consecutive windows
    diffs = np.abs(np.diff(normalized))

    # Threshold based on sensitivity
    threshold = (1.0 - sensitivity) * 0.3 + 0.05

    # Find changes exceeding threshold with verification
    changes = []
    window = 2
    for i in range(len(diffs)):
        if diffs[i] >= threshold:
            before_slice = normalized[max(0, i - window) : i + 1]
            after_slice = normalized[i + 1 : min(len(normalized), i + 1 + window)]

            if len(before_slice) == 0 or len(after_slice) == 0:
                continue

            before_avg = np.mean(before_slice)
            after_avg = np.mean(after_slice)

            verify_diff = abs(after_avg - before_avg)

            if verify_diff >= threshold * 0.5:
                confidence = min(1.0, diffs[i] * 2)
                time_seconds = (i + 1) * segment_samples / sample_rate
                changes.append(
                    {
                        "time": round(time_seconds, 2),
                        "confidence": round(confidence, 2),
                        "type": "amplitude_change",
                    }
                )

    return changes


def detect_solo_regions(audio_data, sample_rate, threshold_db=-40.0, min_duration=0.5):
    """Detect solo/activity regions in audio signal.

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        threshold_db: Activity threshold in dB (default: -40.0)
        min_duration: Minimum duration in seconds (default: 0.5)

    Returns:
        List of active regions, each with:
            - start: Start time in seconds
            - end: End time in seconds
            - duration: Duration in seconds
            - type: Type of activity (e.g., "possible_solo")
    """
    # Ensure audio is 1D
    if audio_data.ndim > 1:
        audio_mono = np.mean(audio_data, axis=1)
    else:
        audio_mono = audio_data

    # Convert threshold from dB to linear
    threshold_linear = 10 ** (threshold_db / 20.0)

    # Calculate RMS in windows
    window_size = int(0.01 * sample_rate)  # 10ms windows
    hop_size = window_size // 2

    is_active = np.zeros(len(audio_mono), dtype=bool)

    for start in range(0, len(audio_mono) - window_size + 1, hop_size):
        end = start + window_size
        window = audio_mono[start:end]
        rms = np.sqrt(np.mean(window**2))
        if rms >= threshold_linear:
            is_active[start:end] = True

    # Find contiguous regions
    active_regions = []
    in_active = False
    active_start = 0

    for i in range(len(is_active)):
        if is_active[i] and not in_active:
            in_active = True
            active_start = i
        elif not is_active[i] and in_active:
            in_active = False
            duration = (i - active_start) / sample_rate
            if duration >= min_duration:
                active_regions.append(
                    {
                        "start": active_start / sample_rate,
                        "end": i / sample_rate,
                        "duration": duration,
                        "type": "possible_solo",
                    }
                )

    # Handle trailing activity
    if in_active:
        duration = (len(is_active) - active_start) / sample_rate
        if duration >= min_duration:
            active_regions.append(
                {
                    "start": active_start / sample_rate,
                    "end": len(is_active) / sample_rate,
                    "duration": duration,
                    "type": "possible_solo",
                }
            )

    return active_regions


def create_visualization(
    audio_data,
    sample_rate,
    output_path,
    silence=None,
    speaker_changes=None,
    loudness=None,
):
    """Create visualization PNG with waveform, spectrogram, and loudness graph.

    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        output_path: Path to save the PNG file
        silence: List of silence regions
        speaker_changes: List of speaker changes
        loudness: Loudness analysis results

    Returns:
        Path to the generated image file
    """
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib import mlab

    # Ensure audio is 1D
    if audio_data.ndim > 1:
        audio_mono = np.mean(audio_data, axis=1)
    else:
        audio_mono = audio_data

    # Default empty lists/dicts
    silence = silence or []
    speaker_changes = speaker_changes or []
    loudness = loudness or {}

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))

    # 1. Waveform with silence and speaker change overlays
    ax1 = plt.subplot(3, 1, 1)
    time_axis = np.arange(len(audio_mono)) / sample_rate

    # Downsample for display if needed
    max_points = 10000
    if len(audio_mono) > max_points:
        step = len(audio_mono) // max_points
        display_audio = audio_mono[::step]
        display_time = time_axis[::step]
    else:
        display_audio = audio_mono
        display_time = time_axis

    ax1.plot(display_time, display_audio, "b-", linewidth=0.5, alpha=0.7)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")
    ax1.set_title("Waveform")
    ax1.grid(True, alpha=0.3)

    # Overlay silence regions
    for region in silence:
        ax1.axvspan(
            region["start"], region["end"], alpha=0.3, color="gray", label="Silence"
        )

    # Overlay speaker changes
    for change in speaker_changes:
        ax1.axvline(
            x=change["time"], color="red", linestyle="--", alpha=0.7, linewidth=1
        )

    # 2. Mel spectrogram
    ax2 = plt.subplot(3, 1, 2)

    # Compute spectrogram
    nfft = 2048
    noverlap = nfft // 2
    spec, freqs, t = mlab.specgram(
        audio_mono, Fs=sample_rate, NFFT=nfft, noverlap=noverlap
    )

    # Convert to dB
    spec_db = 10 * np.log10(spec + 1e-10)

    # Plot spectrogram
    im = ax2.pcolormesh(t, freqs, spec_db, shading="gouraud", cmap="viridis")
    ax2.set_ylabel("Frequency (Hz)")
    ax2.set_xlabel("Time (s)")
    ax2.set_title("Mel Spectrogram")
    ax2.set_ylim(0, sample_rate / 2)
    plt.colorbar(im, ax=ax2, label="Power (dB)")

    # 3. Loudness graph with markers
    ax3 = plt.subplot(3, 1, 3)

    moments = loudness.get("moments", [])
    if moments:
        times = [m["time"] for m in moments]
        lufs = [m["lufs"] for m in moments]
        ax3.plot(times, lufs, "g-", linewidth=1, label="Momentary Loudness")

        # Mark loudest point
        loudest = loudness.get("loudest", {})
        if loudest:
            ax3.scatter(
                [loudest["time"]],
                [loudest["lufs"]],
                color="red",
                s=100,
                zorder=5,
                label="Loudest",
            )

        # Mark softest point
        softest = loudness.get("softest", {})
        if softest:
            ax3.scatter(
                [softest["time"]],
                [softest["lufs"]],
                color="blue",
                s=100,
                zorder=5,
                label="Softest",
            )

    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Loudness (LUFS)")
    ax3.set_title("Loudness (ITU-R BS.1770-4)")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="upper right")

    # Add integrated loudness annotation
    integrated = loudness.get("integrated_lufs")
    if integrated:
        ax3.axhline(y=integrated, color="orange", linestyle=":", alpha=0.7)
        ax3.text(
            0,
            integrated,
            f" Integrated: {integrated:.1f} LUFS",
            va="bottom",
            fontsize=9,
            color="orange",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)

    return output_path
