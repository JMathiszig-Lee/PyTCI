from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_state import PatientState
import math
import statistics
import time
from multiprocessing import Pool
import numpy as np

def test_against_real_data(stuff):
    pmin = stuff[0]
    pmax = stuff[1]
    params = stuff[2]
    patients = read_patient_csv();
    totalrms = 0
    count = 0
    totalcc = 0
    z = []

    for patient in patients[pmin:pmax]:
        a = solve_for_patient(patient, params)["error"]
        # i think this would mean rooting twice?
        #a = math.sqrt(a)
        z.append(a)
        totalrms = totalrms + a
        count += 1

        #set up for cross correlation
        d = solve_for_patient(patient, params)["cps"]
        predcps = []
        meascps = []

        for e in d:
            predcps.append(e['predicted_cp'])
            meascps.append(e['measured_cp'])
        cc = np.correlate(predcps, meascps)
        totalcc =+ cc[0]

    #average RMS and stddeviation
    b =  totalrms / count
    c = statistics.stdev(z)

    #average cross correlation
    d = totalcc / count

    data = (b, c, d)
    #date = (b, d)

    return data

if __name__ == '__main__':
    # startTime = time.time()
    # pmin = 1
    # pmax = 500
    #params = PatientState.schnider_params()
    params_vector = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]
    # stuff = (pmin, pmax, params)
    # schnider= test_against_real_data(stuff)
    #
    # endtime = time.time()
    # worktime = endtime - startTime
    #
    # print schnider
    # print worktime
    params = {
        'k10a': params_vector[0],
        'k10b': params_vector[1],
        'k10c': params_vector[2],
        'k10d': params_vector[3],
        'k12a': params_vector[4],
        'k12b': params_vector[5],
        'k13':  params_vector[6],
        'k21a': params_vector[7],
        'k21b': params_vector[8],
        'k21c': params_vector[9],
        'k21d': params_vector[10],
        'k31':  params_vector[11],
        'v1':   params_vector[12],
        'v3':   params_vector[13],
        'age_offset': params_vector[14],
        'weight_offset': params_vector[15],
        'lbm_offset': params_vector[16],
        'height_offset': params_vector[17]
    }

    startTime = time.time()

    pool = Pool(processes=5)
    results = pool.map(test_against_real_data, [(1, 100, params),(101, 200, params),(201, 300, params),(301, 400, params),(401, 500, params)])

    endtime = time.time()
    worktime = endtime - startTime
    print results
    print worktime
