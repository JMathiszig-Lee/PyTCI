import warnings
from ..weights import leanbodymass


class Propofol:
    """ Base Class for Propofol 3 compartment model """
    def setup(self):

        # Initial concentration is zero in all components
        self.x1 = 0.0
        self.x2 = 0.0
        self.x3 = 0.0
        self.xeo = 0.0

        # divide by 60 as we will be working in seconds
        self.k10 /= 60
        self.k12 /= 60
        self.k13 /= 60
        self.k21 /= 60
        self.k31 /= 60
        self.keo /= 60

    def give_drug(self, drug_milligrams):
        """ add bolus of drug to central compartment """
        self.x1 = self.x1 + drug_milligrams / self.v1

    def wait_time(self, time_seconds):
        """ model distribution of drug between compartments over specified time period """
        x1k10 = self.x1 * self.k10
        x1k12 = self.x1 * self.k12
        x1k13 = self.x1 * self.k13
        x2k21 = self.x2 * self.k21
        x3k31 = self.x3 * self.k31

        xk1e = self.x1 * self.keo
        xke1 = self.xeo * self.keo

        self.x1 = self.x1 + (x2k21 - x1k12 + x3k31 - x1k13 - x1k10) * time_seconds
        self.x2 = self.x2 + (x1k12 - x2k21) * time_seconds
        self.x3 = self.x3 + (x1k13 - x3k31) * time_seconds

        self.xeo = self.xeo + (xk1e - xke1) * time_seconds


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

        #now covert to rate constants
        #source http://www.pfim.biostat.fr/PFIM_PKPD_library.pdf page 8

        self.k10 = self.Q1 / self.v1 
        self.k12 = self.Q2 / self.v1
        self.k13 = self.Q3 / self.v1
        self.k21 = (self.k12 * self.v1) / self.v2
        self.k31 = (self.k13 * self.v1) / self.v3

        self.keo = 0

        Propofol.setup(self)

class Paedfusor(Propofol):
    """Paedfusor paediatric model
    Intended age range 1-12

    Units:
    Weight (kg)"""

    def __init__(self, weight: float, age: float):

        if age < 1:
            warnings.warn("age below that for which model is intended")
        elif age > 12:
            warnings.warn("Warning: Patient older than intended for model")

        self.v1 = 0.46 * weight
        self.v2 = 0.95 * weight
        self.v3 = 5.85 * weight


        i = -0.3
        self.k10 = 0.153 * (weight ** i)
        
        self.k12 = 0.114
        self.k13 = 0.042
        self.k21 = 0.055
        self.k31 = 0.0033

        self.keo = 0

        Propofol.setup(self)