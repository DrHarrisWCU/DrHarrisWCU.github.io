"""Fit the Optional B model to the CSV that log_step.py saved."""
import numpy as np
from scipy.optimize import least_squares

t, cmd, pos = np.loadtxt("run1.csv", delimiter=",", skiprows=1, unpack=True)


def model(p, t, cmd):
    delay, wn, zeta, vmax = p
    th = np.zeros_like(t)
    w = 0.0
    for k in range(1, len(t)):
        dt = t[k] - t[k - 1]                        # real logs are not evenly spaced
        c = np.interp(t[k] - delay, t, cmd)         # the command, delayed
        w += (wn**2 * (c - th[k - 1]) - 2 * zeta * wn * w) * dt
        w = np.clip(w, -vmax, vmax)
        th[k] = th[k - 1] + w * dt
    return th


fit = least_squares(lambda p: model(p, t, cmd) - pos,
                    x0=[0.01, 30, 0.7, 6.0],
                    bounds=([0, 5, 0.1, 1], [0.05, 100, 2.0, 8]))
print({k: round(float(v), 3) for k, v in zip(["delay", "wn", "zeta", "vmax"], fit.x)})
print("RMS error (rad):", float(np.sqrt(np.mean((model(fit.x, t, cmd) - pos) ** 2))))
