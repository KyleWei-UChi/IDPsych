import statistics as stat

def hitRate(eotFiltered, elim = 0):
    '''
    Calculates the hit rate (percentage) for a given measurement. By default,
    it takes all 100 certified trials. If "elim" is not 0, it will
    eliminate the first several trials as given
    :eotFiltered: eot codes filtered using trial certification
    :param elim: specifies how many trials from the beginning are removed
    '''
    hitRatePC = 100 - sum(eotFiltered[elim:]) / len(eotFiltered[elim:]) * 100
    return hitRatePC
    
    
def threshold(cohFiltered, eotFiltered, baseline, method = 0, last = 10, lastRev = 6):
    '''
    Calculates the measured threshold from each session using different methods:
        0 (default): take the last trial from the measurement
        1: average the last few trials (10 by default) as the threshold
        2: average the lasf few reversal values (6 by default) as the threshold
    :param cohFiltered: filtered coherence data on each trial
    :param eotFiltered: filtered eot codes on each trial
    :param method: which method to use (0, 1, or 2)
    :param last: specifies how many trials are used to average in method 1
    :param lastRev: specifies how many reversals are used to average in method 2
    '''
    if method == 0:
        return abs(baseline - cohFiltered[-1])
    else:
        nTrials = len(cohFiltered)
        if method == 1:
            return abs(baseline - stat.mean(cohFiltered[-last:]))
        if method == 2:
            currRev = 0
            revList = []
            tr = len(cohFiltered) - 1       # starting from the last trial
            while currRev < lastRev:
                while eotFiltered[tr - 1] == eotFiltered[tr]:
                    tr -= 1
                revList.append(cohFiltered[tr])
                currRev += 1
                tr -=1
            return abs(baseline - stat.mean(revList))