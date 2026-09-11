# IDPsych

Analysis code for the human psychophysics experiment in
*Increments in visual motion coherence are more readily detected than
decrements* (Wei, Mitchell & Maunsell, 2023, *J Vis* 23(5):18).

Subjects detected a change in motion coherence of a random-dot stimulus,
either an increment (Inc) or a decrement (Dec), with a staircase adjusting
the size of the change. This package loads the session `.mat` files, applies
trial certification, computes per-session summaries (threshold, hit rate,
right-side bias), and produces the summary figures.

## Install

```bash
pip install -e .          # from this folder
pip install -e ".[dev]"   # also installs pytest and jupyter
```

Requires Python 3.9+. Dependencies: numpy, scipy, pandas, matplotlib,
seaborn, pymatreader.

## Data layout

```
<dataDir>/
    403/
        2022-03-01_..._Inc.mat
        2022-03-01_..._Dec.mat
        ...
    404/
    ...
```

One folder per subject, one `.mat` file per session, written by the
experiment control software. Files with `Info` in the name are skipped.
The first 10 characters of each file name are treated as the session date;
each experiment day contains one Inc and one Dec session.

## Usage

```python
from IDPsych import dataIO, vis

allData = dataIO.allSubjectDict("/path/to/data", ["403", "404", "405"])
dataIO.saveDict(allData, "outputs/primaryData")

vis.IDscat(allData, saveTo="outputs/thresholds.pdf")
vis.hitRateHist(allData, saveTo="outputs/hitRate.pdf")
vis.rBias(allData, saveTo="outputs/rBias.pdf")
```

`allData[sj]` is a dictionary of lists with one entry per session:
`fileName, nTrials, taskMode (0 Dec / 1 Inc), stairType, frameRateHz,
baseCohPC, behavSettings, dotSettings, trials, rightBiasPC, thresholdPC,
hitRatePC, dayOfExp`.

Threshold can be computed three ways (`method=` in `allSubjectDict`):

| method | threshold = |
|---|---|
| 0 (default) | coherence change on the last certified trial |
| 1 | mean of the last `last` trials |
| 2 | mean of the last `lastRev` staircase reversals |

See `notebooks/example.ipynb` for a quick start and
`notebooks/paper_figures.ipynb` to reproduce the figures in the paper.

## Reproducing the paper figures

The package ships the per-session thresholds estimated with psignifit
(MATLAB) that the published Fig 2 and Sup Fig 1 are based on, so those
figures and the learning-effect analysis run without the raw data:

```python
from IDPsych import calc, cohorts, dataIO, vis

psig = dataIO.loadPsignifit("33ms")          # {sj: {taskMode, thresholdPC}}
calc.subjectSummary(psig)                     # mean, SEM, Dec/Inc ratio per subject
vis.thresholdScatter(psig, saveTo="Fig2.pdf")  # Fig 2
calc.learningTable(psig)                      # exponential fit per subject
vis.learningAverage(psig)
```

Cohorts (`cohorts.COHORTS`): `100ms` (dot life 100 ms, 2.5 dots/deg²),
`33ms` (33 ms, 5 dots/deg², main dataset), `control` (increment-only
sessions with a lowered baseline).

## Modules

- `dataIO` – read `.mat` sessions, certify trials, build the subject dictionary, save/load JSON
- `calc` – hit rate, threshold, reversal detection, per-subject summary, exponential learning-curve fits
- `cohorts` – subject groups and their stimulus parameters
- `vis` – paper-style figures: threshold scatter, learning curves, hit-rate histogram, right-bias violin plot
- `data/psignifit_thresholds.json` – psignifit thresholds used in the paper

## Tests

```bash
pytest
```

The tests use small synthetic staircases and the packaged psignifit data, so they run without the raw .mat files.
