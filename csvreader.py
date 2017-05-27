import csv
from patient_state import PatientState

csvfile = "propofol.csv"

read = open(csvfile, 'r')

#read first line
read.readline()
pid = 0
#pull demographics
for row in csv.reader(read):
    newid = row[0]
    if newid == pid:
        #still on same patient, carry on
        print 'oldpatient'
    else:
        #save mean error from this patient
        meanerror = totalerror / totalmeasurements
        #do something with this like save it to a file database?

        #new patient, reset compartments
        pid = newid
        age = row[6]
        weight = row[7]
        height = row[8]
        sex = row[9]

        patient = PatientState(age, weight, height, sex)
        totalmeasurements = 0
        totalerror = 0

    mg = row[3]
    rate = row[4]
    cp = row[2]
    cp = float(cp)
    time = float(mg) / float(rate)

    if cp == 0:
        #no plasma concentration so calculate and move on
        patient.give_drug(mg)
        patient.wait_time(time)
    else:
        #do a comparison with x1 and store it somewhere
        predcp = patient.x1
        newerror = cp - pred_cp
        rmserror = SQRT(newerror**)
        totalmeasurements ++
        totalerror = totalerror + rmserror
