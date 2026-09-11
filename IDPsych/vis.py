"""Summary figures across subjects. Every function returns the matplotlib
Figure and only writes a file when `saveTo` is given."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import sem

BACKGROUND = "#fbfbfb"
COLOR_INC = "#0e4f66"
COLOR_DEC = "gray"
COLOR_POINT = "#002d1d"
LABEL_KW = dict(fontsize=14, fontfamily="serif")
TITLE_KW = dict(fontweight="bold", fontsize=14, fontfamily="serif")


def splitByTaskMode(data, key):
    """
    Collects `data[sj][key]` across subjects into two lists, one for
    Inc sessions (taskMode 1) and one for Dec sessions (taskMode 0).
    Returns (inc, dec) as lists of per-subject numpy arrays, in sorted
    subject order.
    """
    inc, dec = [], []
    for sj in sorted(data):
        taskMode = np.asarray(data[sj]["taskMode"])
        values = np.asarray(data[sj][key])
        inc.append(values[taskMode == 1])
        dec.append(values[taskMode == 0])
    return inc, dec


def _finish(fig, saveTo, show):
    if saveTo is not None:
        fig.savefig(Path(saveTo))
    if show:
        plt.show()
    return fig


def IDscat(data, lim=(0, 50), saveTo=None, show=True):
    """
    Scatter of each subject's mean Dec threshold against mean Inc threshold
    (error bars = 2 SEM), with marginal histograms of all sessions.

    :param data: dictionary from dataIO.allSubjectDict
    :param lim: axis limits in percent coherence, shared by both axes
    :param saveTo: optional file path for the figure
    """
    fig = plt.figure(figsize=(6, 6))
    fig.patch.set_facecolor(BACKGROUND)
    incBySj, decBySj = splitByTaskMode(data, "thresholdPC")

    for inc, dec in zip(incBySj, decBySj):
        plt.scatter(np.mean(inc), np.mean(dec), c=COLOR_POINT, s=40, alpha=0.8)
        plt.errorbar(
            x=np.mean(inc), y=np.mean(dec),
            xerr=sem(inc) * 2, yerr=sem(dec) * 2,
            ecolor=COLOR_POINT, linewidth=1,
        )

    plt.xlim(lim)
    plt.ylim(lim)
    plt.plot(lim, lim, "k--", linewidth=1)
    plt.xlabel("Increment (%)", **LABEL_KW)
    plt.ylabel("Decrement (%)", **LABEL_KW)
    sns.histplot(x=np.concatenate(incBySj), bins=10, color=COLOR_INC, alpha=0.6,
                 element="step", linewidth=0, kde=True)
    sns.histplot(y=np.concatenate(decBySj), bins=10, color=COLOR_DEC, alpha=0.6,
                 element="step", linewidth=0, kde=True)
    plt.text(lim[0], lim[1] * 1.04, "Inc/Dec Thresholds", **TITLE_KW)
    return _finish(fig, saveTo, show)


def hitRateHist(data, xlim=(60, 90), saveTo=None, show=True):
    """Histogram of per-session hit rates, Inc and Dec overlaid."""
    fig = plt.figure()
    fig.patch.set_facecolor(BACKGROUND)
    incBySj, decBySj = splitByTaskMode(data, "hitRatePC")
    plt.hist(np.concatenate(incBySj), 10, color=COLOR_INC, alpha=0.6, label="Increment")
    plt.hist(np.concatenate(decBySj), 10, color=COLOR_DEC, alpha=0.6, label="Decrement")
    plt.xlim(xlim)
    plt.xlabel("Hit Rate (%)", **LABEL_KW)
    plt.ylabel("Count", **LABEL_KW)
    plt.legend(frameon=False)
    plt.title("Hit Rate Distribution", loc="left", **TITLE_KW)
    return _finish(fig, saveTo, show)


def rBias(data, saveTo=None, show=True):
    """Violin plot of per-session right-side bias, Inc vs Dec."""
    fig = plt.figure()
    fig.patch.set_facecolor(BACKGROUND)
    incBySj, decBySj = splitByTaskMode(data, "rightBiasPC")
    sns.violinplot(
        data=[np.concatenate(incBySj), np.concatenate(decBySj)],
        palette=[COLOR_INC, COLOR_DEC],
    )
    plt.xticks([0, 1], ["Increment", "Decrement"], **LABEL_KW)
    plt.ylabel("R Bias (%)", **LABEL_KW)
    plt.title("R Bias", loc="left", **TITLE_KW)
    return _finish(fig, saveTo, show)
