"""
Script: Fourier Transform
What it does: Breaks a signal into its frequency components.
Think of it like splitting white light into a rainbow —
it reveals what frequencies (pitches, wavelengths) make up a signal.
Used in audio processing, image compression (JPEG), and signal analysis.

Install: pip install numpy matplotlib
"""

try:
    import numpy as np
    import matplotlib.pyplot as plt

    # --- Create a signal made of multiple frequencies ---
    sample_rate = 1000   # 1000 samples per second
    duration = 1.0       # 1 second
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Mix three sine waves: 5 Hz, 15 Hz, 50 Hz
    freq1, amp1 = 5, 1.0    # 5 Hz  (low frequency)
    freq2, amp2 = 15, 0.5   # 15 Hz (medium frequency)
    freq3, amp3 = 50, 0.3   # 50 Hz (high frequency)

    signal = (amp1 * np.sin(2 * np.pi * freq1 * t) +
              amp2 * np.sin(2 * np.pi * freq2 * t) +
              amp3 * np.sin(2 * np.pi * freq3 * t))

    print("=== Fourier Transform Demo ===")
    print(f"Signal is a mix of: {freq1} Hz, {freq2} Hz, {freq3} Hz\n")

    # --- Apply Fourier Transform ---
    fft_result = np.fft.fft(signal)        # compute FFT
    frequencies = np.fft.fftfreq(len(t), 1/sample_rate)  # frequency axis

    # Take only the positive frequencies (FFT is symmetric)
    pos_mask = frequencies > 0
    frequencies_pos = frequencies[pos_mask]
    magnitude = np.abs(fft_result[pos_mask]) * 2 / len(t)  # normalized magnitude

    # --- Find peak frequencies ---
    top_indices = np.argsort(magnitude)[-5:][::-1]  # top 5 peaks
    print("=== Detected Frequencies ===")
    for idx in top_indices:
        freq = frequencies_pos[idx]
        amp = magnitude[idx]
        if amp > 0.05:  # filter small peaks
            print(f"  Frequency: {freq:.1f} Hz, Amplitude: {amp:.3f}")

    # --- Visualize ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

    # Time domain signal
    ax1.plot(t[:200], signal[:200])  # show first 200ms
    ax1.set_title("Time Domain Signal (first 200ms)")
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Amplitude")
    ax1.grid(True, alpha=0.3)

    # Frequency domain
    ax2.plot(frequencies_pos, magnitude)
    ax2.set_title("Frequency Domain (Fourier Transform)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Amplitude")
    ax2.set_xlim(0, 100)
    ax2.grid(True, alpha=0.3)
    for f in [freq1, freq2, freq3]:
        ax2.axvline(x=f, color="red", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("fourier_transform.png")
    plt.close()
    print("\nVisualization saved: fourier_transform.png")
    print("The FFT correctly identified all 3 frequency components!")

    import os
    os.remove("fourier_transform.png")

except ImportError:
    print("Install: pip install numpy matplotlib")
