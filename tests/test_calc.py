import pytest

from IDPsych import calc


def test_hitRate_counts_zeros_as_hits():
    assert calc.hitRate([0, 0, 1, 1]) == 50
    assert calc.hitRate([0, 0, 0, 1], elim=3) == 0
    with pytest.raises(ValueError):
        calc.hitRate([0, 1], elim=2)


# A synthetic joint staircase: coherence goes down after a hit (0) and up
# after a miss (1). Reversals (first trial of each new run) fall at the
# marked trials.
COH = [40, 35, 30, 35, 40, 35, 30, 25, 30, 35, 30]
EOT = [0,  0,  1,  1,  0,  0,  0,  1,  1,  0,  1]
#              ^R      ^R          ^R      ^R  ^R


def test_threshold_method0_last_trial():
    assert calc.threshold(COH, EOT, baseline=50) == 20


def test_threshold_method1_mean_of_last():
    assert calc.threshold(COH, EOT, baseline=50, method=1, last=2) == 50 - 32.5


def test_reversals_match_original_definition():
    assert calc.reversals(COH, EOT) == [30, 40, 25, 35, 30]


def test_threshold_method2_mean_of_last_reversals():
    assert calc.threshold(COH, EOT, baseline=50, method=2, lastRev=3) == 50 - 30
    with pytest.raises(ValueError):
        calc.threshold(COH, EOT, baseline=50, method=2, lastRev=10)


def test_threshold_rejects_bad_input():
    with pytest.raises(ValueError):
        calc.threshold([], [], 50)
    with pytest.raises(ValueError):
        calc.threshold(COH, EOT, 50, method=7)
