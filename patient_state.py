class PatientState:
    # age: years
    # weight: kilos
    # height: cm
    # sex: 'm' or 'f'
    def __init__(self, age, weight, height, sex):
        lean_body_mass = self.__lean_body_mass(weight, height, sex)

        self.v1 = 4.27
        # TODO: Work out why v2 and v3 are not used in the algorithm
        v2 = 18.9 - 0.391 * (age - 53)
        v3 = 238

        # Initial concentration is zero in all components
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0

        self.k10 = 0.443 + 0.0107 * (weight - 77) - 0.0159 * (lean_body_mass - 59) + 0.0062 * (height - 177)
        self.k12 = 0.302 - 0.0056 * (age - 53)
        self.k13 = 0.196
        self.k21 = (1.29 - 0.024 * (age - 53)) / (18.9 - 0.391 * (age - 53))
        self.k31 = 0.0035

        self.keo = 0.456

        self.xeo = 0.0

    def give_drug(self, drug_milligrams):
        self.x1 = self.x1 + drug_milligrams / self.v1

    def wait_time(self, time_minutes):
        current_x1 = self.x1
        current_x2 = self.x2
        current_x3 = self.x3
        current_xeo = self.xeo

        self.x1 = current_x1 + (self.k21 * current_x2 - self.k12 * current_x1 + self.k31 * current_x3 - self.k13 * current_x1 - self.k10 * current_x1) * time_minutes
        self.x2 = current_x2 + (-self.k21 * current_x2 + self.k12 * current_x1) * time_minutes
        self.x3 = current_x3 + (-self.k31 * current_x3 + self.k13 * current_x1) * time_minutes
        self.xeo = current_xeo + (-self.keo * current_xeo + self.keo * current_x1) * time_minutes

    def __lean_body_mass(self, weight, height, sex):
        # TODO: Use better equation to calculate lean body mass
        if sex == "m":
            return 1.1 * weight - 128 * ((weight/height) * (weight/height))
        else:
            return 1.07 * weight - 148 * ((weight/height) * (weight/height))

    def __repr__(self):
        return "PatientState(x1=%f, x2=%f, x3=%f, xeo=%f)" % (self.x1, self.x2, self.x3, self.xeo)


if __name__ == '__main__':
    patient = PatientState(50, 70, 180, "m")
    print "Initial state: " + str(patient)

    patient.give_drug(92.60001)
    print "After giving drug: " + str(patient)

    for t in range(200):
        patient.wait_time(2)
        print "After 2 mins: " + str(patient)
