"""Reproduce the article's numerical checks and figure."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy
from scipy import signal

fs = 1000.0
t = np.arange(2000) / fs
x = 1.5 + np.sin(2 * np.pi * 8 * t) + 0.3 * np.sin(2 * np.pi * 180 * t)
sos = signal.butter(6, 40, fs=fs, output="sos")
zi0 = signal.sosfilt_zi(sos) * x[0]
y_whole, z_whole = signal.sosfilt(sos, x, zi=zi0.copy())
block_size = 128
state = zi0.copy()
parts, reset_parts = [], []
for start in range(0, len(x), block_size):
    block = x[start:start + block_size]
    y_block, state = signal.sosfilt(sos, block, zi=state)
    parts.append(y_block)
    # Deliberate bug: forget history at each boundary.
    reset_parts.append(signal.sosfilt(sos, block))
y_stream = np.concatenate(parts)
y_reset = np.concatenate(reset_parts)
np.testing.assert_allclose(y_stream, y_whole, rtol=1e-13, atol=1e-13)
np.testing.assert_allclose(state, z_whole, rtol=1e-13, atol=1e-13)
error = np.max(np.abs(y_stream - y_whole))
reset_error = np.max(np.abs(y_reset[block_size:] - y_whole[block_size:]))
print(f"NumPy {np.__version__}; SciPy {scipy.__version__}")
print(f"max streaming error: {error:.3e}")
print(f"max reset error after first block: {reset_error:.6f}")

# Independent state for each of two channels, time axis first.
X = np.column_stack([x, 2 * x])
zi_multi = signal.sosfilt_zi(sos)[:, :, None] * X[0][None, None, :]
Y, zf_multi = signal.sosfilt(sos, X, axis=0, zi=zi_multi)
np.testing.assert_allclose(Y[:, 0], y_whole, rtol=1e-13, atol=1e-13)
np.testing.assert_allclose(Y[:, 1], 2 * y_whole, rtol=1e-13, atol=1e-13)
print(f"multichannel state shape: {zf_multi.shape}")

# Evaluate exactly at the cutoff; sosfreqz works with older SciPy too.
_, h = signal.sosfreqz(sos, worN=[40], fs=fs)
print(f"one-pass cutoff gain: {20 * np.log10(abs(h[0])):.4f} dB")
print(f"forward-backward cutoff gain: {20 * np.log10(abs(h[0]) ** 2):.4f} dB")
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
selection = (t >= 0.20) & (t <= 0.56)
axes[0].plot(t[selection], x[selection], color="0.7", alpha=0.6, label="Input")
axes[0].plot(t[selection], y_whole[selection], lw=2, label="One call / carried state")
axes[0].plot(t[selection], y_reset[selection], label="Zero state every block")
axes[0].set_ylabel("Amplitude")
axes[0].legend(loc="upper right", fontsize=8)
axes[1].plot(t[selection], (y_reset - y_whole)[selection], color="tab:red")
axes[1].set_ylabel("Reset error")
axes[1].set_xlabel("Time [s]")
for ax in axes:
    for boundary in np.arange(block_size, len(x), block_size) / fs:
        if 0.20 <= boundary <= 0.56:
            ax.axvline(boundary, color="0.4", ls="--", lw=0.8)
    ax.grid(alpha=0.25)
fig.suptitle("SOS streaming: carry state across 128-sample blocks")
fig.tight_layout()
fig.savefig(Path(__file__).with_name("sos_block_state.png"), dpi=160)
