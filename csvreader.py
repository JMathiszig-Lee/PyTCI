import csv
from patient_state import PatientState

csvfile = "propofol.csv"

read = open(csvfile, 'r')

#read first line
read.readline()
pid = 0
totalerror = 0
totalmeasurements = 0
pid = 0
previous_time_mins = 0
#pull demographics
for row in csv.reader(read):
    newid = row[0]
    if newid == pid:
        #still on same patient, carry on
        print 'oldpatient'
    else:
        if pid != 0:
            #save mean error from this patient
            meanerror = totalerror / totalmeasurements
            #do something with this like save it to a file database?

        #new patient, reset compartments
        pid = newid
        age = float(row[6])
        weight = float(row[7])
        height = float(row[8])
        # TODO: Convert 1/2 to m/f, and validate in PatientState
        sex = row[9]

        patient = PatientState.with_schnider_params(age, weight, height, sex)
        totalmeasurements = 0
        totalerror = 0

    mg = float(row[3])
    rate = float(row[4])
    cp = float(row[2])

    time_mins = float(row[1])

    seconds_since_last_measurement = int((time_mins - previous_time_mins) * 60)

    for t in range(seconds_since_last_measurement):
        patient.wait_time(1)

    if cp == 0:
        #no plasma concentration so calculate and move on
        patient.give_drug(mg)
    else:
        #do a comparison with x1 and store it somewhere
        pred_cp = patient.x1
        newerror = cp - pred_cp
        # rmserror = SQRT(newerror**)
        # totalmeasurements ++
        # totalerror = totalerror + rmserror

    previous_time_mins = time_mins
