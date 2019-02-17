from PyTCI.weights import leanbodymass


class Remifentanil:
    """ Base Class for remifentanil models """

    # TODO this should probably be a generic 3 compartment model
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

    def give_drug(self, drug):
        """ add bolus of drug to central compartment """
        self.x1 = self.x1 + drug / self.v1

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
        
