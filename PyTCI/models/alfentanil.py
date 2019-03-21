from .base import Three


class Alfentanil(Three):
    """base Alfentanil class"""

    pass


class Maitre(Alfentanil):
    def __init__(self, age, weight, height, sex):

        if sex == "m":
            self.v1 = 0.111 * weight
        elif sex == "f":
            self.v1 = 0.128 * weight
        else:
            raise ValueError("Unknown value for sex")

        self.k12 = 0.104
        self.k13 = 0.017
        self.k21 = 0.0673
        self.k31 = 0.0126
        self.q1 = 0.356

        if age > 40:
            self.k31 = 0.0126 - (0.000113 * (age - 40))
            self.q1 = 0.356 - (0.00269 * (age - 40))

        # calulated stuff as source paper gives mix of clearance and rate constants
        self.k10 = self.q1 / self.v1
        self.v2 = self.v1 * (self.k12 / self.k21)
        self.v3 = self.v1 * (self.k13 / self.k31)

        self.keo = 0.77
        self.setup()
