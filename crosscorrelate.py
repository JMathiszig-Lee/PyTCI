from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_state import PatientState
import math
import statistics
import time
from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt


def test_against_real_data(stuff):
    pmin = stuff[0]
    pmax = stuff[1]
    params = stuff[2]
    patients = read_patient_csv();
    totalrms = 0
    count = 0
    totalcc = 0
    z = []
    percentage_rms = 0
    meas_count = 0
    plot_array = []
    for patient in patients[pmin:pmax]:
        #a = solve_for_patient(patient, params)["error"]
        a = solve_for_patient(patient, params)["percent"]


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

        #somethings going wrong as _percentage_rms increases with patient number
        # print "for patient " + str(count)
        # print totalrms/count
        # print percentage_rms/meas_count
        something = totalrms/count
        plot_array.append(something)
        cc = np.correlate(predcps, meascps)
        totalcc =+ cc[0]

    #average RMS and stddeviation
    b =  totalrms / count
    c = statistics.stdev(z)

    #average cross correlation (i dont think you can do this)
    d = totalcc / count


    data = (b, c, d )
    #date = (b, d)
    # plt.plot(plot_array)
    # plt.show()
    return data

def multi_core_test(min, max, params_vector):
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
    pool = Pool(processes=5)
    step_size = max / 5
    step_size = int(step_size)

    a = step_size
    b = step_size + 1
    c = step_size * 2
    d = step_size * 2 + 1
    e = step_size * 3
    f = step_size * 3 + 1
    g = step_size * 4
    h = step_size * 4 + 1

    startTime = time.time()

    results = pool.map(test_against_real_data, [(1, step_size, params),(b, c, params),(d, e, params),(f, g, params),(h, max, params)])
    rms = sum([thing[0] for thing in results]) * 0.2

    endtime = time.time()
    worktime = endtime - startTime

    #return (rms, worktime)
    return rms

if __name__ == '__main__':
    startTime = time.time()
    pmin = 1
    pmax = 500
    #params = PatientState.schnider_params()
    params_vector = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]
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

    stuff = (pmin, pmax, params)
    schnider= test_against_real_data(stuff)

    endtime = time.time()
    worktime = endtime - startTime

    print schnider
    print worktime

    startTime = time.time()

    pool = Pool(processes=5)
    results = pool.map(test_against_real_data, [(1, 100, params),(101, 200, params),(201, 300, params),(301, 400, params),(401, 500, params)])

    rms = sum([thing[0] for thing in results]) * 0.2
    print rms

    #SD and crosscorrelation dont work like this so leave this out for now. minimise against RMS
    # sd = sum([thing[1] for thing in results]) * 0.2
    # crosscor = sum([thing[2] for thing in results]) * 0.2
    # print sd
    # print crosscor


    endtime = time.time()
    worktime = endtime - startTime
    print results
    print worktime
