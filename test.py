from patient_state import PatientState
import re

patient = PatientState.with_schneider_params(34, 46.3, 157.5, "f")
print "Initial state: " + str(patient)

patient.give_drug(92.60001)
print "After giving drug: " + str(patient)

for t in range(120):
    patient.wait_time(1)
    print "After 2 mins: " + str(patient)
    print patient.x1
