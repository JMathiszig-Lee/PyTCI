from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_state import PatientState

def test_against_real_data():
    patients = read_patient_csv();

    params = PatientState.schnider_params()

    for patient in patients[6:7]:
        results = solve_for_patient(patient, params)
        for result in results["predicted_and_measured"]:
            print "predicted: %f, measured: %f" % result

if __name__ == '__main__':
    test_against_real_data()
