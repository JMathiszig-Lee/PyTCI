from csvreader2 import read_patient_csv
from patient_solver2 import solve_for_patient
from patient_state2 import PatientState
import math
import statistics
import numpy as np

def test_against_real_data(pmin, pmax, params):
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
    #c = statistics.stdev(z)

    #average cross correlation
    d = totalcc / count

    #data = (b, c, d)
    date = (b, d)

    return data

if __name__ == '__main__':
    pmin = 1
    pmax = 5
    #params = PatientState.schnider_params()
    params = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]

    schnider= test_against_real_data(pmin, pmax, params)
    print schnider
