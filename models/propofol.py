from ..weights import leanbodymass


class Propofol:
    """ Base Class for Propofol 3 compartment model """

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

    def __repr__(self):
        # TODO this should probably be a dictionary
        return "PatientState(x1=%f, x2=%f, x3=%f, xeo=%f)" % (
            self.x1,
            self.x2,
            self.x3,
            self.xeo,
        )


class Schnider(Propofol):
    """ Implementation of the schnider model """

    # UNITS:
    # age: years
    # weight: kilos
    # height: cm
    # sex: 'm' or 'f'

    def __init__(self, age, weight, height, sex):
        # Initial concentration is zero in all components
        self.x1 = 0.0
        self.x2 = 0.0
        self.x3 = 0.0
        self.xeo = 0.0

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

        # divide by 60 as we will be working in seconds
        self.k10 /= 60
        self.k12 /= 60
        self.k13 /= 60
        self.k21 /= 60
        self.k31 /= 60
        self.keo /= 60


class PatientState2:
    # age: years
    # weight: kilos
    # height: cm
    # sex: 'm' or 'f'
    def __init__(self, age, weight, height, sex, params):
        self.params = params

        lean_body_mass = self.__lean_body_mass(weight, height, sex)

        self.v1 = (
            (params["v1a"] * 50) - params["v1b"] * (age - (params["age_offset"]) * 100)
        ) * (params["v1c"] * (lean_body_mass - (params["lbm_offset"] * 100)))
        self.v2 = params["v2a"] * lean_body_mass * 2
        self.v3 = params["v3a"] * weight * 5

        # Initial concentration is zero in all components
        self.x1 = 0.0
        self.x2 = 0.0
        self.x3 = 0.0

        self.k10 = (params["k10a"] * self.v1) / 60
        self.k12 = params["k12"] / 60
        self.k13 = params["k13"] / 60
        self.k21 = (params["k12"] * (self.v1 / self.v2)) / 60
        self.k31 = (params["k13"] * (self.v1 / self.v3)) / 60

        self.keo = 0.456 / 60

        self.xeo = 0.0

    def give_drug(self, drug_milligrams):
        self.x1 = self.x1 + drug_milligrams / self.v1

    def wait_time(self, time_seconds):

        x1k10 = self.x1 * self.k10
        x1k12 = self.x1 * self.k12
        x1k13 = self.x1 * self.k13
        x2k21 = self.x2 * self.k21
        x3k31 = self.x3 * self.k31

        self.x1 = self.x1 + (x2k21 - x1k12 + x3k31 - x1k13 - x1k10) * time_seconds
        self.x2 = self.x2 + (x1k12 - x2k21) * time_seconds
        self.x3 = self.x3 + (x1k13 - x3k31) * time_seconds

    def __lean_body_mass(self, weight, height, sex):
        if sex != "m" and sex != "f":
            raise ValueError(
                "Unknown sex '%s'. This algorithm can only handle 'm' and 'f'. :(" % sex
            )

        if sex == "m":
            return (0.32819 * weight) + (0.33929 * height) - 29.5336
        else:
            return (0.29569 * weight) + (0.41813 * height) - 43.2933

    def __repr__(self):
        return "PatientState(x1=%f, x2=%f, x3=%f, xeo=%f)" % (
            self.x1,
            self.x2,
            self.x3,
            self.xeo,
        )


class MarshState:
    def __init__(self, age, weight, height, sex, params):
        self.params = params

        self.v1 = params["v1a"] * weight
        self.v2 = params["v2a"] * weight
        self.v3 = params["v3a"] * weight

        # Initial concentration is zero in all components
        self.x1 = 0.0
        self.x2 = 0.0
        self.x3 = 0.0

        self.k10 = params["k10a"] / 60
        self.k12 = params["k12"] / 60
        self.k13 = params["k13"] / 60
        self.k21 = params["k12"] / 60
        self.k31 = params["k13"] / 60

    def give_drug(self, drug_milligrams):
        self.x1 = self.x1 + drug_milligrams / self.v1

    def wait_time(self, time_seconds):

        x1k10 = self.x1 * self.k10
        x1k12 = self.x1 * self.k12
        x1k13 = self.x1 * self.k13
        x2k21 = self.x2 * self.k21
        x3k31 = self.x3 * self.k31

        self.x1 = self.x1 + (x2k21 - x1k12 + x3k31 - x1k13 - x1k10) * time_seconds
        self.x2 = self.x2 + (x1k12 - x2k21) * time_seconds
        self.x3 = self.x3 + (x1k13 - x3k31) * time_seconds

    @staticmethod
    def with_marsh_params(age, weight, height, sex):
        params = MarshState.marsh_params()

        return MarshState(age, weight, height, sex, params)

    @staticmethod
    def marsh_params():
        params = {
            "v1a": 0.228,
            "v2a": 0.463,
            "v3a": 2.893,
            "k10a": 0.119,
            "k12": 0.112,
            "k13": 0.042,
            "k21": 0.055,
            "k31": 0.0033,
            "keo": 0.26,
        }

        return params

    def __repr__(self):
        return "PatientState(x1=%f, x2=%f, x3=%f)" % (self.x1, self.x2, self.x3)
