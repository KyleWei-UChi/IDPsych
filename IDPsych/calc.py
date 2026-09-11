"""Per-session summary statistics computed from certified trials."""

from statistics import mean


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
