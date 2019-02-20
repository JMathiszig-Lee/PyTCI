import warnings
from math import exp
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
    Age (years)
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

        # now covert to rate constants
        # source http://www.pfim.biostat.fr/PFIM_PKPD_library.pdf page 8

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
    Weight (kg)
    Age (years)

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


class Eleveld(Propofol):
    """Eleveld universal model

    Units:
    Height (cm)
    Weight (Kg)
    Age (years)

    Special methods for this model
    .venous()
    Switches from arterial(default) to arterial targerting

    .with_opiates()
    models co-administration with opiates

    Reference:

    """

    def __init__(self, age: int, weight: float, height: int, sex: str):
        if sex != "m" and sex != "f":
                raise ValueError(
                    "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :("
                    % sex
                )

        # post menstrual age
        pma = age * 52 + 40

        # constants from paper to help reduce transcioption errors
        theta01 = 6.28
        theta02 = 25.5
        theta03 = 273
        theta04 = 1.79
        theta05 = 1.81
        theta06 = 1.11
        theta07 = 0.191
        theta08 = 42.3
        theta09 = 9.06
        theta10 = -0.0156
        theta11 = -0.00286
        theta12 = 33.6
        theta13 = -0.0138
        theta14 = 68.3
        theta15 = 2.10
        theta16 = 1.30
        theta17 = 1.42
        theta18 = 0.68

        # al-sallami allometric scaling thing
        def alsallami(height, weight, sex):

            if sex == "m":
                alsal = 0.88 + (
                    0.12 / (1 + (age / 13.4) ** -12.7)
                ) * leanbodymass.janmahasation(height, weight, sex)
            else:
                alsal = 1.11 + (
                    (1 - 1.11) / (1 + (age / 7.1) ** -1.1)
                ) * leanbodymass.janmahasation(height, weight, sex)

            return alsal

        def ageing(i, age):
            """ ageing function"""
            return exp(i * (age - ageref))

        # sigmoid function
        def sigmoid(x, e50, y):
            """ sigmoid function from eleveld paper """
            sig = (x ** y) / ((x ** y) + (e50 ** y))
            return sig

        def central(i):
            """ central function """
            return sigmoid(i, theta12, 1)

        def clmat(j):
            """ returns central maturation """
            return sigmoid(pma, theta08, theta09)

        # q3 maturation
        q3mat = sigmoid(pma, theta14, 1)

        # opiate coeffecient, changed by .with_opiates()
        self.opiatesv3 = 1
        self.opiatescl = 1

        self.v1 = theta01 * (central(age) / central(ageref)) * exp(0.610)
        self.v2 = theta02 * (weight / weightref) * ageing(theta10, age) * exp(0.565)
        self.v3 = theta03 * alsallami(height, weight, sex) * opiatesv3 * exp(0.597)

        #clearance
        if sex == "m":
            self.q1 = theta04 * (weight/weightref)**0.75 * (q3mat / q3matref) * self.opiatescl * exp(0.265)
        else:   
            self.q1 = theta15 * (weight/weightref)**0.75 * (q3mat / q3matref) * self.opiatescl * exp(0.265)  

        self.q2 = theta05 * (self.v2 ** 0.75) * (1 + theta16 * (1 - q3mat)) * exp(0.346)
        self.q3 = theta06 * (self.v3 ** 0.75) * (q3mat / q3matref) * exp(0.209)

        self.keo = theta02 * ((weight/70) ** -0.25) * exp(0.565) 

        Propofol.setup(self)

        @classmethod
        def venous():
            """ switches the following parameters to target venous concentrations
            V1
            Ke0
            Q2
            """
            self.v1 = self.v1 * (1 + theta17 * (1 - central(weight)))
            self.keo = theta08 * ((weight/70) ** -0.25) * exp(0.565) 
            self.q2 = theta18 * self.q2

        @classmethod
        def with_opiates():
            """ switches the opiate parameters
            using this method indicates opiates are being administered concurrently
            """
            self.opiatesv3 = exp(theta13 * age)
            self.opiatescl = exp(theta11 * age)
