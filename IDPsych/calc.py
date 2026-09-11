"""Per-session summary statistics computed from certified trials."""

from statistics import mean

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import sem


def hitRate(eotFiltered, elim=0):
    """
    Hit rate (percent) over certified trials.

    :param eotFiltered: end-of-trial codes for certified trials only,
                        where 0 = hit and 1 = miss
    :param elim: number of trials to drop from the beginning before
                 computing the rate (0 keeps all trials)
    """
    eot = eotFiltered[elim:]
    if len(eot) == 0:
        raise ValueError("no trials left after eliminating the first %d" % elim)
    return 100 - sum(eot) / len(eot) * 100


def threshold(cohFiltered, eotFiltered, baseline, method=0, last=10, lastRev=6):
    """
    Threshold (percent coherence change from baseline) for one session.

    Methods:
        0 (default): coherence of the last trial
        1: mean coherence of the last `last` trials
        2: mean coherence at the last `lastRev` staircase reversals

    :param cohFiltered: coherence on each certified trial
    :param eotFiltered: end-of-trial code on each certified trial (0 hit, 1 miss)
    :param baseline: baseline coherence the staircase is measured against
    :param method: 0, 1, or 2 (see above)
    :param last: number of trials averaged in method 1
    :param lastRev: number of reversals averaged in method 2
    """
    if len(cohFiltered) == 0:
        raise ValueError("cohFiltered is empty")
    if len(cohFiltered) != len(eotFiltered):
        raise ValueError("cohFiltered and eotFiltered must have the same length")

    if method == 0:
        return abs(baseline - cohFiltered[-1])
    if method == 1:
        return abs(baseline - mean(cohFiltered[-last:]))
    if method == 2:
        revList = reversals(cohFiltered, eotFiltered)[-lastRev:]
        if len(revList) < lastRev:
            raise ValueError(
                "only %d reversals found, %d requested" % (len(revList), lastRev)
            )
        return abs(baseline - mean(revList))
    raise ValueError("method must be 0, 1, or 2, got %r" % method)


def reversals(cohFiltered, eotFiltered):
    """
    Coherence values at every staircase reversal, in trial order.

    A reversal is the first trial of a new run of outcomes, i.e. a trial
    whose end-of-trial code differs from the previous trial's. This is the
    same definition the original method 2 used, without the unbounded
    backward walk.
    """
    return [
        cohFiltered[tr]
        for tr in range(1, len(eotFiltered))
        if eotFiltered[tr] != eotFiltered[tr - 1]
    ]


# --------------------------------------------------------------------------
# Across-session summaries
# --------------------------------------------------------------------------

def splitByTaskMode(sjData):
    """
    (inc, dec) threshold arrays for one subject's data dictionary, where
    inc = sessions with taskMode 1 and dec = sessions with taskMode 0.
    """
    taskMode = np.asarray(sjData["taskMode"])
    thr = np.asarray(sjData["thresholdPC"], dtype=float)
    return thr[taskMode == 1], thr[taskMode == 0]


def subjectSummary(data, sj=None):
    """
    Mean and SEM of Inc and Dec thresholds.

    With `sj` given, returns a dict for that subject:
        {'Inc': (mean, sem), 'Dec': (mean, sem), 'ratio': meanDec / meanInc}
    Without `sj`, returns a pandas DataFrame with one row per subject.
    """
    if sj is not None:
        inc, dec = splitByTaskMode(data[sj])
        return {
            "Inc": (float(np.mean(inc)), float(sem(inc))),
            "Dec": (float(np.mean(dec)), float(sem(dec))),
            "ratio": float(np.mean(dec) / np.mean(inc)),
        }
    rows = {}
    for s in sorted(data):
        r = subjectSummary(data, s)
        rows[s] = {
            "incMean": r["Inc"][0], "incSEM": r["Inc"][1],
            "decMean": r["Dec"][0], "decSEM": r["Dec"][1],
            "ratio": r["ratio"],
        }
    return pd.DataFrame(rows).T


# --------------------------------------------------------------------------
# Learning effect: exponential fit of threshold against session number
# --------------------------------------------------------------------------

def fitExp(x, a, b, c):
    """a * exp(b * x) + c"""
    return a * np.exp(b * x) + c


def learningCurve(thresholds, normalize=False, nBaseline=5, bounds=None):
    """
    Fits threshold vs. session number with a decaying exponential and
    returns the time constant and asymptote.

    :param thresholds: threshold on each session, in session order
    :param normalize: divide by the mean of the first `nBaseline` sessions
                      before fitting
    :param bounds: (lower, upper) bounds for (a, b, c) passed to curve_fit.
                   Default forces b < -0.002 (a decreasing curve) and keeps
                   a and c within the data range, matching the paper analysis.
    Returns a dict with keys:
        tau        time constant in sessions (-1 / b)
        intercept  fitted value at x = 0 (a + c)
        asymptote  c
        params     (a, b, c)
        x, y       the session numbers and (possibly normalized) data
        fitted     fitted curve evaluated at x
    """
    y = np.asarray(thresholds, dtype=float)
    if normalize:
        y = y / np.mean(y[:nBaseline])
    x = np.arange(1, len(y) + 1, dtype=float)
    if bounds is None:
        bounds = ([0, -np.inf, 0], [max(30, y.max()), -0.002, y.max()])
    params, _ = curve_fit(fitExp, x, y, bounds=bounds, maxfev=1000)
    a, b, c = params
    return {
        "tau": -1 / b,
        "intercept": a + c,
        "asymptote": c,
        "params": tuple(params),
        "x": x,
        "y": y,
        "fitted": fitExp(x, *params),
    }


def learningTable(data, subjects=None):
    """
    Per-subject learning-curve fits for Inc and Dec, plus a fit to the
    across-subject average. Returns a DataFrame with rows
    [Inc tau, Inc intercept, Inc asymptote, Dec tau, Dec intercept, Dec asymptote].
    """
    subjects = sorted(data) if subjects is None else list(subjects)
    cols = {}
    allInc, allDec = [], []
    for sj in subjects:
        inc, dec = splitByTaskMode(data[sj])
        allInc.append(inc)
        allDec.append(dec)
        fi, fd = learningCurve(inc), learningCurve(dec)
        cols[sj] = [fi["tau"], fi["intercept"], fi["asymptote"],
                    fd["tau"], fd["intercept"], fd["asymptote"]]
    fi = learningCurve(np.mean(allInc, axis=0))
    fd = learningCurve(np.mean(allDec, axis=0))
    cols["Average"] = [fi["tau"], fi["intercept"], fi["asymptote"],
                       fd["tau"], fd["intercept"], fd["asymptote"]]
    index = ["Inc tau", "Inc intercept", "Inc asymptote",
             "Dec tau", "Dec intercept", "Dec asymptote"]
    return pd.DataFrame(cols, index=index).round(1)
