from copy import deepcopy

import numpy as np
import pytest

from PyTCI.models import propofol, remifentanil
from PyTCI.models.base import BaselineAboveTargetError, PeakNotFoundError


def state(patient):
    return (patient.x1, patient.x2, patient.x3, patient.xeo)


def simulate_peak(patient, dose, duration=10, horizon=3600, step=1):
    """Deliver the returned dose through the public simulation API."""
    patient = deepcopy(patient)
    peak = patient.xeo
    for _ in range(int(duration / step)):
        patient.giveoverseconds(dose / duration, step)
        peak = max(peak, patient.xeo)
    for _ in range(int((horizon - duration) / step)):
        patient.wait_time(step)
        peak = max(peak, patient.xeo)
    return peak


def test_reset_and_zero():
    patient = propofol.Marsh(80)
    patient.give_drug(200)
    patient.wait_time(30)
    patient.reset_concs({"ox1": 1, "ox2": 2, "ox3": 3, "oxeo": 4})
    assert state(patient) == (1, 2, 3, 4)
    patient.zero_comps()
    assert state(patient) == (0, 0, 0, 0)


@pytest.mark.parametrize("integrator", ["euler", "exact"])
@pytest.mark.parametrize(
    "factory",
    [
        lambda: propofol.Schnider(40, 70, 190, "m"),
        lambda: propofol.Marsh(70),
        lambda: propofol.Eleveld(35, 70, 170, "m"),
        lambda: remifentanil.Minto(40, 70, 170, "m"),
    ],
)
def test_initial_effect_bolus_reaches_actual_peak(factory, integrator):
    patient = factory()
    patient.set_integrator(integrator)
    original = state(patient)
    dose = patient.effect_bolus(4)
    assert state(patient) == original
    assert simulate_peak(
        patient, dose, step=0.25 if integrator == "exact" else 1
    ) == pytest.approx(4, rel=2e-5)
    assert patient.effect_bolus(8) == pytest.approx(2 * dose, rel=1e-12)


@pytest.mark.parametrize("integrator", ["euler", "exact"])
def test_top_up_accounts_for_future_baseline(integrator):
    patient = propofol.Marsh(70)
    patient.set_integrator(integrator)
    patient.give_drug(60)
    patient.wait_time(90)
    original = state(patient)
    dose = patient.effect_bolus_from_baseline(4)
    naive = (4 - patient.xeo) / patient.unit_bolus_peak()[0]
    assert dose != pytest.approx(naive, rel=0.01)
    assert patient.effect_bolus(4) == pytest.approx(dose)
    assert state(patient) == original
    assert simulate_peak(
        patient, dose, step=0.25 if integrator == "exact" else 1
    ) == pytest.approx(4, rel=2e-5)


def test_equal_current_ce_can_allow_a_top_up_when_baseline_is_falling():
    patient = propofol.Marsh(70)
    patient.xeo = 2
    dose = patient.effect_bolus_from_baseline(2)
    assert dose > 0
    assert simulate_peak(patient, dose) == pytest.approx(2)


def test_same_ce_different_residual_states_require_different_boluses():
    first = propofol.Marsh(70)
    second = deepcopy(first)
    first.xeo = second.xeo = 1
    first.x1, first.x2, first.x3 = 1, 3, 2
    second.x1, second.x2, second.x3 = 4, 5, 6
    assert first.effect_bolus_from_baseline(4) != pytest.approx(
        second.effect_bolus_from_baseline(4)
    )


@pytest.mark.parametrize("integrator", ["euler", "exact"])
def test_wait_reassess_when_existing_drug_predicts_overshoot(integrator):
    patient = propofol.Marsh(70)
    patient.set_integrator(integrator)
    patient.give_drug(300)
    assert patient.xeo == 0  # Future overshoot matters even before Ce rises.
    original = state(patient)
    with pytest.raises(BaselineAboveTargetError, match="wait and reassess"):
        patient.effect_bolus_from_baseline(2)
    assert state(patient) == original


@pytest.mark.parametrize("integrator", ["euler", "exact"])
def test_custom_bolus_duration(integrator):
    patient = propofol.Marsh(70)
    patient.set_integrator(integrator)
    dose = patient.effect_bolus(3, bolus_seconds=30)
    assert simulate_peak(patient, dose, duration=30) == pytest.approx(3, rel=3e-5)


