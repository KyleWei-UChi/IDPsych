"""Loading session .mat files and building the per-subject data dictionary."""

import json
from pathlib import Path

import numpy as np
from pymatreader import read_mat

from IDPsych import calc


def allSubjectDict(dataDir, sjID, **kwargs):
    """
    Master dictionary with every subject's data, keyed by subject ID.

    :param dataDir: folder that contains one sub-folder per subject
    :param sjID: iterable of subject IDs (strings matching the folder names)
    :param kwargs: passed through to loadSubject (elim, method, last, lastRev)
    """
    dataDir = Path(dataDir)
    return {sj: loadSubject(dataDir / sj, **kwargs) for sj in sjID}


def listSessionFiles(sjDir):
    """Sorted list of session .mat files in a subject folder (skips *Info*.mat)."""
    sjDir = Path(sjDir)
    if not sjDir.is_dir():
        raise FileNotFoundError("subject folder not found: %s" % sjDir)
    return sorted(
        f for f in sjDir.iterdir() if f.suffix == ".mat" and "Info" not in f.name
    )


def loadSubject(sjDir, elim=10, method=0, last=10, lastRev=6):
    """
    Loads every session file for one subject and computes per-session
    summaries. Returns a dictionary of lists, one entry per session:

        fileName, nTrials, taskMode (0 Dec / 1 Inc), stairType, frameRateHz,
        baseCohPC, behavSettings, dotSettings, trials, rightBiasPC,
        thresholdPC, hitRatePC, dayOfExp

    :param sjDir: path to the subject's folder of .mat files
    :param elim: certified trials dropped from the start when computing hit rate
    :param method: threshold method (0, 1, or 2), see calc.threshold
    :param last: trials averaged in threshold method 1
    :param lastRev: reversals averaged in threshold method 2
    """
    fileList = listSessionFiles(sjDir)
    # File names start with a 10-character date; each experiment day has one
    # Inc and one Dec session, so dayOfExp counts pairs of dates.
    fileListDate = sorted({f.name[:10] for f in fileList})

    sjData = {
        "fileName": [f.name for f in fileList],
        "nTrials": [],
        "taskMode": [],
        "stairType": [],
        "frameRateHz": [],
        "baseCohPC": [],
        "behavSettings": [],
        "dotSettings": [],
        "trials": [],
        "rightBiasPC": [],
        "thresholdPC": [],
        "hitRatePC": [],
        "dayOfExp": [],
    }

    for fi in fileList:
        session = loadSession(fi)
        trials = session["trials"]
        baseline = session["baseCohPC"]

        for key in (
            "nTrials",
            "taskMode",
            "stairType",
            "frameRateHz",
            "baseCohPC",
            "behavSettings",
            "dotSettings",
            "trials",
        ):
            sjData[key].append(session[key])

        # A trial is certified only when trialCertify == 0 and eotCode is 0 or 1
        cert = np.asarray(trials["trialCertify"])
        eot = np.asarray(trials["eotCode"])
        certified = np.logical_and(cert == 0, np.isin(eot, [0, 1]))

        locFiltered = [l for l, c in zip(trials["changeLoc"], certified) if c]
        eotFiltered = [e for e, c in zip(eot, certified) if c]
        cohFiltered = [k for k, c in zip(trials["trialCohPC"], certified) if c]

        sjData["rightBiasPC"].append(rightBias(locFiltered, eotFiltered))
        sjData["thresholdPC"].append(
            calc.threshold(cohFiltered, eotFiltered, baseline, method, last, lastRev)
        )
        sjData["hitRatePC"].append(calc.hitRate(eotFiltered, elim))
        sjData["dayOfExp"].append(fileListDate.index(fi.name[:10]) // 2 + 1)

    return sjData


def loadSession(matFile):
    """
    Reads one session .mat file into a plain dictionary (settings + trial
    arrays). No filtering or statistics are applied here.
    """
    allTrials = read_mat(str(matFile))
    data = allTrials["trials"]
    fileInfo = allTrials["file"]
    trialList = data["trial"]
    nTrials = len(trialList)
    first = trialList[0]

    return {
        "fileName": Path(matFile).name,
        "nTrials": nTrials,
        # 0 for Dec and 1 for Inc
        "taskMode": first["taskMode"],
        # 0 for joint staircase
        "stairType": first["stairType"],
        "frameRateHz": fileInfo["frameRateHz"]["data"],
        "baseCohPC": first["baseCohPC"],
        "behavSettings": {
            "baseDurMS": first["baseDurMS"],
            "stepDurMS": first["stepDurMS"],
            # Not stored in the .mat file; these were the fixed values used
            # for every session of the 2022 human experiment.
            "revBeforeChange": 6,
            "maxStepPC": abs(first["threshStepsPC"]),
            "minStepPC": abs(trialList[-1]["threshStepsPC"]),
            "stepChangeFactor": 0.5,
        },
        "dotSettings": _dotSettings(data["randomDots"][0]),
        # trialCertify: 0 if the trial is qualified
        # eotCode: 0 for hits and 1 for misses
        # stepDir: 0 for Dec and 1 for Inc (constant within a unidirectional staircase)
        # changeLoc: 0 for left and 1 for right
        "trials": {
            "trialCertify": data["trialCertify"],
            "eotCode": data["eotCode"],
            "stepDir": [tr["stepDir"] for tr in trialList],
            "changeLoc": [tr["changeLoc"] for tr in trialList],
            "stepSizePC": [abs(tr["threshStepsPC"]) for tr in trialList],
            "trialCohPC": [tr["stepCohPC"] for tr in trialList],
        },
    }


def _dotSettings(dots):
    return {
        "azimuthDeg": dots["azimuthDeg"],
        "elevationDeg": dots["elevationDeg"],
        "radiusDeg": dots["radiusDeg"],
        "densityDPD": dots["density"],
        "diameterDeg": dots["dotDiameterDeg"],
        "speedDPS": dots["speedDPS"],
        "lifeFrames": dots["lifeFrames"],
    }


def rightBias(locFiltered, eotFiltered):
    """
    Right-side response bias (percent) over certified trials:
    (right responses - right changes) / n trials * 100.

    A hit (eot 0) means the response matched changeLoc; a miss (eot 1)
    means the subject chose the other side. So the response is "right"
    when changeLoc + eot == 1.
    """
    if len(locFiltered) == 0:
        raise ValueError("no certified trials")
    rightChanges = sum(locFiltered)
    rightResponses = sum(1 for l, e in zip(locFiltered, eotFiltered) if l + e == 1)
    return (rightResponses - rightChanges) / len(locFiltered) * 100


def saveDict(data, filePath):
    """
    Writes the data dictionary to JSON. numpy arrays are converted to lists.

    :param data: dictionary to save
    :param filePath: output path; '.json' is added if missing
    """
    filePath = Path(filePath)
    if filePath.suffix != ".json":
        filePath = filePath.with_suffix(".json")
    with open(filePath, "w") as f:
        json.dump(data, f, default=_jsonDefault)
    return filePath


def loadDict(filePath):
    """Reads a dictionary previously written by saveDict."""
    with open(filePath) as f:
        return json.load(f)


def _jsonDefault(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError("cannot serialize %r" % type(obj))


# --------------------------------------------------------------------------
# psignifit thresholds shipped with the package
# --------------------------------------------------------------------------

_PSIG_FILE = Path(__file__).parent / "data" / "psignifit_thresholds.json"


def loadPsignifit(cohort):
    """
    Per-session thresholds estimated with psignifit (MATLAB), stored in
    IDPsych/data/psignifit_thresholds.json, returned in the same shape
    as allSubjectDict so that calc and vis functions work on them:

        {sj: {'taskMode': [1]*nInc + [0]*nDec,
              'thresholdPC': incThresholds + decThresholds}}

    :param cohort: '100ms' or '33ms'
    """
    with open(_PSIG_FILE) as f:
        raw = json.load(f)
    if cohort not in raw or cohort.startswith("_"):
        raise KeyError("no psignifit data for cohort %r" % cohort)
    out = {}
    for sj, d in raw[cohort].items():
        inc, dec = d["threshIncPC"], d["threshDecPC"]
        out[sj] = {
            "taskMode": [1] * len(inc) + [0] * len(dec),
            "thresholdPC": list(inc) + list(dec),
        }
    return out


def fromThresholds(inc, dec):
    """
    Builds a one-subject data dictionary from explicit Inc and Dec
    threshold lists, for figures that pair sessions across cohorts
    (e.g. the control comparison).
    """
    return {
        "taskMode": [1] * len(inc) + [0] * len(dec),
        "thresholdPC": list(inc) + list(dec),
    }
