"""Parent-drug arterial remimazolam models; doses in mg, concentrations in mg/L."""

from math import exp, isfinite
import warnings

from .base import Three


class Remimazolam(Three):
    """Base class for remimazolam models."""


class Eleveld(Remimazolam):
    """Eleveld et al. (2025), simplified TCI equations for normal hepatic function.

    age: years; weight: kg; sex: 'm'/'f'; opioids: coadministration.
    Uses the MOAA/S effect compartment from the paper's simplified TCI model.
    Cp/Ce are mg/L (= ug/mL), doses mg. Predicts parent-drug arterial
    concentrations, not BIS, MOAA/S scores, venous concentrations, CNS7054
    tolerance, or the ICU/ECMO extensions of the full published PK-PD model.

    Source: doi:10.1016/j.bja.2025.02.038, simplified equations on pp. 210-211.
    Development population: ages 6-93 years, weights 21-171 kg.
    """

    def __init__(self, age, weight, sex, *, opioids=False):
        if not isfinite(age) or age < 0 or not isfinite(weight) or weight <= 0:
            raise ValueError(
                "age must be finite and nonnegative; weight finite and positive"
            )
        if sex not in ("m", "f"):
            raise ValueError("sex must be 'm' or 'f'")
        if not isinstance(opioids, bool):
            raise ValueError("opioids must be a bool")
        if not 6 <= age <= 93 or not 21 <= weight <= 171:
            warnings.warn(
                "Covariates outside the Eleveld remimazolam development population",
                stacklevel=2,
            )
        size = weight / 70
        female = sex == "f"
        self.v1 = size * 4.30730
        self.v2 = size * 12.2994
        self.v3 = size * 18.6411 * exp(0.00730817 * (age - 35) + 0.287037 * female)
        self.Q1 = size**0.75 * 1.11977 * exp(0.162802 * female - 0.139340 * opioids)
        self.Q2 = size**0.75 * 1.45260
        self.Q3 = (self.v3 / 18.6411) ** 0.75 * 0.297838
        self.keo = 0.298269
        self.from_clearances()
        self.setup()
