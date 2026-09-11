# 2.1.0 — paper figures integrated

Merges the pre-package `IDPsychFigures.ipynb` into the package.

New
- `cohorts.py`: subject groups (100ms, 33ms, control) with stimulus parameters
- `IDPsych/data/psignifit_thresholds.json`: the psignifit thresholds that were pasted as literals in the notebook; loaded with `dataIO.loadPsignifit(cohort)` into the same shape as `allSubjectDict` output
- `dataIO.fromThresholds(inc, dec)`: build a data entry from explicit lists (control figure)
- `calc.splitByTaskMode`, `calc.subjectSummary` (mean/SEM/ratio, dict or DataFrame), `calc.fitExp`, `calc.learningCurve`, `calc.learningTable`
- `vis.thresholdScatter` (Fig 2 / Sup Fig 1 style, per-subject `style` overrides), `vis.thresholdScatterColored`, `vis.learningAverage`, `vis.learningNormalized`, `vis.learningBySubject`, `vis.paperStyle` context manager
- `notebooks/paper_figures.ipynb`: reproduces every figure from the old notebook; psignifit-based cells run without raw data
- 4 more tests (12 total); one checks the published ~2x Dec/Inc ratio from the shipped data

Changed
- `vis` default style is now the paper style (Helvetica/Arial fallback, 14 pt, unrotated y-labels, 1 SEM error bars). The 2022 look (`#fbfbfb` background, serif, 2 SEM, marginal histograms) is gone; `vis.IDscat` is kept as an alias of `thresholdScatter`
- `hitRateHist` and `rBias` use the paper colors
- `pandas` added as a dependency; `package-data` added so the JSON ships with `pip install`
- `.gitignore` exception for `IDPsych/data/*.json`

# 2.0.0 — changes from the 2022 version (setup.py 1.1.1)

Packaging
- `setup.py` replaced by `pyproject.toml`; stray imports and the `statistics` pseudo-dependency removed; Bitbucket URL removed
- Real README, MIT license, Python `.gitignore`, `__init__.py` with version and submodule imports
- Removed the empty `simul.py`, the dead `.git` (Bitbucket remote, zero commits), `.ipynb_checkpoints`, and `testFunctions.ipynb` (a copy of the module source)
- `notebooks/testPackage.ipynb` replaced by `notebooks/example.ipynb` with relative paths

dataIO
- `loadMatFilePyMat` renamed `loadSubject` and takes a folder path; no more `os.chdir` (the old `os.getcwd()[:-3]` only worked for 3-character subject IDs)
- `allSubjectDict(dataDir, sjID, **kwargs)` now takes the data root explicitly
- `.mat` reading split out into `loadSession`, right bias into `rightBias`, so each piece can be tested on its own
- `saveDict` takes a path (any folder), converts numpy types, returns the written path; `loadDict` added
- Output dictionary keys and values are unchanged

calc
- `threshold`: `baseline` documented, method 2 no longer walks past the start of the list (raises ValueError if too few reversals), unknown method raises instead of returning None
- `reversals` factored out; same definition as before (first trial of each new run of outcomes)
- `hitRate` raises on empty input

vis
- All three functions take `saveTo=` and `show=` and return the Figure; nothing is written to the working directory by default
- Axis limits are parameters (`lim`, `xlim`) with the old values as defaults
- Shared `splitByTaskMode` helper replaces three copies of the Inc/Dec loop; colors and font settings are module constants
- Legend added to the hit-rate histogram; text titles moved to `plt.title(loc='left')`

Tests
- `tests/test_calc.py` and `tests/test_dataIO.py`, run with `pytest` (8 tests, no raw data needed)
