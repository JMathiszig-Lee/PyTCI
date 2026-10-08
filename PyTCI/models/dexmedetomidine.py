import math
from PyTCI.models.base import Three


class Dexmed(Three):
    """base class for demedetomidine"""

    pass


class Hannivoort(Dexmed):
    def __init__(self, weight: int):
        """3 compartment dexmedetomidine Pk model

        Units:
        weight(kg)

        Reference:
        Hannivoort, L, et al
        Development of an Optimized Pharmacokinetic Model of Dexmedetomidine Using Target-controlled Infusion in Healthy Volunteers
        Anesthesiology 8 2015, Vol.123, 357-367.
        doi:10.1097/ALN.0000000000000740
        """

        self.v1 = 1.78 * (weight / 70)
        self.v2 = 30.3 * (weight / 70)
        self.v3 = 52.0 * (weight / 70)

        self.Q1 = 0.686 * ((weight / 70)) ** 0.75
        self.Q2 = 2.98 * (self.v2 / 30.3) ** 0.75
        self.Q3 = 0.602 * (self.v3 / 52.0) ** 0.75

        self.from_clearances()

        self.keo = 0

        self.setup()


class Dyck(Dexmed):
    def __init__(self, height: int):
        """

        Units:
        Height(cm)

        Reference:
        Dyck, JB, et al
        Computer-controlled infusion of intravenous dexmedetomidine hydrochloride in adult human volunteers
        Anesthesiology. 1993 May;78(5):821-8.
        PMID:8098191 DOI:10.1097/00000542-199305000-00003
        """

        self.v1 = 7.99
        self.v2 = 13.8
        self.v3 = 187

        self.Q1 = round((0.00791 * height) - 0.928, 4)
        self.Q2 = 2.26
        self.Q3 = 1.99

        self.from_clearances()

        self.keo = 0

        self.setup()


class Morse(Dexmed):
    """Morse, Cortinez & Anderson (2020) universal dexmedetomidine PK model.

    age: years, weight: kg, height: cm, sex: 'm'/'f'. Optional pma is
    postmenstrual age in weeks; default assumes birth at 40 weeks.
    Dose units: micrograms; Cp: micrograms/L (= ng/mL). No PD/keo was
    estimated in this model, so effect-site targeting is unavailable.

    Table 1 and equations (9)-(16), doi:10.3390/jcm9113480.
    Development population: 40.6 postmenstrual weeks to 70.8 years, 3.1-152 kg.
    """

    def __init__(self, age, weight, height, sex, *, pma=None):
        import warnings
        from PyTCI.weights.leanbodymass import fat_free_mass

        ffm = fat_free_mass(age, height, weight, sex)
        pma = 40 + age * 52 if pma is None else pma
        if not math.isfinite(pma) or pma <= 0:
            raise ValueError("pma must be finite and positive")
        if pma < 40.6 or age > 70.8 or not 3.1 <= weight <= 152:
            warnings.warn(
                "Covariates outside the Morse model development population",
                stacklevel=2,
            )
        nfm = ffm + 0.293 * (weight - ffm)
        nfm_reference = 56.1 + 0.293 * (70 - 56.1)
        volume_scale = nfm / nfm_reference
        clearance_scale = (ffm / 56.1) ** 0.75
        self.v1 = 25.2 * volume_scale
        self.v2 = 34.4 * volume_scale
        self.v3 = 65.4 * volume_scale
        # The maturation factor applies to elimination clearance, not Q2/Q3.
        self.Q1 = 0.897 * clearance_scale * pma / (52.4 + pma)
        self.Q2 = 1.68 * clearance_scale
        self.Q3 = 0.62 * clearance_scale
        self.keo = 0.0
        self.from_clearances()
        self.setup()