def test_exact_peak_is_between_samples_and_cp_equals_ce():
    patient = propofol.Marsh(70)
    patient.set_integrator("exact")
    peak, seconds = patient.unit_bolus_peak()
    assert seconds != round(seconds)
    patient.giveoverseconds(0.1, 10)
    patient.wait_time(seconds - 10)
    assert patient.x1 == pytest.approx(patient.xeo, rel=1e-9)
    assert patient.xeo == pytest.approx(peak, rel=1e-9)


def test_peak_cache_tracks_changes_to_keo_and_rates():
    patient = propofol.Marsh(70)
    first = patient.effect_bolus(4)
    patient.keo *= 2
    second = patient.effect_bolus(4)
    assert second != pytest.approx(first)
    patient.k10 *= 2
    assert patient.effect_bolus(4) != pytest.approx(second)


def test_horizon_and_missing_effect_compartment():
    patient = propofol.Marsh(70)
    with pytest.raises(PeakNotFoundError):
        patient.effect_bolus(4, max_time=20)
    with pytest.raises(ValueError, match="positive keo"):
        propofol.Kataria(20, 6).effect_bolus(4)
    assert patient.effect_bolus(0) == 0


@pytest.mark.parametrize("target", [-1, float("nan"), float("inf")])
def test_invalid_target_preserves_state(target):
    patient = propofol.Marsh(70)
    original = state(patient)
    with pytest.raises(ValueError):
        patient.effect_bolus(target)
    assert state(patient) == original


def test_plasma_infusion_legacy_values_with_numeric_tolerance():
    patient = propofol.Marsh(70)
    assert patient.plasma_infusion(2, 60) == pytest.approx(
        [
            3.27269899102373,
            0.1453355022895698,
            0.14478000490919285,
            0.14422948797801816,
            0.1436839059972244,
            0.143143213884116,
        ],
        rel=1e-12,
    )


@pytest.mark.parametrize("integrator", ["euler", "exact"])
@pytest.mark.parametrize("period", [1, 10, 30])
def test_plasma_schedule_custom_period_and_remainder(integrator, period):
    planner = propofol.Marsh(70)
    planner.set_integrator(integrator)
    replay = deepcopy(planner)
    time = 65
    rates = planner.plasma_infusion(2, time, period)
    assert len(rates) == (time + period - 1) // period
    for index, rate in enumerate(rates):
        replay.giveoverseconds(rate, min(period, time - index * period))
        assert replay.x1 == pytest.approx(2, rel=1e-12)
    assert state(planner) == pytest.approx(state(replay), rel=1e-12)


def test_negative_plasma_rate_is_clamped_before_simulation():
    patient = propofol.Marsh(70)
    patient.give_drug(500)
    replay = deepcopy(patient)
    rates = patient.plasma_infusion(0, 35, 30)
    assert rates == [0, 0]
    replay.wait_time(35)
    assert state(patient) == pytest.approx(state(replay), rel=1e-12)


@pytest.mark.parametrize("integrator", ["euler", "exact"])
def test_effect_schedule_returns_rates_and_preserves_state(integrator):
    patient = propofol.Marsh(70)
    patient.set_integrator(integrator)
    original = state(patient)
    rates = patient.effect_target(4, 65, period=30)
    assert len(rates) == 3
    assert np.all(np.array(rates) >= 0)
    assert rates[0] == pytest.approx(patient.effect_bolus(4, bolus_seconds=30) / 30)
    assert state(patient) == original
    replay = deepcopy(patient)
    for index, rate in enumerate(rates):
        seconds = min(30, 65 - index * 30)
        for _ in range(seconds):
            replay.giveoverseconds(rate, 1)
            assert replay.xeo <= 4 + 1e-8
    assert simulate_peak(replay, 0) <= 4 + 1e-8


def test_effect_schedule_waits_and_restores_state_on_failure():
    patient = propofol.Marsh(70)
    patient.give_drug(300)
    original = state(patient)
    assert patient.effect_target(2, 60) == [0] * 6
    assert state(patient) == original
    with pytest.raises(PeakNotFoundError):
        patient.effect_target(4, 60, max_time=20)
    assert state(patient) == original
    assert patient.effect_target(0, 35, 30) == [0, 0]
    assert patient.effect_target(4, 0) == []


@pytest.mark.parametrize(
    "time,period", [(-1, 10), (60, 0), (2.5, 10), (60, 1.5), (True, 10)]
)
def test_schedule_validation(time, period):
    patient = propofol.Marsh(70)
    with pytest.raises(ValueError):
        patient.plasma_infusion(2, time, period)
