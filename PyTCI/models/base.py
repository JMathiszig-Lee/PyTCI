from numba import jit
# from numba import jitclass
from numba.experimental import jitclass
from numba import njit
from numba.typed import List as NumbaList
import numpy as np

@njit()
def jit_one_second(concs, consts):
    """ time steps must be one second for accurate modelling """
    # x1k10 : float
    # x1k12 : float
    # x1k13 : float
    # x2k21 : float
    # x3k31 : float

    # xk1e : float
    # xke1 : float

    # x1 : float
    # x2 : float
    # x3 : float
    # x0 : float

    # concs:NumbaList[float]
    # consts:NumbaList[float]

    x1k10 = concs[0] * consts[0]
    x1k12 = concs[0] * consts[1]
    x1k13 = concs[0] * consts[2]
    x2k21 = concs[1] * consts[3]
    x3k31 = concs[2] * consts[4]

    xk1e = concs[0] * consts[5]
    xke1 = concs[3] * consts[5]

    x1 = concs[0] + (x2k21 - x1k12 + x3k31 - x1k13 - x1k10)
    x2 = concs[1] + (x1k12 - x2k21)
    x3 = concs[2] + (x1k13 - x3k31)
    x0 = concs[3] + (xk1e - xke1)

    return (x1, x2, x3, x0)


class Three:
    """ Base 3 compartment model"""
    def __init__(self):
        self.x1 :float 
        self.x2 :float
        self.x3 :float
        self.xeo :float

        # declare variables so the linting doesnt get upset
        self.v1: float
        self.v2: float
        self.v3: float
        self.Q1: float
        self.Q2: float
        self.Q3: float
        self.k10: float
        self.k12: float
        self.k13: float
        self.k21: float
        self.k31: float
        self.keo: float

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

    def from_clearances(self):
        """
        Converts intercompartment clearances into rate constants
        Needed as we currently use them for the maths

        source http://www.pfim.biostat.fr/PFIM_PKPD_library.pdf page 8
        """
        self.k10 = self.Q1 / self.v1
        self.k12 = self.Q2 / self.v1
        self.k13 = self.Q3 / self.v1
        self.k21 = (self.k12 * self.v1) / self.v2
        self.k31 = (self.k13 * self.v1) / self.v3

    def give_drug(self, drug_milligrams):
        """ add bolus of drug to central compartment """
        self.x1 = self.x1 + drug_milligrams / self.v1

    def jit_wait_time(self, time_seconds):
        """ model distribution of drug between compartments over specified time period """
        constants = np.array([self.k10, self.k12, self.k13, self.k21, self.k31, self.keo])
        # @staticmethod
        # @njit
        # def jit_one_second(concs, consts):
        #     """ time steps must be one second for accurate modelling """
        #     # x1k10 : float
        #     # x1k12 : float
        #     # x1k13 : float
        #     # x2k21 : float
        #     # x3k31 : float

        #     # xk1e : float
        #     # xke1 : float

        #     # x1 : float
        #     # x2 : float
        #     # x3 : float
        #     # x0 : float

        #     # concs:NumbaList[float]
        #     # consts:NumbaList[float]

        #     x1k10 = concs[0] * consts[0]
        #     x1k12 = concs[0] * consts[1]
        #     x1k13 = concs[0] * consts[2]
        #     x2k21 = concs[1] * consts[3]
        #     x3k31 = concs[2] * consts[4]

        #     xk1e = concs[0] * consts[5]
        #     xke1 = concs[3] * consts[5]

        #     x1 = concs[0] + (x2k21 - x1k12 + x3k31 - x1k13 - x1k10)
        #     x2 = concs[1] + (x1k12 - x2k21)
        #     x3 = concs[2] + (x1k13 - x3k31)
        #     x0 = concs[3] + (xk1e - xke1)

        #     # return (x1, x2, x3, x0)

        for _ in range(time_seconds):
            concentrations = np.array([self.x1, self.x2, self.x3, self.xeo])
            self.x1, self.x2, self.x3, self.xe0 = jit_one_second(concentrations, constants)
            # jit_one_second(concentrations, constants)
    
    def wait_time(self, time_seconds):
        """ model distribution of drug between compartments over specified time period """

        def one_second(self):
            """ time steps must be one second for accurate modelling """
            x1k10 : float
            x1k12 : float
            x1k13 : float
            x2k21 : float
            x3k31 : float

            xk1e : float
            xke1 : float

            x1k10 = self.x1 * self.k10
            x1k12 = self.x1 * self.k12
            x1k13 = self.x1 * self.k13
            x2k21 = self.x2 * self.k21
            x3k31 = self.x3 * self.k31

            xk1e = self.x1 * self.keo
            xke1 = self.xeo * self.keo

            self.x1 = self.x1 + (x2k21 - x1k12 + x3k31 - x1k13 - x1k10)
            self.x2 = self.x2 + (x1k12 - x2k21)
            self.x3 = self.x3 + (x1k13 - x3k31)

            self.xeo = self.xeo + (xk1e - xke1)

        for _ in range(time_seconds):
            one_second(self)

    def reset_concs(self, old_conc):
        """ resets concentrations using python dictionary"""
        self.x1 = old_conc["ox1"]
        self.x2 = old_conc["ox2"]
        self.x3 = old_conc["ox3"]
        self.xeo = old_conc["oxeo"]

    def zero_comps(self):
        """ sets all compartment concentrations to 0 """
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.xeo = 0

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
            self.tenseconds(final_mgpersec)

            if final_mgpersec < 0:
                # do not allow for a negative drug dose
                final_mgpersec = 0

            old_conc = {
                "ox1": self.x1,
                "ox2": self.x2,
                "ox3": self.x3,
                "oxeo": self.xeo,
            }

            pump_instructions.append(final_mgpersec)

        return pump_instructions

    def effect_target(self, target: float, time: int, period: int = 10):
        """ returns list of infusion rates to maintain desired plasma concentration
        inputs:
        target: desired plasma concentration in units/ml
        time: infusion duration in seconds
        period: time in seconds for each chunk of pump instructions, defaults to 10

        returns:
        list of infusion rates in mg per second over period defined by user (or 10 if default)"""

        old_conc = {"ox1": self.x1, "ox2": self.x2, "ox3": self.x3, "oxeo": self.xeo}
        pump_instructions = []
        sections = round(time / period)

        # see how long we need to wait to allow ce to decrease
        wait_seconds = 0
        while self.xeo > target:
            self.wait_time(1)
            wait_seconds += 1

        for _ in range(round(wait_seconds / period)):
            pump_instructions.append(0)

        # reset the concentrations so we've not change the patient state
        self.reset_concs(old_conc)

        # trim pump instructions if it's longer than requested
        if len(pump_instructions) > sections:
            return pump_instructions[:sections]

        # this is nesscary as we need instructions in user definied increments
        self.wait_time(len(pump_instructions) * period)
        top_up = self.effect_bolus(target)
        pump_instructions.append(top_up)
        self.giveoverseconds((top_up / period), period)

        remaining_time = time - (len(pump_instructions) * period)

        pump_instructions += self.plasma_infusion(target, remaining_time, period)

        # final reset to make sure function doesn't change pateint state
        self.reset_concs(old_conc)

        return pump_instructions
