# PyTCI

A Python library for target-controlled infusion (TCI) simulation. Originated in the
[NHS Hack Day Propofol project](https://github.com/JMathiszig-Lee/Propofol).

Supports Python 3.11–3.14. Python 3.14 is the stable feature series as of
8 October 2026; [3.15 is still a release candidate](https://discuss.python.org/t/python-3-15-0-candidate-3-is-here/109327).
Numerical propagation uses NumPy and SciPy.

## Installation and development

```sh
pip install PyTCI
# From a checkout:
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
python -m build
python -m benchmarks.simulation
```

Package metadata lives in `pyproject.toml`. CI tests Python 3.11, 3.12, 3.13 and
3.14. Pushing a tag matching the package version (for example `v1.2.0`)
runs the publishing workflow after tests, formatting and distribution checks.
It uses the repository secret `PYPI_PASSWORD`, containing a PyPI API token
with permission to upload PyTCI, and the required username `__token__`.
Account passwords and TestPyPI tokens cannot publish to PyPI.
For the original `v1.2.0` workflow, also set the legacy `PYPI_USERNAME` secret
to `__token__` before rerunning its failed upload job.
The optional Pipenv configuration targets 3.14; regenerate its lockfile with
`pipenv lock` if using Pipenv (the obsolete Python 3.9 lockfile was removed).

## Models

| Drug | Models | Dose units | Cp and Ce units |
| --- | --- | --- | --- |
| Propofol | Schnider, Marsh, Eleveld, Kataria, Paedfusor | mg | mg/L = ug/mL |
| Remifentanil | Minto, Eleveld | ug | ug/L = ng/mL |
| Alfentanil | Maitre | ug | ug/L = ng/mL |
| Dexmedetomidine | Hannivoort, Dyck, **Morse** | ug | ug/L = ng/mL |
| Remimazolam | **Eleveld (2025), simplified arterial TCI model** | mg | mg/L = ug/mL |

The mathematics is independent of dose units: choose the units in the table for
all doses, rates and targets belonging to a given drug. Parameter volumes are
litres, clearances L/min; initialized rate constants are per second.
Kataria, Paedfusor, Hannivoort, Dyck and Morse have no estimated effect-site rate
in these implementations (`keo=0`); they support plasma simulation and targeting,
and reject effect-site calculations.

```python
from PyTCI.models import propofol

patient = propofol.Marsh(70)
patient.give_drug(200)      # instantaneous dose, mg
patient.wait_time(60)      # redistribution and elimination, seconds
print(patient.x1)         # plasma concentration, ug/mL
print(patient.xeo)        # effect-site concentration, ug/mL
```

For compatibility, `x2` and `x3` represent peripheral **amount divided by V1**.
They are not peripheral concentrations. Actual peripheral concentrations are
`x2 * v1 / v2` and `x3 * v1 / v3`. `x1` and `xeo` are concentrations.
A nonzero baseline needs the complete state: preserve it by simulating the dose
history, or restore `ox1`, `ox2`, `ox3`, `oxeo` with `reset_concs()`.
`zero_comps()` empties all compartments.

## Integration and performance

The default `euler` mode retains the original one-second Euler recurrence and
one dose increment at the beginning of each infusion second. Cached matrix powers
advance long intervals without looping over every second. Reordering arithmetic
can change the last few floating-point digits.

```python
patient.set_integrator("exact")
patient.giveoverseconds(0.5, 10)  # continuous 0.5 mg/s input over 10 seconds
patient.wait_time(0.25)          # fractional seconds supported in exact mode
```

Exact mode uses the augmented matrix exponential to calculate both `Phi` and
`Gamma` for constant input, including singular systems. It removes Euler time-step
error and models continuous delivery rather than repeated instantaneous doses.
Switching modes preserves state. Cache keys include current rates, V1, mode,
bolus duration and horizon, so parameter edits cannot reuse a stale response.
Cache sizes are bounded. Euler mode requires integer seconds and rejects rates
that make its one-second update nonpositive; use exact mode for those models.

`python -m benchmarks.simulation` compares scalar and cached one-hour Euler
washout and reports cached bolus timing. On the development machine (Python
3.14.7), one run measured 1,726 us versus 23 us per one-hour washout (about 76x),
and 11 us per cached initial bolus. These are warm-cache, machine-dependent
measurements; imports and the first unit-response calculation are excluded.
Single-second calls may be slower than the original scalar recurrence.

## Effect-site boluses and nonzero baselines

```python
from PyTCI.models import propofol
from PyTCI.models.base import BaselineAboveTargetError, PeakNotFoundError

patient = propofol.Marsh(70)
patient.set_integrator("exact")
initial_mg = patient.effect_bolus(4, bolus_seconds=10)
patient.giveoverseconds(initial_mg / 10, 10)
patient.wait_time(300)

try:
    top_up_mg = patient.effect_bolus_from_baseline(4, bolus_seconds=10)
except BaselineAboveTargetError:
    top_up_mg = None  # Existing drug already predicts a peak above target: wait/reassess.
```

Both bolus methods return a dose without administering it or changing state.
`effect_bolus()` also handles nonzero baselines automatically; the explicit
`effect_bolus_from_baseline()` method makes top-up use clear.
`unit_bolus_peak()` returns `(concentration_per_dose_unit, peak_seconds)`.

For empty compartments and a fixed bolus duration, the cached unit-dose response
is `h(t)`, so dose = `target / max(h(t))`. The full PK parameters and `keo` determine
that response. Peak time is found from the response, replacing the former fixed
90-second evaluation and iterative dose adjustments. In exact mode, the initial
peak is refined using `Cp = Ce`, excluding time zero.

For existing drug, predict its no-input effect-site trajectory `b(t)`. The top-up
is the minimum of `(target - b(t)) / h(t)` for positive `h(t)`. The prediction
includes all compartments, rather than subtracting the current Ce. An existing
baseline peak above target raises `BaselineAboveTargetError`; no nonnegative
bolus can remove that drug. Numerical comparisons allow a floating-point tolerance
of `1e-12 * max(1, target)`.

The default search horizon is `max_time=3600` seconds. Euler mode constrains a
one-second grid. Exact mode refines sampled local dose minima and baseline maxima
between grid points. A peak/minimum at the end of the horizon, or a baseline still
rising at its end, raises `PeakNotFoundError`; increase `max_time`. These are
finite-horizon numerical calculations, not a proof of no overshoot for arbitrary
custom models beyond the horizon. Validate the horizon and sampling for custom
parameters, especially unusually fast or slow rates.

Bolus results are unrounded so rounding cannot introduce a target overshoot.
The calculation assumes a fixed delivery duration and **no subsequent infusion**.
If pump rate limits change that duration, recompute the response for the new
profile. Peak targeting and maintaining a target are different calculations.

## Infusion schedules

```python
patient = propofol.Marsh(70)
rates = patient.plasma_infusion(2, time=65, period=30)
# Three rates in mg/s, for segments lasting 30, 30 and 5 seconds.
```

`plasma_infusion()` advances patient state. Each segment targets its ending Cp
using a no-input prediction and a unit-rate response. Negative rates are clamped
before state propagation, allowing residual drug to wash out. It uses the requested
period and includes a final partial segment.

```python
patient = propofol.Marsh(70)
rates = patient.effect_target(4, time=600, period=10)
# Plan only: patient state is preserved, including when planning raises an error.
for rate in rates:
    patient.giveoverseconds(rate, 10)
```

`effect_target()` returns only rates in dose units/s, including its initial loading
segment. Each segment predicts a peak-targeted top-up from the evolving state and
replans after delivery; it uses zero input while residual drug exceeds the target.
For a partial final segment, replay it for `time % period` seconds. This planner
assumes no rate limit and provides model-based schedules for simulation.

## Newly added models and further candidates

`dexmedetomidine.Morse(age, weight, height, sex, pma=None)` implements the published
Table 1 population medians with FFM clearance scaling, normal fat mass volumes
and clearance maturation. `pma` is postmenstrual age in weeks; its default assumes
40 weeks at birth. FFM is predicted without intermediate rounding, including the
age-zero limit. This is a PK-only model. Its source reports a broad development
population and also notes uncertainty in FFM prediction below age three.
[Morse, Cortinez & Anderson (2020)](https://doi.org/10.3390/jcm9113480)

`remimazolam.Eleveld(age, weight, sex, opioids=False)` implements the paper's
simplified normal-hepatic-function TCI equations with the MOAA/S effect compartment.
It predicts typical parent-drug arterial concentrations. It does not reproduce
the complete paper's venous delay, metabolite tolerance, PD scores, or ICU/ECMO
extensions. Use exact mode for continuous delivery.
[Eleveld et al. (2025), pp. 210–211](https://doi.org/10.1016/j.bja.2025.02.038)

Further candidates found in the literature search on 8 October 2026:

| Candidate | Reason to consider it | Remaining implementation work |
| --- | --- | --- |
| Kim–Obara–Egan remifentanil (2017) | Extends obesity covariates; absent from this library | Verify the primary parameter/covariate tables and keep it PK-only unless a sourced PD model is selected |
| Eisenried/Schüttler remimazolam (2020) | Useful comparator to the new remimazolam implementation | Transcribe the original parameter tables and select the matching PD endpoint |
| Vellinga remimazolam tolerance model (2024) | Captures acute tolerance during prolonged delivery | Requires metabolite and PD states beyond this base model |

Sources: [Kim et al.](https://doi.org/10.1097/ALN.0000000000001635),
[Eisenried et al.](https://pubmed.ncbi.nlm.nih.gov/31972655/),
[Vellinga et al.](https://doi.org/10.1097/ALN.0000000000004811).
These candidates are not implemented. A newer paper alone does not establish
better predictive performance for every population.

## Body mass equations

`PyTCI.weights.leanbodymass` provides BMI, Devine ideal body weight, adjusted body
weight, James, Boer, Hume (1966/1971), Janmahasation and Al-Sallami equations.
The older APIs preserve their rounding behavior; `fat_free_mass(age, height,
weight, sex)` provides an unrounded Al-Sallami estimate for PK covariates.

```python
from PyTCI.weights import leanbodymass
print(leanbodymass.hume66(180, 60, "m"))  # 51.2 kg
```

## Custom models

```python
from PyTCI.models.base import Three

class MyModel(Three):
    def __init__(self):
        self.v1, self.v2, self.v3 = 5.0, 20.0, 100.0  # L
        self.Q1, self.Q2, self.Q3 = 1.0, 0.5, 0.1   # L/min
        self.keo = 0.2                             # /min
        self.from_clearances()
        self.setup()                               # converts rates to /s
```

## Changes from 1.1

- Python support now starts at 3.11; packaging and CI support 3.14.
- NumPy and SciPy are runtime dependencies.
- Cached linear propagation and unit-bolus responses replace repeated simulation
  and the unbounded dose-adjustment loop. Exact continuous integration is optional.
- Effect bolus results target the predicted peak, are unrounded, and may raise
  explicit baseline/horizon errors; doses differ from the old 90-second search.
- `effect_target()` now returns consistent rates, rather than mixing its initial
  bolus amount with subsequent rates. Existing consumers must update accordingly.
- Custom infusion periods, partial segments and negative-rate propagation are fixed.
- Schnider `k21` now divides the entire age-adjusted intercompartmental clearance
  by V2. This corrects a parenthesis error and changes Schnider trajectories.
  [Original PK publication](https://doi.org/10.1097/00000542-199805000-00006)
- Eleveld propofol `with_opiates()` retains per-second rate units and is idempotent.
- Added the Morse dexmedetomidine PK parameterization and simplified Eleveld 2025
  remimazolam arterial TCI model, with population warnings and source references.

Tests verify the legacy Euler recurrence independently, compare exact propagation
with an independent ODE solver and a known analytic solution, replay infusion
schedules, and check initial/top-up peak accuracy, state preservation, infeasible
baselines, cache changes and sourced model equations. These are numerical and
software checks, not clinical validation of a pump or patient dosing system.
