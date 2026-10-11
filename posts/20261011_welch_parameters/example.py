import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import get_window, welch
from pathlib import Path

rng = np.random.default_rng(20261011)
fs = 1024.0
N = 32768
t = np.arange(N) / fs
x = 2.0 + np.sin(2 * np.pi * 100 * t)
x += 0.5 * np.sin(2 * np.pi * 104 * t)
x += rng.normal(0.0, 0.2, N)

fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
for L, nfft in [(512, 512), (512, 8192), (4096, 8192)]:
    overlap = L // 2
    w = get_window('hann', L, fftbins=True)
    kw = dict(fs=fs, window=w, nperseg=L, noverlap=overlap,
              nfft=nfft, detrend='constant', return_onesided=True,
              average='mean')
    f, p = welch(x, scaling='density', **kw)
    _, s = welch(x, scaling='spectrum', **kw)
    df = f[1] - f[0]
    enbw = fs * np.sum(w**2) / np.sum(w)**2
    power = np.sum(p) * df
    hop = L - overlap
    starts = range(0, N - L + 1, hop)
    weighted = []
    for start in starts:
        segment = x[start:start + L]
        segment = segment - segment.mean()
        weighted.append(np.sum((segment * w)**2) / np.sum(w**2))
    assert np.allclose(s, p * enbw)
    assert np.isclose(power, np.mean(weighted), rtol=1e-12)
    K = 1 + (N - L) // hop
    print(f'L={L:4d} nfft={nfft:4d} K={K:3d} df={df:.3f} '
          f'ENBW={enbw:.3f} power={power:.6f}')
    label = f'L={L}, nfft={nfft}'
    axes[0].plot(f, p, label=label)
    axes[1].semilogy(f, p, label=label)
for ax in axes:
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('PSD [V²/Hz]')
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
axes[0].set_xlim(94, 110)
axes[0].set_title('Close tones: segment length vs zero padding')
axes[1].set_xlim(150, 300)
axes[1].set_ylim(1e-5, 1e-3)
axes[1].set_title('Noise floor: fewer averages at larger L')
fig.savefig(Path(__file__).with_name('welch_parameters.png'), dpi=160)

print(f'variance={np.var(x):.6f} mean_square={np.mean(x**2):.6f}')
w = get_window('hann', 4096, fftbins=True)
f, p = welch(x, fs=fs, window=w, nperseg=4096, noverlap=2048,
             nfft=8192, detrend=False, scaling='density', average='mean')
print(f'no_detrend_power={np.sum(p) * (f[1] - f[0]):.6f}')
print(f'NumPy={np.__version__} SciPy={scipy.__version__}')
