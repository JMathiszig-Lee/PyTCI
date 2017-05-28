import numpy as np
from scipy.optimize import basinhopping

from patient_state import PatientState

from csvreader import read_patient_csv


def solve():
    starting_params = PatientState.schnider_params()

    params_array = convert_params_structure_to_vector(starting_params)

    result = basinhopping(find_lsq_for_all_patients, params_array)
    return result.x


def get_patients():
    # TODO: Memoize
    return read_patient_csv();


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
        # TODO: Use params rather than schnider_params
        patient_error = solve_for_patient(patient, PatientState.schnider_params())
        total_lsq += patient_error

    return total_lsq


def solve_for_patient(patient, params):
    print "Patient %s" % patient["id"]

    patient_model = PatientState(patient['age'], patient['weight'], patient['height'], patient['sex'], params)
    patient_model.give_drug(patient['propofol_mg'])

    previous_time_mins = 0

    total_lsq_error = 0
    total_measurements = 0

    for measurement in patient['measurements']:
        for t in range(int((measurement['time_mins'] - previous_time_mins) * 60)):
            patient_model.wait_time(1)

        predicted_cp = patient_model.x1
        error = measurement['cp'] - predicted_cp

        total_lsq_error += error ** 2
        total_measurements += 1

    return total_lsq_error / total_measurements


result = solve()
print result
