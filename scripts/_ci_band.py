"""Shared 95% confidence-interval half-width (Step C #243).

Local-projection and quantile-regression CSVs carry a coefficient and its
two-sided p-value but no standard error. Reconstruct a 95% CI half-width under a
normal approximation so point-estimate charts can show uncertainty whiskers:
|coef|/se = z_p where z_p = Phi^-1(1 - p/2); half = 1.96 * se.
"""
from __future__ import annotations

import numpy as np


def ci95_halfwidth(coef, p_value):
    from scipy.stats import norm
    p = np.clip(np.asarray(p_value, dtype=float), 1e-6, 1 - 1e-6)
    z = norm.ppf(1.0 - p / 2.0)
    se = np.abs(np.asarray(coef, dtype=float)) / np.where(z == 0, np.nan, z)
    return 1.96 * se
