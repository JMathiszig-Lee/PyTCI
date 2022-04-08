from PyTCI.weights import leanbodymass
from .base import Three
from math import exp


class Remifentanil(Three):
    """Base Class for remifentanil models"""

    pass


class Minto(Remifentanil):
    def __init__(self, age, weight, height, sex):

        lean_body_mass = leanbodymass.james(height, weight, sex)

        self.v1 = 5.1 - 0.0201 * (age - 40) + 0.072 * (lean_body_mass - 55)
        self.v2 = 9.82 - 0.0811 * (age - 40) + 0.108 * (lean_body_mass - 55)
        self.v3 = 5.42

        self.k10 = (
            2.6 - 0.0162 * (age - 40) + 0.0191 * (lean_body_mass - 55)
        ) / self.v1
        self.k12 = (2.05 - 0.0301 * (age - 40)) / self.v1
        self.k13 = (0.076 - 0.00113 * (age - 40)) / self.v1
        self.k21 = self.k12 * (self.v1 / self.v2)
        self.k31 = self.k13 * (self.v1 / self.v3)

        self.keo = 0.595 - 0.007 * (age - 40)

        Remifentanil.setup(self)


class Eleveld(Remifentanil):
    """
    Eleveld universal remifentanil model

    Units:
    Age (years)
    Weight (Kg)

    Reference:
    An Allometric Model of Remifentanil Pharmacokinetics and Pharmacodynamics.
    Eleveld DJ, Proost JH, Vereecke H, Absalom AR, Olofsen E, Vuyk J, Struys MMRF.
    Anesthesiology. 2017 Jun;126(6):1005-1018.
    doi: 10.1097/ALN.0000000000001634.
    """

    def __init__(self, age, weight, height, sex):
        def ageing(i, age):
            """ageing function"""
            return exp(i * (age - 35))

        def sigmoid(x, e50, y):
            """sigmoid function from eleveld paper"""
            sig = (x ** y) / ((x ** y) + (e50 ** y))
            return sig

        # constants from paper
        v1ref = 5.81
        v2ref = 8.82
        v3ref = 5.03

        clref = 2.58
        q2ref = 1.72
        q3ref = 0.124

        Θ1 = 2.88
        Θ2 = -0.00554
        Θ3 = -0.00327
        Θ4 = -0.0315
        Θ5 = 0.470
        Θ6 = -0.0260

        ffm = leanbodymass.alsallami(age, height, weight, sex)
        ffmref = leanbodymass.alsallami(35, 170, 70, "m")
        Fsize = ffm / ffmref

        mat = sigmoid(weight, Θ1, 2)
        matref = sigmoid(70, Θ1, 2)
        Fmat = mat / matref

        # define constant for sex
        if sex == "m":
            Fsex = 1
        elif sex == "f":
            Fsex = 1 + Θ5 * sigmoid(age, 12, 6) * (1 - sigmoid(age, 45, 6))

        self.v1 = v1ref * Fsize * ageing(Θ2, age)
        self.v2 = v2ref * Fsize * ageing(Θ3, age) * Fsex
        self.v3 = v3ref * Fsize * ageing(Θ4, age) * exp(Θ6 * (weight - 70))

        self.Q1 = clref * Fsize ** 0.75 * Fmat * Fsex * ageing(Θ3, age)
        self.Q2 = q2ref * (self.v2 / v2ref) ** 0.75 * ageing(Θ2, age) * Fsex
        self.Q3 = q3ref * (self.v3 / v3ref) ** 0.75 * ageing(Θ2, age)

        self.keo = 1.09 * ageing(-0.0289, age)

        self.from_clearances()
        self.setup()
