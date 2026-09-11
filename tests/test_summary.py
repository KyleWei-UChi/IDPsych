import numpy as np
import pytest

from IDPsych import calc, cohorts, dataIO


def test_loadPsignifit_shape_and_ratio():
    d = dataIO.loadPsignifit("33ms")
    assert sorted(d) == cohorts.subjects("33ms")
    for sj in d:
        assert len(d[sj]["thresholdPC"]) == 30
        assert d[sj]["taskMode"] == [1] * 15 + [0] * 15
    # The published result: decrement thresholds roughly twice increment
    summary = calc.subjectSummary(d)
    assert (summary["ratio"] > 1.5).all()
    with pytest.raises(KeyError):
        dataIO.loadPsignifit("control")


def test_subjectSummary_single():
    d = {"x": dataIO.fromThresholds([10, 12, 14], [20, 22, 24])}
    s = calc.subjectSummary(d, "x")
    assert s["Inc"][0] == 12 and s["Dec"][0] == 22
    assert s["ratio"] == pytest.approx(22 / 12)


def test_learningCurve_recovers_tau():
    x = np.arange(1, 16)
    y = 20 * np.exp(-x / 4) + 15
    f = calc.learningCurve(y)
    assert f["tau"] == pytest.approx(4, rel=0.05)
    assert f["asymptote"] == pytest.approx(15, rel=0.05)
    fn = calc.learningCurve(y, normalize=True)
    assert fn["y"][:5].mean() == pytest.approx(1)


def test_learningTable_columns():
    d = dataIO.loadPsignifit("33ms")
    t = calc.learningTable(d)
    assert list(t.columns) == cohorts.subjects("33ms") + ["Average"]
    assert t.shape == (6, 6)
