from scipy.optimize import fsolve
# from scipy.optimize import odeint
import math

from scipy.integrate import odeint

from patient_state import PatientState


def solve():
    starting_params = {
            'k10a': 0.443,
            'k10b': 0.0107,
            'k10c': -0.0159,
            'k10d': 0.0062,
            'k12a': 0.302,
            'k12b': -0.0056,
            'k13a': 0.196,
            'k21a': 1.29,
            'k21b': -0.024,
            'k21c': 18.9,
            'k21d': -0.391,
            'k31a': 0.0035,
            'keo': 0.456,
            'weightoffset': 77,
            'lbmoffset': 59,
            'ageoffset': 53,
            'heightoffset': 177
        }



def rate_equations(params):
    for patient in patients:
        result = solve_for_patient(patient, params)
        diff = (result - expected_result) ** 2


def solve_for_patient(params):
    patient = PatientState(50, 70, 180, "m", params)
    print "Initial state: " + str(patient)

    patient.give_drug(92.60001)
    print "After giving drug: " + str(patient)

    for t in range(130):
        patient.wait_time(1)
        print "After 1 sec: " + str(patient)

    return patient.x1

# scipy.integrate.odeint
#
#
# def equations(p):
#     x, y = p
#     return x+y**2-4, math.exp(x) + x*y - 3
#
# def solve():
#
# x, y = fsolve(equations, (1, 1))
#
# print equations((x, y))
#
