from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_state import PatientState
import math
import statistics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def test_against_real_data():
    patients = read_patient_csv();

    params = PatientState.schnider_params()
    totalrms = 0
    count = 0
    z = []
    for patient in patients[280:290]:
        a = solve_for_patient(patient, params)["error"]
        a = math.sqrt(a)
        z.append(a)
        totalrms = totalrms + a
        count += 1
    b =  totalrms / count
    c = statistics.stdev(z)

    data = (b, c)

    return data

def mute_against_real_data():
    patients = read_patient_csv();
    v1      = 4.27 * np.random.normal(1, 0.2)
    k10a    = 0.443 * np.random.normal(1, 0.1)
    k10b    = 0.0107 * np.random.normal(1, 0.1)
    k10c    = -0.0159 * np.random.normal(1, 0.1)
    k13     = 0.196 * np.random.normal(1, 0.1)

    params = {
        'k10a': k10a,
        'k10b': k10b,
        'k10c': k10c,
        'k10d': 0.0062,
        'k12a': 0.302,
        'k12b': -0.0056,
        'k13': k13,
        'k21a': 1.29,
        'k21b': -0.024,
        'k21c': 18.9,
        'k21d': -0.391,
        'k31': 0.0035,
        'v1': v1,
        'v3': 238,
        'age_offset': 53,
        'weight_offset': 77,
        'lbm_offset': 59,
        'height_offset': 177
    }
    totalrms = 0
    count = 0
    z = []
    for patient in patients[280:300]:
        a = solve_for_patient(patient, params)["error"]
        a = math.sqrt(a)
        z.append(a)
        totalrms = totalrms + a
        count += 1
    b =  totalrms / count
    c = statistics.stdev(z)

    data = (b, c)

    return data

if __name__ == '__main__':
    fig1 = plt.figure()
    def update(i):
        fig1.clear()
        schnider= test_against_real_data()
        mutant = mute_against_real_data()
        ys = (schnider[0], mutant[0])
        xs = (1, 2)
        es = (schnider[1], mutant[1])
        if schnider[0] < mutant [0]:
            c = 'r'
        else:
            c = 'g'
        stuff = (plt.errorbar(xs, ys, es, color=c))
        return stuff
    ani = animation.FuncAnimation(fig1, update, interval=10)
    #plt.show()
    #plt.errorbar(xs, ys, es)
    plt.show()
