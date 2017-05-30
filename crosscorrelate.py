from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_state import PatientState
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
    c = statistics.stdev(z)

    #average cross correlation
    d = totalcc / count

    data = (b, c, d)

    return data

if __name__ == '__main__':
    pmin = 1
    pmax = 5
    params = PatientState.schnider_params()
    schnider= test_against_real_data(pmin, pmax, params)
    print schnider
