from PyTCI.weights import leanbodymass
from .base import Three


class Remifentanil(Three):
    """ Base Class for remifentanil models """

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
