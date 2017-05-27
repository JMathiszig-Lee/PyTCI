class PatientState:
    # age: years
    # weight: kilos
    # height: cm
    # sex: 'm' or 'f'
    def __init__(self, age, weight, height, sex):
        is_male = sex == "m"

        # TODO: Use better equation to calculate lean body mass
        if (is_male):
            lbm = 1.1 * weight - 128 * ((weight/height) * (weight/height))
        else:
            lbm = 1.07 * weight - 148 * ((weight/height) * (weight/height))

        self.v1 = 4.27
        # TODO: Work out why v2 and v3 are not used in the algorithm
        v2 = 18.9 - 0.391 * (age - 53)
        v3 = 238

        #
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0

        self.k10 = 0.443 + 0.0107 * (weight - 77) - 0.0159 * (lbm - 59) + 0.0062 * (height - 177)
        self.k12 = 0.302 - 0.0056 * (age - 53)
        self.k13 = 0.196
        self.k21 = (1.29 - 0.024 * (age - 53)) / (18.9 - 0.391 * (age - 53))
        self.k31 = 0.0035

        self.keo = 0.456

        self.xeo = 0.0

    def giveDrug(self, drugMilligrams):
        self.x1 = self.x1 + drugMilligrams / self.v1

    def waitTime(self, timeSeconds):
        self.x1 = self.x1 + (self.k21 * self.x2 + -(self.k12) * self.x1 + self.k31 * self.x3 + -(self.k13) * self.x1 - self.k10 * self.x1) * timeSeconds
        self.x2 = self.x2 + (-self.k21 * self.x2 + self.k12 * self.x1) * timeSeconds
        self.x3 = self.x3 + (-self.k31 * self.x3 + self.k13 * self.x1) * timeSeconds
        self.xeo = self.xeo + (-self.keo * self.xeo + self.keo * self.x1) * timeSeconds

    def __repr__(self):
        return "PatientState(x1=%f, x2=%f, x3=%f, xeo=%f)" % (self.x1, self.x2, self.x3, self.xeo)


if __name__ == '__main__':
    patient = PatientState(50, 70, 180, "m")
    print "Initial state: " + str(patient)

    patient.giveDrug(50)
    print "After giving drug: " + str(patient)

    patient.waitTime(1)
    print "After 1 second: " + str(patient)

    patient.waitTime(60)
    print "After another 1 minute: " + str(patient)

    patient.waitTime(3600)
    print "After another 1 hour: " + str(patient)
