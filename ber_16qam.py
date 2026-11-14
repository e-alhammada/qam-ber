"""Gray 16-QAM over AWGN: Monte Carlo BER vs exact theory."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

M, k = 16, 4                                   # constellation size, bits per symbol
N = 500_000                                    # symbols per Eb/N0 point
ebn0_db = np.arange(0, 13, 2)                  # 0, 2, ..., 12 dB
rng = np.random.default_rng(1)                 # seeded generator

pam = np.array([-3, -1, 3, 1])                 # Gray 4-PAM levels for labels 00, 01, 10, 11
labels = np.arange(M)
c = (pam[labels // 4] + 1j * pam[labels % 4]) / np.sqrt(10)   # Es = 1


def q(x):
    """Gaussian Q-function."""
    return 0.5 * erfc(x / np.sqrt(2))


def ber_theory(eb_db):
    """Exact BER of Gray 16-QAM over AWGN (same as MATLAB berawgn)."""
    d = np.sqrt(0.8 * 10 ** (eb_db / 10))
    return (3 * q(d) + 2 * q(3 * d) - q(5 * d)) / 4


ber_sim = np.zeros(len(ebn0_db))
for i, eb_db in enumerate(ebn0_db):            # enumerate gives index and value
    esn0 = k * 10 ** (eb_db / 10)              # Es/N0 = k * Eb/N0
    idx = rng.integers(0, M, size=N)           # transmitted symbol indices
    noise = np.sqrt(1 / (2 * esn0)) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    y = c[idx] + noise                         # AWGN channel
    idx_hat = np.argmin(np.abs(y[:, None] - c[None, :])**2, axis=1)   # minimum distance
    n_err = np.bitwise_count(idx ^ idx_hat).sum()   # XOR, then count the 1-bits
    ber_sim[i] = n_err / (N * k)
    th = ber_theory(eb_db)
    print(f"Eb/N0 = {eb_db:2d} dB: errors = {n_err:7d}, "
          f"BER sim = {ber_sim[i]:.3e}, theory = {th:.3e}, ratio = {ber_sim[i] / th:.3f}")

eb_fine = np.linspace(0, 12, 121)              # smooth theory curve
fig, ax = plt.subplots()
ax.semilogy(eb_fine, ber_theory(eb_fine), "-", label="Theory (exact, Gray)")
ax.semilogy(ebn0_db, ber_sim, "o", label=f"Monte Carlo ({N:,} symbols/point)")
ax.set_xlabel("Eb/N0 (dB)")
ax.set_ylabel("BER")
ax.set_title("Gray 16-QAM over AWGN")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.savefig("ber_16qam.png", dpi=150, bbox_inches="tight")   # image for the README