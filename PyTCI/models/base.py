"""Linear three-compartment PK models with an optional effect compartment."""

from functools import lru_cache
from math import isfinite
from numbers import Integral

import numpy as np
from scipy.linalg import expm
from scipy.optimize import brentq, minimize_scalar


class BaselineAboveTargetError(ValueError):
    """Existing drug already exceeds the requested future effect-site target.

    A nonnegative bolus cannot meet this constraint; wait and reassess.
    """


class PeakNotFoundError(ValueError):
    """The search horizon is too short to resolve the effect-site peak."""


def _nonnegative(value, name):
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return float(value)


def _seconds(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer number of seconds")
    if value < (1 if positive else 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return int(value)


@lru_cache(maxsize=256)
def _system(parameters):
    v1, k10, k12, k13, k21, k31, keo = parameters
    # x2 and x3 retain the original library's amount / V1 convention.
    # x1 and xeo are plasma and effect-site concentrations, respectively.
    a = np.array(
        [
            [-k10 - k12 - k13, k21, k31, 0],
            [k12, -k21, 0, 0],
            [k13, 0, -k31, 0],
            [keo, 0, 0, -keo],
        ],
        dtype=float,
    )
    b = np.array([1 / v1, 0, 0, 0])
    a.setflags(write=False)
    b.setflags(write=False)
    return a, b


@lru_cache(maxsize=1024)
def _transition(parameters, integrator, seconds):
    """Return Phi and Gamma for constant input, without inverting A."""
    a, b = _system(parameters)
    augmented = np.zeros((5, 5))
    if integrator == "exact":
        augmented[:4, :4] = a
        augmented[:4, 4] = b
        transition = expm(augmented * seconds)
    else:
        # Preserve give_drug(rate); wait_time(1), including dosing before decay.
        augmented[:4, :4] = np.eye(4) + a
        augmented[:4, 4] = augmented[:4, :4] @ b
        augmented[4, 4] = 1
        if np.any(augmented[:4, :4] < 0):
            raise ValueError(
                "Rates are too fast for one-second Euler steps; use exact integration"
            )
        transition = np.linalg.matrix_power(augmented, int(seconds))
    transition.setflags(write=False)
    return transition[:4, :4], transition[:4, 4]


def _advance(parameters, integrator, state, seconds, rate=0.0):
    phi, gamma = _transition(parameters, integrator, seconds)
    return phi @ state + gamma * rate


@lru_cache(maxsize=32)
def _unit_response(parameters, integrator, bolus_seconds, max_time):
    """Cache the entire one-unit response, including the bolus delivery period."""
    phi, gamma = _transition(parameters, integrator, 1)
    curve = np.zeros((max_time + 1, 4))
    state = np.zeros(4)
    for t in range(1, max_time + 1):
        state = phi @ state
        if t <= bolus_seconds:
            state = state + gamma / bolus_seconds
        curve[t] = state
    curve.setflags(write=False)
    return curve


def _unit_at(parameters, integrator, bolus_seconds, t):
    if t <= bolus_seconds:
        return _advance(parameters, integrator, np.zeros(4), t, 1 / bolus_seconds)
    delivered = _advance(
        parameters, integrator, np.zeros(4), bolus_seconds, 1 / bolus_seconds
    )
    return _advance(parameters, integrator, delivered, t - bolus_seconds)


@lru_cache(maxsize=128)
def _unit_peak(parameters, integrator, bolus_seconds, max_time):
    curve = _unit_response(parameters, integrator, bolus_seconds, max_time)
    index = int(np.argmax(curve[:, 3]))
    if index == max_time:
        raise PeakNotFoundError(
            "Unit-dose peak is outside max_time; increase the horizon"
        )
    t = float(index)
    if integrator == "exact":
        # dCe/dt = ke0 * (Cp - Ce). Exclude the equality at time zero.
        def slope(time):
            state = _unit_at(parameters, integrator, bolus_seconds, time)
            return state[0] - state[3]

        lower, upper = max(1e-9, index - 1), index + 1
        if slope(lower) > 0 and slope(upper) < 0:
            t = brentq(slope, lower, upper, xtol=1e-10)
        peak = _unit_at(parameters, integrator, bolus_seconds, t)[3]
    else:
        peak = curve[index, 3]
    if not isfinite(peak) or peak <= 0:
        raise ValueError(
            "No positive effect-site response; check keo and model parameters"
        )
    return float(peak), t


class Three:
    """Base model; all rate constants are in seconds after setup().

    x1 and xeo are concentrations in dose units/L. For backward compatibility,
    x2 and x3 are peripheral drug amounts divided by V1, rather than V2/V3.
    Euler integration retains the historical ten one-second bolus increments.
    set_integrator('exact') selects continuous infusion and matrix exponentials.
    """

    def setup(self):
        self.zero_comps()
        self.k10 /= 60
        self.k12 /= 60
        self.k13 /= 60
        self.k21 /= 60
        self.k31 /= 60
        self.keo /= 60
        self._is_setup = True
        self.integrator = "euler"

    def from_clearances(self):
        """Convert L/min clearances into rates, respecting an initialized model."""
        scale = 60 if getattr(self, "_is_setup", False) else 1
        self.k10 = self.Q1 / self.v1 / scale
        self.k12 = self.Q2 / self.v1 / scale
        self.k13 = self.Q3 / self.v1 / scale
        self.k21 = self.Q2 / self.v2 / scale
        self.k31 = self.Q3 / self.v3 / scale

    def set_integrator(self, method):
        """Select 'euler' (legacy) or 'exact' (continuous input); preserve state."""
        if method not in ("euler", "exact"):
            raise ValueError("integrator must be 'euler' or 'exact'")
        self.integrator = method

    def _parameters(self):
        parameters = (
            self.v1,
            self.k10,
            self.k12,
            self.k13,
            self.k21,
            self.k31,
            self.keo,
        )
        if not all(isfinite(p) and p >= 0 for p in parameters) or self.v1 == 0:
            raise ValueError(
                "Model parameters must be finite, rates nonnegative, and V1 positive"
            )
        return parameters

    def _state(self):
        values = (self.x1, self.x2, self.x3, self.xeo)
        if not all(isfinite(x) and x >= 0 for x in values):
            raise ValueError("Compartment states must be finite and nonnegative")
        return np.array(values, dtype=float)

    def _set_state(self, state):
        self.x1, self.x2, self.x3, self.xeo = map(float, state)

    def _duration(self, seconds):
        if self.integrator == "euler":
            return _seconds(seconds, "seconds")
        return _nonnegative(seconds, "seconds")

    def give_drug(self, drug_milligrams):
        """Add an instantaneous bolus in the chosen drug's dose units."""
        dose = _nonnegative(drug_milligrams, "dose")
        self._parameters()
        self.x1 += dose / self.v1

    def wait_time(self, time_seconds):
        """Advance the model without input (fractional seconds in exact mode)."""
        duration = self._duration(time_seconds)
        self._set_state(
            _advance(self._parameters(), self.integrator, self._state(), duration)
        )

    def reset_concs(self, old_conc):
        """Restore a dictionary containing ox1, ox2, ox3 and oxeo."""
        state = [old_conc[key] for key in ("ox1", "ox2", "ox3", "oxeo")]
        if not all(isfinite(x) and x >= 0 for x in state):
            raise ValueError("Compartment states must be finite and nonnegative")
        self._set_state(state)

    def zero_comps(self):
        """Empty all compartments."""
        self.x1 = self.x2 = self.x3 = self.xeo = 0.0

    def giveoverseconds(self, mgpersec, secs):
        """Deliver a constant rate in dose units/s, advancing the model."""
        rate = _nonnegative(mgpersec, "rate")
        duration = self._duration(secs)
        self._set_state(
            _advance(self._parameters(), self.integrator, self._state(), duration, rate)
        )
        return self.x1

    def tenseconds(self, mgpersec):
        """Deliver a constant rate for ten seconds."""
        return self.giveoverseconds(mgpersec, 10)

    def _bolus_arguments(self, target, bolus_seconds, max_time):
        target = _nonnegative(target, "target")
        bolus_seconds = _seconds(bolus_seconds, "bolus_seconds", positive=True)
        max_time = _seconds(max_time, "max_time", positive=True)
        if max_time <= bolus_seconds:
            raise ValueError("max_time must exceed bolus_seconds")
        parameters = self._parameters()
        if parameters[-1] <= 0:
            raise ValueError("Effect-site targeting requires a positive keo")
        return target, bolus_seconds, max_time, parameters

    def unit_bolus_peak(self, bolus_seconds=10, max_time=3600):
        """Return (effect-site concentration per dose unit, peak time in seconds)."""
        _, duration, horizon, parameters = self._bolus_arguments(
            0, bolus_seconds, max_time
        )
        return _unit_peak(parameters, self.integrator, duration, horizon)

    def effect_bolus(self, target, *, bolus_seconds=10, max_time=3600):
        """Return a peak-targeted bolus, accounting for all existing drug.

        Empty compartments: target / unit-dose peak. With residual drug: use
        effect_bolus_from_baseline(). Does not administer drug or mutate state.
        Dose units must match concentrations: mg/L (= ug/mL) for propofol;
        ug/L (= ng/mL) for remifentanil/dexmedetomidine. No dose rounding is applied.
        """
        target, duration, horizon, parameters = self._bolus_arguments(
            target, bolus_seconds, max_time
        )
        state = self._state()
        if np.any(state):
            return self.effect_bolus_from_baseline(
                target, bolus_seconds=duration, max_time=horizon
            )
        peak, _ = _unit_peak(parameters, self.integrator, duration, horizon)
        return target / peak

    def effect_bolus_from_baseline(self, target, *, bolus_seconds=10, max_time=3600):
        """Top up from the current full state using b(t) + D*h(t).

        Return min((target-b(t))/h(t)) over the search horizon. In exact mode,
        refine every sampled local minimum and every baseline peak. Euler mode
        constrains its one-second grid. BaselineAboveTargetError means wait and
        reassess; PeakNotFoundError means increase max_time. State is preserved.
        The result assumes fixed delivery duration and no subsequent infusion.
        """
        target, duration, horizon, parameters = self._bolus_arguments(
            target, bolus_seconds, max_time
        )
        state = self._state()
        if not np.any(state):
            return self.effect_bolus(target, bolus_seconds=duration, max_time=horizon)
        # Check the response horizon even when baseline feasibility fails.
        _unit_peak(parameters, self.integrator, duration, horizon)
        unit = _unit_response(parameters, self.integrator, duration, horizon)
        phi, _ = _transition(parameters, self.integrator, 1)
        baseline = np.empty_like(unit)
        baseline[0] = state
        for t in range(1, horizon + 1):
            baseline[t] = phi @ baseline[t - 1]

        baseline_peak = float(np.max(baseline[:, 3]))
        if self.integrator == "exact":

            def base_at(t):
                return _advance(parameters, self.integrator, state, t)

            differences = baseline[:, 0] - baseline[:, 3]
            crossings = np.flatnonzero((differences[:-1] > 0) & (differences[1:] <= 0))
            for index in crossings:
                t = brentq(lambda t: base_at(t)[0] - base_at(t)[3], index, index + 1)
                baseline_peak = max(baseline_peak, float(base_at(t)[3]))
        tolerance = 1e-12 * max(1.0, target)
        if baseline_peak > target + tolerance:
            raise BaselineAboveTargetError(
                f"Existing drug predicts Ce={baseline_peak:.8g} above target={target:.8g}; wait and reassess"
            )

        if baseline_peak >= target - tolerance and baseline_peak > state[3]:
            return 0.0
        if baseline[-1, 0] > baseline[-1, 3]:
            raise PeakNotFoundError(
                "Baseline is still rising at max_time; increase the horizon"
            )

        candidates = np.full(horizon + 1, np.inf)
        valid = unit[:, 3] > 0
        candidates[valid] = (target - baseline[valid, 3]) / unit[valid, 3]
        index = int(np.argmin(candidates))
        if index == horizon:
            raise PeakNotFoundError(
                "Top-up minimum is at max_time; increase the horizon"
            )
        dose = float(candidates[index])
        if self.integrator == "exact":

            def candidate(t):
                h = _unit_at(parameters, self.integrator, duration, t)[3]
                return (target - base_at(t)[3]) / h if h > 0 else np.inf

            minima = (
                np.flatnonzero(
                    (candidates[1:-1] <= candidates[:-2])
                    & (candidates[1:-1] <= candidates[2:])
                )
                + 1
            )
            for i in minima:
                result = minimize_scalar(
                    candidate,
                    bounds=(max(1e-9, i - 1), i + 1),
                    method="bounded",
                    options={"xatol": 1e-9},
                )
                if not result.success:
                    raise ValueError("Could not refine the top-up peak")
                dose = min(dose, float(result.fun))
        if not isfinite(dose) or dose < 0:
            raise ValueError("No finite nonnegative bolus satisfies the target")
        return dose

    @staticmethod
    def _segments(time, period):
        time = _seconds(time, "time")
        period = _seconds(period, "period", positive=True)
        return [period] * (time // period) + ([time % period] if time % period else [])

    def plasma_infusion(self, target, time, period=10):
        """Return rates in dose units/s and advance state by exactly time seconds.

        Each period targets its ending plasma concentration. The final segment
        is shorter if time is not divisible by period. Negative rates are clamped
        before applying them, allowing residual drug to wash out.
        """
        target = _nonnegative(target, "target")
        segments = self._segments(time, period)
        parameters = self._parameters()
        state = self._state()
        instructions = []
        for seconds in segments:
            phi, gamma = _transition(parameters, self.integrator, seconds)
            baseline = phi @ state
            if gamma[0] <= 0:
                raise ValueError("No positive plasma response to infusion")
            rate = max(0.0, float((target - baseline[0]) / gamma[0]))
            state = baseline + gamma * rate
            instructions.append(rate)
        self._set_state(state)
        return instructions

    def effect_target(self, target, time, period=10, *, max_time=3600):
        """Plan effect-site targeting; return ONLY rates in dose units/s.

        At each segment, top up to the predicted future peak, then replan from
        the resulting full state. If residual drug exceeds target, give zero.
        State is restored on success and failure. This assumes an unlimited
        delivery rate and is a simulation planner, not a pump controller.
        """
        target = _nonnegative(target, "target")
        segments = self._segments(time, period)
        original = self._state()
        instructions = []
        try:
            for seconds in segments:
                if target == 0:
                    dose = 0.0
                else:
                    try:
                        dose = self.effect_bolus_from_baseline(
                            target, bolus_seconds=seconds, max_time=max_time
                        )
                    except BaselineAboveTargetError:
                        dose = 0.0
                rate = dose / seconds
                self.giveoverseconds(rate, seconds)
                instructions.append(rate)
        finally:
            self._set_state(original)
        return instructions
