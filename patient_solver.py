from patient_state import PatientState

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
