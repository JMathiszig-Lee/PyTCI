from genetic_solver import create_new_population
from crosscorrelate import test_against_real_data
from multiprocessing import Pool

pool = Pool(5)

param = create_new_population(2)

def multi_core_test(cores, max, params_vector):
    #TODO change this so params can be any size
    params = {
        'v1a': params_vector[0],
        'v1b': params_vector[1],
        'age_offset': params_vector[2],
        'v1c': params_vector[3],
        'lbm_offset': params_vector[4],
        'v2a': params_vector[5],
        'v3a':  params_vector[6],
        'k10a': params_vector[7],
        'k12': params_vector[8],
        'k13': params_vector[9],
    }

    step_size = max / cores
    step_size = int(step_size)

    jobs = []
    for idx in range(cores):
        a = step_size * idx + 1
        b = step_size * (idx + 1)
        if idx == (cores-1):
            b = max
        thing = (a, b, params)
        jobs.append(thing)

    results = pool.map(test_against_real_data, jobs)

    #make this dynamic, cast to float?
    rms = sum([thing[0] for thing in results]) / cores
    meds = sum([thing[1] for thing in results]) / cores

    # "%-15s %-15s" % (rms, meds)


    return meds

print param[0]

params_vector = [19.0316, 0.8329, 60.0775, 0.3416, 30.6775, 1.0755, 4.3761, 0.635, 0.3794, 0.3031]
params = {
    'v1a': params_vector[0],
    'v1b': params_vector[1],
    'age_offset': params_vector[2],
    'v1c': params_vector[3],
    'lbm_offset': params_vector[4],
    'v2a': params_vector[5],
    'v3a':  params_vector[6],
    'k10a': params_vector[7],
    'k12': params_vector[8],
    'k13': params_vector[9],
}

stuff =(0,2,params)
single = test_against_real_data(stuff)

print single

multi = multi_core_test(4, 12, params_vector)

print multi
