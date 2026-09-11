import json

import numpy as np

from IDPsych import dataIO


def test_rightBias():
    # two right changes, both hit -> two right responses -> no bias
    assert dataIO.rightBias([1, 1, 0, 0], [0, 0, 0, 0]) == 0
    # all changes left, all missed -> every response was "right"
    assert dataIO.rightBias([0, 0], [1, 1]) == 100


def test_saveDict_roundtrip_handles_numpy(tmp_path):
    data = {"a": np.arange(3), "b": np.float64(1.5), "c": [1, 2]}
    out = dataIO.saveDict(data, tmp_path / "x")
    assert out.suffix == ".json"
    assert json.load(open(out)) == {"a": [0, 1, 2], "b": 1.5, "c": [1, 2]}
    assert dataIO.loadDict(out)["a"] == [0, 1, 2]
