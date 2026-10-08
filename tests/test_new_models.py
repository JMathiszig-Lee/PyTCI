from math import exp

import pytest

from PyTCI.models import dexmedetomidine, remimazolam
from PyTCI.weights.leanbodymass import fat_free_mass


def test_remimazolam_reference_matches_published_simplified_equations():
    patient = remimazolam.Eleveld(35, 70, "m")
    assert patient.v1 == 4.30730
    assert patient.v2 == 12.2994
    assert patient.v3 == 18.6411
    assert patient.Q1 == 1.11977
    assert patient.Q2 == 1.45260
    assert patient.Q3 == 0.297838
    assert patient.keo == pytest.approx(0.298269 / 60)
    assert patient.k21 == pytest.approx(1.45260 / 12.2994 / 60)


def test_remimazolam_covariates_match_published_simplified_equations():
    patient = remimazolam.Eleveld(70, 140, "f", opioids=True)
    expected_v3 = 2 * 18.6411 * exp(0.00730817 * 35 + 0.287037)
    assert patient.v1 == pytest.approx(2 * 4.30730)
    assert patient.v3 == pytest.approx(expected_v3)
    assert patient.Q1 == pytest.approx(2**0.75 * 1.11977 * exp(0.162802 - 0.139340))
    assert patient.Q3 == pytest.approx((expected_v3 / 18.6411) ** 0.75 * 0.297838)
    patient.set_integrator("exact")
    dose = patient.effect_bolus(0.8)
    patient.giveoverseconds(dose / 10, 10)
    peak = patient.xeo
    for _ in range(3590):
        patient.wait_time(1)
        peak = max(peak, patient.xeo)
    assert peak == pytest.approx(0.8, rel=2e-5)


@pytest.mark.parametrize(
    "args", [(-1, 70, "m"), (35, 0, "m"), (35, 70, "x"), (float("nan"), 70, "m")]
)
def test_remimazolam_invalid_covariates(args):
    with pytest.raises(ValueError):
        remimazolam.Eleveld(*args)


@pytest.mark.parametrize(
    "age,weight,height,sex", [(20, 70, 175, "m"), (1, 10, 75, "m"), (40, 120, 165, "f")]
)
def test_morse_matches_published_table_1_and_covariate_equations(
    age, weight, height, sex
):
    patient = dexmedetomidine.Morse(age, weight, height, sex)
    bmi = weight / (height / 100) ** 2
    if sex == "m":
        ffm = (
            (0.88 + 0.12 / (1 + (age / 13.4) ** -12.7))
            * 9270
            * weight
            / (6680 + 216 * bmi)
        )
    else:
        ffm = (
            (1.11 - 0.11 / (1 + (age / 7.1) ** -1.1))
            * 9270
            * weight
            / (8780 + 244 * bmi)
        )
    nfm = ffm + 0.293 * (weight - ffm)
    reference_nfm = 56.1 + 0.293 * (70 - 56.1)
    clearance_scale = (ffm / 56.1) ** 0.75
    pma = age * 52 + 40
    assert patient.v1 == pytest.approx(25.2 * nfm / reference_nfm)
    assert patient.v2 == pytest.approx(34.4 * nfm / reference_nfm)
    assert patient.v3 == pytest.approx(65.4 * nfm / reference_nfm)
    assert patient.Q1 == pytest.approx(0.897 * clearance_scale * pma / (52.4 + pma))
    assert patient.Q2 == pytest.approx(1.68 * clearance_scale)
    assert patient.Q3 == pytest.approx(0.62 * clearance_scale)
    assert patient.keo == 0
    with pytest.raises(ValueError, match="positive keo"):
        patient.effect_bolus(1)
    rates = patient.plasma_infusion(1, 60)
    assert all(rate >= 0 for rate in rates)
    assert patient.x1 == pytest.approx(1)


def test_morse_uses_normal_fat_mass_and_pma_for_maturation():
    patient = dexmedetomidine.Morse(0, 3.6, 50, "m", pma=40.6)
    ffm = 0.88 * 9270 * 3.6 / (6680 + 216 * (3.6 / 0.5**2))
    scale = (ffm + 0.293 * (3.6 - ffm)) / (56.1 + 0.293 * 13.9)
    assert patient.v1 == pytest.approx(25.2 * scale)
    assert patient.Q1 == pytest.approx(0.897 * (ffm / 56.1) ** 0.75 * 40.6 / 93.0)
    older = dexmedetomidine.Morse(0, 3.6, 50, "m", pma=60)
    assert older.Q1 > patient.Q1
    assert older.Q2 == patient.Q2
    assert older.v1 == patient.v1


def test_new_model_population_warnings():
    with pytest.warns(UserWarning, match="development population"):
        remimazolam.Eleveld(3, 15, "f")
    with pytest.warns(UserWarning, match="development population"):
        dexmedetomidine.Morse(80, 160, 180, "m")
    with pytest.raises(ValueError, match="pma"):
        dexmedetomidine.Morse(1, 10, 75, "m", pma=0)


def test_unrounded_ffm_and_neonatal_limit():
    assert fat_free_mass(0, 50, 3.6, "m") > 0
    assert fat_free_mass(0, 50, 3.6, "f") > 0
    expected = (
        (0.88 + 0.12 / (1 + (35 / 13.4) ** -12.7))
        * 9270
        * 70
        / (6680 + 216 * (70 / 1.75**2))
    )
    assert fat_free_mass(35, 175, 70, "m") == pytest.approx(expected, rel=1e-12)
