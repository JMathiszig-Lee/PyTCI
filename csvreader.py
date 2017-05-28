import csv
from patient_state import PatientState

csvfile = "propofol.csv"

def read_patient_csv():
    patients = []

    read = open(csvfile, 'r')
    # Read header line
    read.readline()

    pid = None
    current_patient = __build_new_patient()

    for row in csv.reader(read):
        newid = row[0]

        if newid == pid:
            measurement = {
                "time_mins": float(row[1]),
                "cp": float(row[2])
            }
            current_patient["measurements"].append(measurement)
        else:
            pid = newid
            current_patient = __build_new_patient()
            patients.append(current_patient)

            # Assume that the first row for a patient contains the bolus
            # TODO: Check that this is always true
            current_patient['propofol_mg'] = float(row[3])

            current_patient['id'] = pid
            current_patient['age'] = float(row[6])
            current_patient['weight'] = float(row[7])
            current_patient['height'] = float(row[8])
            patient_sex_code = int(row[9])
            if patient_sex_code == 1:
                current_patient['sex'] = "m"
            elif patient_sex_code == 2:
                current_patient['sex'] = "m"
            else:
                raise ValueError("Unknown value for patient sex '%s'. Expected '1' or '2'" % sex)

    return patients

def __build_new_patient():
    return {
        "measurements": []
    }
