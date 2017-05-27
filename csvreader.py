import csv

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
        pid = newid
        #new patient, reset compartments
        print 'newpatient'
    age = row[6]
    weight = row[7]
    height = row[8]
    sex = row[9]
    mg = row[3]
    rate = row[4]
    cp = row[2]
    cp = float(cp)

    if cp == 0:
        #no plasma concentration so calculate and move on
        time = float(mg) / float(rate)
        print 'time:'
        print time
    else:
        #do a comparison with x1 and store it somewhere
        print 'plasma concentration alert!'

    print age
    print mg
    print cp
