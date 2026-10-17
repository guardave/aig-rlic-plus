"""Causal regime signals for the harness: IS-frozen fits with filtered probabilities (scripts/_regime_causal.py).

On the revised / market track the fit uses rows before the OOS start and filters forward. In a null draw the
raw inputs are shifted first, so the fit is re-estimated on the shifted data (R7.1 runs the full pipeline).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _regime_causal import fit_hmm_causal, fit_ms_causal  # noqa: E402,F401


def hmm_stress(features: pd.DataFrame, oos_start, label_feature: str, seeds=(42, 0, 1, 2, 3), **kw) -> pd.Series:
    """Filtered P(stress) of a 2-state Gaussian HMM; stress = higher IS mean of `label_feature`."""
    fit = fit_hmm_causal(features, oos_start, n_states=2, label_feature=label_feature, label="max",
                         covariance_type="full", n_iter=200, seeds=seeds, **kw)
    return fit.prob.reindex(features.index)


def ms_stress(y: pd.Series, oos_start, **kw) -> pd.Series:
    """Hamilton-filtered P(high-variance regime) of a 2-regime Markov-switching model, IS-frozen params."""
    fit = fit_ms_causal(y, oos_start, k_regimes=2, switching_variance=True, label="max_variance", **kw)
    return fit.prob.reindex(y.index)
