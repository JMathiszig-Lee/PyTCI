from patient_state import PatientState

patient = PatientState(34, 46.3, 157.5, "f")
print "Initial state: " + str(patient)

patient.give_drug(92)
print "After giving drug: " + str(patient)

patient.wait_time(2.11)
print "After 1 second: " + str(patient)

patient.wait_time(4.2)
print "After another 1 minute: " + str(patient)

patient.wait_time(8)
print "After another 1 hour: " + str(patient)
