import warnings
from ..weights import leanbodymass
from .base import Three


class Propofol(Three):
    """ Base Class for Propofol 3 compartment model """

    def effect_bolus(self, target: float):
        """ determines size of bolus needed over 10 seconds to achieve target at ttpe """

        # store concentrations so we can reset after search
        old_conc = {"ox1": self.x1, "ox2": self.x2, "ox3": self.x3, "oxeo": self.xeo}

        ttpe = 90
        bolus_seconds = 10
        bolus = 10

        effect_error = 100
        while not -5 < effect_error < 5:
            mgpersec = bolus / bolus_seconds
            for _ in range(10):
                self.give_drug(mgpersec)
                self.wait_time(1)
            self.wait_time(80)
            effect_error = ((self.xeo - target) / target) * 100
            step = effect_error / -1
            bolus += step
            bolus = round(bolus, 2)

            print(effect_error, bolus, step, self.xeo)
            # reset concentrations
            reset_concs(old_conc)

        bolus_needed = mgpersec * 10

        return bolus_needed

    def reset_concs(self, old_conc):
        """ resets concentrations using python dictionary"""
        self.x1 = old_conc["ox1"]
        self.x2 = old_conc["ox2"]
        self.x3 = old_conc["ox3"]
        self.xeo = old_conc["oxeo"]

    def plasma_infusion(self, target: float, time: int):
        """ returns list of infusion rates to maintain desired plasma concentration
        inputs:
        target: desired plasma concentration in ug/min
        time: infusion duration in seconds

        returns:
        list of infusion rates over 10 seconds"""

        old_conc = {"ox1": self.x1, "ox2": self.x2, "ox3": self.x3, "oxeo": self.xeo}
        sections = round(time / 10)
        pump_instructions = []

        def tenseconds(mgpersec: float):
            """ gives set amount of drug every second for 10 seconds """
            for _ in range(10):
                self.give_drug(mgpersec)
                self.wait_time(1)

            return self.x1

        for _ in range(sections):

            first_cp = tenseconds(3)

            self.reset_concs(old_conc)

            second_cp = tenseconds(12)

            self.reset_concs(old_conc)

            gradient = (second_cp - first_cp) / 9
            offset = first_cp - (gradient * 3)
            print("gradient:", gradient)
            print("offset:", offset)
            #final_mgpersec = (target / gradient) - offset
            final_mgpersec = (target - offset) / gradient
            section_cp = tenseconds(final_mgpersec)
            old_conc = {
                "ox1": self.x1,
                "ox2": self.x2,
                "ox3": self.x3,
                "oxeo": self.xeo,   
            }

            print(" ")
            pump_instructions.append((final_mgpersec, section_cp))
            print(3, first_cp)
            print(12, second_cp)
            print(final_mgpersec, section_cp)

        print(pump_instructions)


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
