import warnings
from ..weights import leanbodymass
from .base import Three


class Propofol(Three):
    """ Base Class for Propofol 3 compartment model """

    def reset_concs(self, old_conc):
        """ resets concentrations using python dictionary"""
        self.x1 = old_conc["ox1"]
        self.x2 = old_conc["ox2"]
        self.x3 = old_conc["ox3"]
        self.xeo = old_conc["oxeo"]

    def effect_bolus(self, target: float):
        """ determines size of bolus needed over 10 seconds to achieve target at ttpe """

        # store concentrations so we can reset after search
        old_conc = {"ox1": self.x1, "ox2": self.x2, "ox3": self.x3, "oxeo": self.xeo}

        ttpe = 90
        bolus_seconds = 10
        bolus = 10

        effect_error = 100
        while not -1 < effect_error < 1:
            mgpersec = bolus / bolus_seconds

            self.tenseconds(mgpersec)
            self.wait_time(ttpe - 10)

            effect_error = ((self.xeo - target) / target) * 100

            step = effect_error / -5
            bolus += step

            # reset concentrations
            self.reset_concs(old_conc)

        return round(mgpersec * 10, 2)

    def tenseconds(self, mgpersec: float):
        """ gives set amount of drug every second for 10 seconds """
        for _ in range(10):
            self.give_drug(mgpersec)
            self.wait_time(1)

        return self.x1

    def giveoverseconds(self, mgpersec: float, secs: float):
        """ gives set amount of drug every second for user defined period"""
        for _ in range(secs):
            self.give_drug(mgpersec)
            self.wait_time(1)

        return self.x1

    def plasma_infusion(self, target: float, time: int, period: int = 10):
        """ returns list of infusion rates to maintain desired plasma concentration
        inputs:
        target: desired plasma concentration in ug/min
        time: infusion duration in seconds
        period: time in seconds for each chunk of pump instructions, defaults to 10

        returns:
        list of infusion rates in mg per second over period defined by user (or 10 if default)"""

        old_conc = {"ox1": self.x1, "ox2": self.x2, "ox3": self.x3, "oxeo": self.xeo}
        sections = round(time / period)
        pump_instructions = []

        for _ in range(sections):

            first_cp = self.giveoverseconds(3, period)

            self.reset_concs(old_conc)

            second_cp = self.giveoverseconds(12, period)

            self.reset_concs(old_conc)

            gradient = (second_cp - first_cp) / 9
            offset = first_cp - (gradient * 3)
            final_mgpersec = (target - offset) / gradient
            if final_mgpersec < 0:
                # do not allow for a negative drug dose
                final_mgpersec = 0

            section_cp = self.tenseconds(final_mgpersec)
            old_conc = {
                "ox1": self.x1,
                "ox2": self.x2,
                "ox3": self.x3,
                "oxeo": self.xeo,
            }

            pump_instructions.append(final_mgpersec)

        return pump_instructions


class Schnider(Propofol):
    """ Implementation of the schnider model """

    # UNITS:
    # age: years
    # weight: kilos
    # height: cm
    # sex: 'm' or 'f'

    def __init__(self, age, weight, height, sex):

        lean_body_mass = leanbodymass.james(height, weight, sex)

        self.v1 = 4.27
        self.v2 = 18.9 - 0.391 * (age - 53)
        self.v3 = 238

        self.k10 = (
            0.443
            + 0.0107 * (weight - 77)
            - 0.0159 * (lean_body_mass - 59)
            + 0.0062 * (height - 177)
        )
        self.k12 = 0.302 - 0.0056 * (age - 53)
        self.k13 = 0.196
        self.k21 = 1.29 - 0.024 * (age - 53) / self.v2
        self.k31 = 0.0035

        self.keo = 0.456

        Propofol.setup(self)


class Marsh(Propofol):
    """ Marsh 3 compartment Propofol Pk Model

    Units required:
    weight (kg)

    Returns:
    """

    def __init__(self, weight: float):

        self.v1 = 0.228 * weight
        self.v2 = 0.463 * weight
        self.v3 = 2.893 * weight

        self.k10 = 0.119
        self.k12 = 0.112
        self.k13 = 0.042
        self.k21 = 0.055
        self.k31 = 0.0031

        self.keo = 0.26

        Propofol.setup(self)


class Kataria(Propofol):
    """Kataria paediatric model
    Intended age range 3-11

    Units:
    Age
    Weight (kg)"""

    def __init__(self, weight: float, age: float):
        if not 2.99 < age < 12:
            warnings.warn("Age out of range of model validation (3-11)")

        self.v1 = 0.38 * weight
        self.v2 = (0.59 * weight) + (3.1 * age) - 13
        self.v3 = 6.12 * weight

        self.Q1 = 0.037 * weight
        self.Q2 = 0.063 * weight
        self.Q3 = 0.025 * weight

        Propofol.from_clearances(self)

        self.keo = 0

        Propofol.setup(self)


class Paedfusor(Propofol):
    """Paedfusor paediatric model
    Intended age range 1-12

    Units:
    Weight (kg)

    Reference:
    Absalom, A, Kenny, G
    BJA: British Journal of Anaesthesia, Volume 95, Issue 1, 1 July 2005, Pages 110,
    https://doi.org/10.1093/bja/aei567
    """

    def __init__(self, weight: float, age: float):

        if age < 1:
            warnings.warn("age below that for which model is intended")
        elif age > 12:
            warnings.warn("Warning: Patient older than intended for model")

        self.v1 = 0.46 * weight
        self.v2 = 0.95 * weight
        self.v3 = 5.85 * weight

        self.k10 = 0.1527 * (weight ** (-0.3))
        self.k12 = 0.114
        self.k13 = 0.042
        self.k21 = 0.055
        self.k31 = 0.0033

        self.keo = 0

        Propofol.setup(self)
