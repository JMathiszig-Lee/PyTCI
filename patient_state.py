# "weight": kilos
# "height": cm
def newPatientWithAge(age, weight, height, sex):
    is_male = sex == "m"

    # "TODO": Use better equation to calculate lean body mass
    if (is_male):
        lbm = 1.1 * weight - 128 * ((weight/height) * (weight/height))
    else:
        lbm = 1.07 * weight - 148 * ((weight/height) * (weight/height))

    v1 = 4.27
    v2 = 18.9 - 0.391 * (age - 53)
    v3 = 238

    k10 = 0.443 + 0.0107 * (weight - 77) - 0.0159 * (lbm - 59) + 0.0062 * (height - 177)
    k12 = 0.302 - 0.0056 * (age - 53)
    k13 = 0.196
    k21 = (1.29 - 0.024 * (age - 53)) / (18.9 - 0.391 * (age - 53))
    k31 = 0.0035

    keo = 0.456

    xeo = 0.0

    return {
        "x1": 0,
        "x2": 0,
        "x3": 0,
        "v1": v1,
        "v2": v2,
        "v3": v3,
        "k10": k10,
        "k12": k12,
        "k13": k13,
        "k21": k21,
        "k31": k31,
        "keo": keo,
        "xeo": xeo
    }

def giveDrug(drugMilligrams, patientState):
    patientState["x1"] = patientState["x1"] + drugMilligrams / patientState["v1"]
    return patientState

def waitTime(timeSeconds, patientState):
    x1 = patientState["x1"]
    x2 = patientState["x2"]
    x3 = patientState["x3"]

    k10 = patientState["k10"]
    k21 = patientState["k21"]
    k12 = patientState["k12"]
    k13 = patientState["k13"]
    k31 = patientState["k31"]
    keo = patientState["keo"]
    xeo = patientState["xeo"]

    patientState["x1"] = x1 + (k21 * x2 + -(k12) * x1 + k31 * x3 + -(k13) * x1 - k10 * x1) * timeSeconds
    patientState["x2"] = x2 + (-k21 * x2 + k12 * x1) * timeSeconds
    patientState["x3"] = x3 + (-k31 * x3 + k13 * x1) * timeSeconds
    patientState["xeo"] = xeo + (-keo * xeo + keo * x1) * timeSeconds

    return patientState;

if __name__ == '__main__':
    patient = newPatientWithAge(50, 70, 180, "m")
    print "Initial state: " + str(patient)

    patient = giveDrug(50, patient)
    print "After giving drug: " + str(patient)

    patient = waitTime(1, patient)
    print "After 1 second: " + str(patient)

    patient = waitTime(60, patient)
    print "After another 1 minute: " + str(patient)

    patient = waitTime(3600, patient)
    print "After another 1 hour: " + str(patient)
