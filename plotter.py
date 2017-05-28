import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import csv
from patient_state import PatientState

fig, ax = plt.subplots()
line, = ax.plot(np.random.rand(10))
ax.set_ylim(0, 1)

def estimate_propofol(maxcount):
    csvfile = "testpatient.csv"

    read = open(csvfile, 'r')

    #read first line
    read.readline()
    count = maxcount
    totalerror = 0
    totalmeasurements = 0
    previous_time_mins = 0
    #pull demographics

    truecp = []
    calccp = []
    schnider = []
    times = []
    for row in csv.reader(read):

        age = float(row[6])
        weight = float(row[7])
        height = float(row[8])
        # TODO: Convert 1/2 to m/f, and validate in PatientState
        sex = row[9]
        if sex == 1:
            sex = 'm'
        else:
            sex = 'f'

        if count == 0:
            patient = PatientState.with_schnider_params(age, weight, height, sex)
        else:
            v1      = 4.27 * np.random.normal(1, 0.2)
            k10a    = 0.443 * np.random.normal(1, 0.1)
            k10b    = 0.0107 * np.random.normal(1, 0.1)
            k10c    = -0.0159 * np.random.normal(1, 0.1)
            k13     = 0.196 * np.random.normal(1, 0.1)

            params = {
                'k10a': k10a,
                'k10b': k10b,
                'k10c': k10c,
                'k10d': 0.0062,
                'k12a': 0.302,
                'k12b': -0.0056,
                'k13': k13,
                'k21a': 1.29,
                'k21b': -0.024,
                'k21c': 18.9,
                'k21d': -0.391,
                'k31': 0.0035,
                'v1': v1,
                'v3': 238,
                'age_offset': 53,
                'weight_offset': 77,
                'lbm_offset': 59,
                'height_offset': 177
            }
            patient = PatientState(age, weight, height, sex, params)

        mg = float(row[3])
        rate = float(row[4])
        cp = float(row[2])

        patient.give_drug(mg)

        time_mins = float(row[1])
        seconds_since_last_measurement = int((time_mins - previous_time_mins) * 60)

        for t in range(seconds_since_last_measurement):
            patient.wait_time(1)

        if cp != 0:
            #do a comparison with x1 and store it somewhere
            pred_cp = patient.x1
            print pred_cp
            if count == 0:
                #first run so plot schider and true cp
                truecp.append(cp)
                schnider.append(pred_cp)
                times.append(time_mins)
            else:
                calccp.append(pred_cp)

        previous_time_mins = time_mins




    data = (truecp, schnider, calccp, times)
    return data



something = estimate_propofol(1)
someone = estimate_propofol(0)
#data = (someone[0], someone[3], someone[1], someone[3], something[2], someone[3])
data = (someone[3], someone[1], someone[3], something[2], someone[3], someone[0])


x = np.array(someone[3])
y1 = np.array(someone[0])
y2 = np.array(someone[1])
y3 = np.array(something[2])
print data
print x

# plt.plot(y1, x)
# plt.plot(x, y2)
# plt.plot(x, y3)
plt.plot(data)
plt.axis([0, 104, 0, 20])
def update(data):
    line.set_ydata(data)
    return line,


def data_gen():
    while True:
        yield np.random.rand(10)

#ani = animation.FuncAnimation(fig, update, data_gen, interval=100)
plt.show()
