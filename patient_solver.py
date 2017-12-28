from patient_state import PatientState, PatientState2
#from patient_state2 import PatientState2
import math
import statistics

def solve_for_patient(patient, params):
    #print "Patient %s" % patient["id"]

    patient_model = PatientState2(patient['age'], patient['weight'], patient['height'], patient['sex'], params)

    results = {
        "cps": []
    }

    total_lsq_error = 0
    total_measurements = 0
    total_percent_error = 0

    previous_time_mins = 0
    current_dose_mg_per_sec = 0
    infusion_seconds_remaining = 0

    absolutelist = []
    biaslist    = []

    for event in patient['events']:
        for t in range(int((event['time_mins'] - previous_time_mins) * 60)):
            if infusion_seconds_remaining > 0:
                patient_model.give_drug(current_dose_mg_per_sec)
                infusion_seconds_remaining -= 1

            patient_model.wait_time(1)

        if event["type"] == "measurement":
            predicted_cp = patient_model.x1
            error = event['cp'] - predicted_cp

            percent_error = error / event['cp']
            biaslist.append(error)

            results["cps"].append({
                "time_seconds": int(previous_time_mins * 60) + t,
                "predicted_cp": predicted_cp,
                "measured_cp": event['cp']
            })

            #print "Predicted: %f, Actual: %f" % (predicted_cp, event['cp'])

            error = error ** 2
            error = math.sqrt(error)


            total_lsq_error += error
            total_measurements += 1

            percent_error = error / event['cp']
            if percent_error < 0:
                print percent_error

            absolutelist.append(percent_error)


            total_percent_error += percent_error

        elif event["type"] == "start_infusion":
            amount_mg = event["propofol_mg"]
            current_dose_mg_per_sec = event["rate_mg_per_min"] / 60
            infusion_seconds_remaining = amount_mg / current_dose_mg_per_sec
        else:
            raise ValueError("Unknown patient event type '%s'. Expected 'measurement' or 'start_infusion'" % event["type"])

        previous_time_mins = event['time_mins']

    results["error"]    = total_lsq_error / total_measurements
    results["percent"]  = total_percent_error / total_measurements
    results["median"]   = statistics.median(absolutelist)
    results["bias"]     = statistics.median(biaslist)
    return results

def solve_for_schnider(patient, params):
        #print "Patient %s" % patient["id"]

        patient_model = PatientState(patient['age'], patient['weight'], patient['height'], patient['sex'], params)

        results = {
            "cps": []
        }

        total_lsq_error = 0
        total_measurements = 0
        total_percent_error = 0

        previous_time_mins = 0
        current_dose_mg_per_sec = 0
        infusion_seconds_remaining = 0

        absolutelist = []
        biaslist    = []

        for event in patient['events']:
            for t in range(int((event['time_mins'] - previous_time_mins) * 60)):
                if infusion_seconds_remaining > 0:
                    patient_model.give_drug(current_dose_mg_per_sec)
                    infusion_seconds_remaining -= 1

                patient_model.wait_time(1)

            if event["type"] == "measurement":
                predicted_cp = patient_model.x1
                error = event['cp'] - predicted_cp

                percent_error = error / event['cp']
                biaslist.append(error)

                results["cps"].append({
                    "time_seconds": int(previous_time_mins * 60) + t,
                    "predicted_cp": predicted_cp,
                    "measured_cp": event['cp']
                })

                #print "Predicted: %f, Actual: %f" % (predicted_cp, event['cp'])

                error = error ** 2
                error = math.sqrt(error)


                total_lsq_error += error
                total_measurements += 1

                percent_error = error / event['cp']
                if percent_error < 0:
                    print percent_error

                absolutelist.append(percent_error)


                total_percent_error += percent_error

            elif event["type"] == "start_infusion":
                amount_mg = event["propofol_mg"]
                current_dose_mg_per_sec = event["rate_mg_per_min"] / 60
                infusion_seconds_remaining = amount_mg / current_dose_mg_per_sec
            else:
                raise ValueError("Unknown patient event type '%s'. Expected 'measurement' or 'start_infusion'" % event["type"])

            previous_time_mins = event['time_mins']

        results["error"]    = total_lsq_error / total_measurements
        results["percent"]  = total_percent_error / total_measurements
        results["median"]   = statistics.median(absolutelist)
        results["bias"]     = statistics.median(biaslist)
        return results
