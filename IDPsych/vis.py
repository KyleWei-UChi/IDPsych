"""Figures. Styling follows Wei, Mitchell & Maunsell (2023): Helvetica,
14 pt labels, unrotated multi-line y-labels, black error bars.

Every function returns the matplotlib Figure and writes a file only when
`saveTo` is given. Pass `show=False` in scripts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import sem

from IDPsych import calc

# Paper palette
BLUE = "#438de7"      # increment
RED = "#cb4c73"       # decrement
GRAY = "gray"
YELLOW = "#ffc61e"

PAPER_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.frameon": False,
    "legend.fontsize": 8,
    "figure.dpi": 150,
    "savefig.dpi": 300,
}


def paperStyle():
    """Context manager: `with vis.paperStyle(): ...` applies the paper rcParams."""
    return plt.rc_context(PAPER_RC)


def _finish(fig, saveTo, show):
    fig.set_tight_layout(True)
    if saveTo is not None:
        fig.savefig(Path(saveTo))
    if show:
        plt.show()
    return fig


def _ylabel(ax, text, labelpad=50):
    """Unrotated, multi-line y-label as used throughout the paper."""
    ax.set_ylabel(text, rotation=0, labelpad=labelpad, va="center")


# --------------------------------------------------------------------------
# Threshold scatter (Fig 2, Sup Fig 1, control)
# --------------------------------------------------------------------------

def thresholdScatter(data, subjects=None, style=None, lim=(0, 50),
                     xlabel="Increment Change Threshold (%)",
                     ylabel="Decrement\nChange\nThreshold\n(%)",
                     ax=None, saveTo=None, show=True):
    """
    Mean Dec threshold against mean Inc threshold, one point per subject,
    error bars = 1 SEM across sessions, with the unity line.

    :param data: {sj: {'taskMode': [...], 'thresholdPC': [...]}}
    :param subjects: which subjects to plot, in order (default: all, sorted)
    :param style: {sj: dict of errorbar kwargs} to override the default
                  gray filled circle for particular subjects, e.g.
                  {'201': dict(mfc='w')} for an open symbol
    :param lim: axis limits, shared by x and y
    """
    subjects = sorted(data) if subjects is None else list(subjects)
    style = style or {}
    with paperStyle():
        if ax is None:
            fig, ax = plt.subplots(figsize=(6.4, 5))
        else:
            fig = ax.figure
        for sj in subjects:
            inc, dec = calc.splitByTaskMode(data[sj])
            kw = dict(marker="o", mec="k", mfc=GRAY, markeredgewidth=0.5,
                      ecolor="k", linewidth=1, linestyle="none")
            kw.update(style.get(sj, {}))
            ax.errorbar(np.mean(inc), np.mean(dec), xerr=sem(inc), yerr=sem(dec), **kw)
        ax.plot(lim, lim, "k--", linewidth=1, dashes=(5, 10))
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_xlabel(xlabel)
        _ylabel(ax, ylabel)
        return _finish(fig, saveTo, show)


def thresholdScatterColored(data, groups, lim=(0, 50), saveTo=None, show=True):
    """
    Colored variant of thresholdScatter used in early drafts:
    `groups` is {color: [subjects]} (see notebook for the paper's grouping).
    """
    style = {sj: dict(mfc=color, mec=color, color=color)
             for color, sjs in groups.items() for sj in sjs}
    subjects = [sj for sjs in groups.values() for sj in sjs]
    return thresholdScatter(data, subjects, style, lim,
                            xlabel="Increment Threshold (%)",
                            ylabel="Decrement\nThreshold\n(%)",
                            saveTo=saveTo, show=show)


# --------------------------------------------------------------------------
# Learning effect
# --------------------------------------------------------------------------

def learningAverage(data, subjects=None, ylim=(10, 50), showFit=True,
                    saveTo=None, show=True):
    """
    Across-subject mean threshold on each session, Inc (blue) and Dec (red),
    error bars = SEM across subjects, with the exponential fit dotted in red.
    """
    subjects = sorted(data) if subjects is None else list(subjects)
    allInc = np.array([calc.splitByTaskMode(data[sj])[0] for sj in subjects])
    allDec = np.array([calc.splitByTaskMode(data[sj])[1] for sj in subjects])
    aveInc, aveDec = allInc.mean(axis=0), allDec.mean(axis=0)
    x = np.arange(1, len(aveInc) + 1)

    with paperStyle():
        fig, ax = plt.subplots()
        ax.plot(x, aveInc, "-o", color=BLUE, label="Increment")
        ax.plot(x, aveDec, "-o", color=RED, label="Decrement")
        ax.errorbar(x, aveInc, yerr=sem(allInc, axis=0), fmt="o", color=BLUE,
                    ecolor="k", linewidth=0.5)
        ax.errorbar(x, aveDec, yerr=sem(allDec, axis=0), fmt="o", color=RED,
                    ecolor="k", linewidth=0.5)
        if showFit:
            for y in (aveInc, aveDec):
                f = calc.learningCurve(y)
                ax.plot(f["x"], f["fitted"], ":r")
        ax.set_ylim(ylim)
        ax.set_xticks([1, 5, 10, 15])
        ax.set_xlabel("Session #")
        _ylabel(ax, "Threshold\n(%)")
        ax.legend()
        return _finish(fig, saveTo, show)


def learningNormalized(data, subjects=None, nBaseline=5, saveTo=None, show=True):
    """
    Three-panel figure: average thresholds (top) and, below, Inc and Dec
    thresholds normalized to the first `nBaseline` sessions with the
    fitted time constant printed on each panel.
    """
    subjects = sorted(data) if subjects is None else list(subjects)
    allInc = np.array([calc.splitByTaskMode(data[sj])[0] for sj in subjects])
    allDec = np.array([calc.splitByTaskMode(data[sj])[1] for sj in subjects])
    aveInc, aveDec = allInc.mean(axis=0), allDec.mean(axis=0)
    fInc = calc.learningCurve(aveInc, normalize=True, nBaseline=nBaseline,
                              bounds=([0, -np.inf, 0], [np.inf, np.inf, np.inf]))
    fDec = calc.learningCurve(aveDec, normalize=True, nBaseline=nBaseline,
                              bounds=([0, -np.inf, 0], [np.inf, np.inf, np.inf]))
    x = fInc["x"]

    with paperStyle():
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        ax0 = fig.add_subplot(gs[0, :])
        ax0.plot(x, aveInc, "-o", color=BLUE, label="Increment")
        ax0.plot(x, aveDec, "-o", color=RED, label="Decrement")
        ax0.errorbar(x, aveInc, yerr=sem(allInc, axis=0), fmt="o", color=BLUE,
                     ecolor="k", linewidth=1)
        ax0.errorbar(x, aveDec, yerr=sem(allDec, axis=0), fmt="o", color=RED,
                     ecolor="k", linewidth=1)
        ax0.set_ylim(0, 50)
        ax0.set_xticks([1, 5, 10, 15])
        ax0.set_yticks([0, 10, 20, 30, 40, 50])
        _ylabel(ax0, "Threshold\n(%)")
        ax0.legend()

        for col, (f, color) in enumerate([(fInc, BLUE), (fDec, RED)]):
            ax = fig.add_subplot(gs[1, col])
            ax.plot(x, f["y"], "-o", color=color)
            ax.plot(x, f["fitted"], "-", color="k", linewidth=0.8)
            ax.set_ylim(0.5, 1.5)
            ax.set_xticks([1, 5, 10, 15])
            ax.set_yticks([0.5, 1, 1.5])
            ax.text(10.5, 1.35, r"$\tau$ = %d" % round(f["tau"]))
            ax.set_xlabel("Session")
            if col == 0:
                _ylabel(ax, "Normalized\nThreshold")
        return _finish(fig, saveTo, show)


def learningBySubject(data, subjects=None, ylim=(0, 50), saveTo=None, show=True):
    """
    Grid of per-subject learning curves (top row Inc, bottom row Dec) with
    the exponential fit in red, plus an 'Average' column. The fitted
    parameters are available from calc.learningTable(data).
    """
    subjects = sorted(data) if subjects is None else list(subjects)
    n = len(subjects)
    allInc, allDec = [], []
    with paperStyle():
        fig, axes = plt.subplots(2, n + 1, figsize=(4 * (n + 1), 6),
                                 sharex=True, sharey=True)
        for j, sj in enumerate(subjects):
            inc, dec = calc.splitByTaskMode(data[sj])
            allInc.append(inc)
            allDec.append(dec)
            for row, (y, color) in enumerate([(inc, BLUE), (dec, RED)]):
                f = calc.learningCurve(y)
                axes[row, j].plot(f["x"], f["y"], "-o", color=color)
                axes[row, j].plot(f["x"], f["fitted"], "-r")
            axes[0, j].set_title(sj)
        for row, (y, color) in enumerate([(np.mean(allInc, axis=0), BLUE),
                                          (np.mean(allDec, axis=0), RED)]):
            f = calc.learningCurve(y)
            axes[row, n].plot(f["x"], f["y"], "-o", color=color)
            axes[row, n].plot(f["x"], f["fitted"], "-r")
        axes[0, n].set_title("Average")
        axes[0, 0].set_ylim(ylim)
        axes[1, 0].set_xlabel("Session")
        _ylabel(axes[0, 0], "Inc\n(%)", labelpad=30)
        _ylabel(axes[1, 0], "Dec\n(%)", labelpad=30)
        return _finish(fig, saveTo, show)


# --------------------------------------------------------------------------
# Session-level diagnostics (kept from v2.0.0)
# --------------------------------------------------------------------------

def _pool(data, key):
    inc, dec = [], []
    for sj in sorted(data):
        tm = np.asarray(data[sj]["taskMode"])
        v = np.asarray(data[sj][key], dtype=float)
        inc.extend(v[tm == 1])
        dec.extend(v[tm == 0])
    return np.array(inc), np.array(dec)


def hitRateHist(data, xlim=(60, 90), saveTo=None, show=True):
    """Histogram of per-session hit rates, Inc and Dec overlaid."""
    inc, dec = _pool(data, "hitRatePC")
    with paperStyle():
        fig, ax = plt.subplots()
        ax.hist(inc, 10, color=BLUE, alpha=0.6, label="Increment")
        ax.hist(dec, 10, color=RED, alpha=0.6, label="Decrement")
        ax.set_xlim(xlim)
        ax.set_xlabel("Hit Rate (%)")
        ax.set_ylabel("Count")
        ax.legend()
        return _finish(fig, saveTo, show)


def rBias(data, saveTo=None, show=True):
    """Violin plot of per-session right-side bias, Inc vs Dec."""
    import seaborn as sns
    inc, dec = _pool(data, "rightBiasPC")
    with paperStyle():
        fig, ax = plt.subplots()
        sns.violinplot(data=[inc, dec], palette=[BLUE, RED], ax=ax)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Increment", "Decrement"])
        ax.set_ylabel("R Bias (%)")
        return _finish(fig, saveTo, show)


# Backward-compatible name from v2.0.0
def IDscat(data, lim=(0, 50), saveTo=None, show=True):
    """Alias of thresholdScatter with default (gray) styling."""
    return thresholdScatter(data, lim=lim, saveTo=saveTo, show=show)
