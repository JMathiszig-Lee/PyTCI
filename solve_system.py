import numpy as np
from scipy.optimize import basinhopping

from patient_state import PatientState


def solve():
    starting_params = PatientState.schnider_params()

    params_array = convert_params_structure_to_vector(starting_params)

    result = basinhopping(find_lsq_for_all_patients, params_array)
    return result.x


def get_patients():
    return [{
        'age': 60,
        'expected_result': 0,
        'weight': 70,
        'height': 180,
        'sex': 'm'
    }]


def convert_vector_to_params_structure(params_vector):
    # ToDo: need to construct params object in a well-defined way
    pass


def convert_params_structure_to_vector(params):
    # ToDo: order of dictionary items is not well defined
    params_list = [v for k, v in params.items()]
    return np.array(params_list)


def find_lsq_for_all_patients(params_vector):
    params = convert_vector_to_params_structure(params_vector)
    total_lsq = 0
    for patient in get_patients():
        result = solve_for_patient(patient, params)
        residual = result - patient['expected_result']
        total_lsq += residual ** 2


def solve_for_patient(patient, params):
    patient = PatientState(patient['age'], patient['weight'], patient['height'], patient['sex'], params)
    patient.give_drug(92.60001)
    for t in range(130):
        patient.wait_time(1)
    return patient.x1


result = solve()
print result
