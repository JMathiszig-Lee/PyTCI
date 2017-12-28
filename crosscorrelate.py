from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_solver import solve_for_schnider
from patient_state import PatientState
import math
import statistics
import time
from multiprocessing import Pool
import numpy as np
#import matplotlib.pyplot as plt


def test_against_real_data(stuff):
    pmin = stuff[0]
    pmax = stuff[1]
    params = stuff[2]
    patients = read_patient_csv();

    totalrms = 0
    totalmed = 0
    totalbias = 0
    count = 0

    for patient in patients[pmin:pmax]:
        res = solve_for_patient(patient, params)
        a = res["percent"]
        med = res["median"]
        bias = res["bias"]

        #print "%-10s %-10s" % (a, med)

        totalrms    += a
        totalbias   += bias
        totalmed    += med
        count += 1

    b = totalrms / count
    c = totalmed / count
    d = totalbias / count


    data = (b, c, d)
    return data

def test_with_schnider(stuff):
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
        params = PatientState.schnider_params()
        #print patient["id"]
        b = solve_for_schnider(patient, params)
        a = solve_for_schnider(patient, params)["percent"]

        print b["percent"]
        print a



        z.append(a)
        totalrms = totalrms + a
        count += 1
        print "Patient: %s, Error: %f" % ( patient["id"], a)

        #set up for cross correlation
        #d = solve_for_schnider(patient, params)["cps"]
        predcps = []
        meascps = []

        # for e in d:
        #
        #     predcps.append(e['predicted_cp'])
        #     meascps.append(e['measured_cp'])

        #somethings going wrong as _percentage_rms increases with patient number
        # print "for patient " + str(count)
        # print totalrms/count
        # print percentage_rms/meas_count
        something = totalrms/count
        plot_array.append(something)
        #cc = np.correlate(predcps, meascps)
        #totalcc =+ cc[0]

    #average RMS and stddeviation
    b =  totalrms / count
    #c = statistics.stdev(z)

    #average cross correlation (i dont think you can do this)
    d = totalcc / count




    #data = (b, c, d )
    data = (b)
    #plot_array.append(something)
    plt.plot(plot_array)
    plt.show()

    return data

def multi_core_test(cores, max, params_vector):
    #TODO change this so params can be any size
    params = {
        'v1a': params_vector[0],
        'v1b': params_vector[1],
        'age_offset': params_vector[2],
        'v1c': params_vector[3],
        'lbm_offset': params_vector[4],
        'v2a': params_vector[5],
        'v3a':  params_vector[6],
        'k10a': params_vector[7],
        'k12': params_vector[8],
        'k13': params_vector[9],
    }

    step_size = max / cores
    step_size = int(step_size)

    jobs = []
    for idx in range(cores):
        a = step_size * idx + 1
        b = step_size * (idx + 1)
        if idx == (cores-1):
            b = max
        thing = (a, b, params)
        jobs.append(thing)

    results = pool.map(test_against_real_data, jobs)

    #make this dynamic, cast to float?
    rms = sum([thing[0] for thing in results]) / cores
    meds = sum([thing[1] for thing in results]) / cores

    # "%-15s %-15s" % (rms, meds)


    return meds

if __name__ == '__main__':
    startTime = time.time()
    pmin = 0
    pmax = 2
    params = PatientState.schnider_params()



    stuff = (pmin, pmax, params)
    schnider= test_with_schnider(stuff)

    param = create_new_set()

    print multi_core_test(4, pmax, param)

    endtime = time.time()
    worktime = endtime - startTime

    print schnider
    print worktime
