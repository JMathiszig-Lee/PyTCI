from copy import deepcopy
from math import exp

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from PyTCI.models import propofol, remifentanil
from PyTCI.models.base import Three


def state(patient):
    return np.array([patient.x1, patient.x2, patient.x3, patient.xeo])


def legacy_step(patient, rate=0):
    """Independent scalar recurrence from the original library."""
    x1, x2, x3, ce = state(patient)
    x1 += rate / patient.v1
    patient.x1 = (
        x1
        + x2 * patient.k21
        + x3 * patient.k31
        - x1 * (patient.k10 + patient.k12 + patient.k13)
    )
    patient.x2 = x2 + x1 * patient.k12 - x2 * patient.k21
    patient.x3 = x3 + x1 * patient.k13 - x3 * patient.k31
    patient.xeo = ce + patient.keo * (x1 - ce)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: propofol.Marsh(70),
        lambda: propofol.Schnider(40, 70, 170, "m"),
        lambda: remifentanil.Minto(40, 70, 170, "m"),
    ],
)
@pytest.mark.parametrize("seconds", [0, 1, 10, 60, 3600])
def test_cached_euler_matches_independent_scalar_recurrence(factory, seconds):
    patient = factory()
    patient.give_drug(100)
    patient.x2, patient.x3, patient.xeo = 2, 1, 0.5
    reference = deepcopy(patient)
    patient.giveoverseconds(0.3, seconds)
    for _ in range(seconds):
        legacy_step(reference, 0.3)
    assert state(patient) == pytest.approx(state(reference), rel=1e-11)


def test_exact_against_independent_ode_in_amount_coordinates():
    patient = propofol.Marsh(70)
    patient.set_integrator("exact")
    patient.give_drug(80)
    patient.x2, patient.x3, patient.xeo = 3, 2, 1
    initial = state(patient)
    initial[:3] *= patient.v1
    rate = 0.5

    def ode(t, values):
        a1, a2, a3, ce = values
        return [
            rate
            - a1 * (patient.k10 + patient.k12 + patient.k13)
            + a2 * patient.k21
            + a3 * patient.k31,
            a1 * patient.k12 - a2 * patient.k21,
            a1 * patient.k13 - a3 * patient.k31,
            patient.keo * (a1 / patient.v1 - ce),
        ]

    reference = solve_ivp(
        ode, (0, 123.45), initial, method="DOP853", rtol=1e-11, atol=1e-12
    ).y[:, -1]
    reference[:3] /= patient.v1
    patient.giveoverseconds(rate, 123.45)
    assert state(patient) == pytest.approx(reference, rel=1e-10)


def test_exact_handles_singular_matrix_and_known_one_compartment_solution():
    patient = Three()
    patient.v1 = 10
    patient.k10 = 0.6
    patient.k12 = patient.k13 = patient.k21 = patient.k31 = patient.keo = 0
    patient.setup()
    patient.set_integrator("exact")
    patient.giveoverseconds(1, 100)
    assert patient.x1 == pytest.approx(10 * (1 - exp(-1)))
    patient.wait_time(100)
    assert patient.x1 == pytest.approx(10 * (1 - exp(-1)) * exp(-1))


def test_clearance_update_keeps_units_state_and_integrator():
    patient = propofol.Eleveld(35, 70, 170, "m")
    patient.set_integrator("exact")
    patient.give_drug(100)
    original = state(patient)
    patient.with_opiates()
    assert patient.k10 == pytest.approx(patient.Q1 / patient.v1 / 60)
    assert patient.k31 == pytest.approx(patient.Q3 / patient.v3 / 60)
    assert state(patient) == pytest.approx(original)
    assert patient.integrator == "exact"
    rates = [patient.k10, patient.k12, patient.k13, patient.k21, patient.k31]
    patient.with_opiates()
    assert rates == [patient.k10, patient.k12, patient.k13, patient.k21, patient.k31]


def test_invalid_inputs_do_not_change_state():
    patient = propofol.Marsh(70)
    initial = state(patient)
    for call in [
        lambda: patient.give_drug(-1),
        lambda: patient.giveoverseconds(-1, 10),
        lambda: patient.wait_time(-1),
        lambda: patient.wait_time(1.5),
        lambda: patient.set_integrator("unknown"),
    ]:
        with pytest.raises(ValueError):
            call()
        assert state(patient) == pytest.approx(initial)
