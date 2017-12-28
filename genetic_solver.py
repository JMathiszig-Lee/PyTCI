from crosscorrelate import test_against_real_data
import numpy as np
import random
import time
import csv
import os
from multiprocessing import Pool


def create_population(size):
    params = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]
    pop_size = size

    pop_list = []
    for i in range(pop_size):
        newparam = []
        for k in params:
            k = k * np.random.normal(1, 0.3)
            k = round(k, 4)
            newparam.append(k)

        pop_list.append(newparam)
    return pop_list

def create_new_set():
    #TODO make this all 0,1 so we can easily switch between models for a variable size population
    # this means setting the magnitude within the patientstateX class
    new_set = []
    new_set.append(random.uniform(0,50))    #v1a
    new_set.append(random.uniform(0,1))     #v1b
    new_set.append(random.uniform(0,100))   #age_offset
    new_set.append(random.uniform(0,1))     #v1c
    new_set.append(random.uniform(0,100) )   #lbm_offset
    new_set.append(random.uniform(0,2))   #v2a
    new_set.append(random.uniform(0,5))    #v3a
    new_set.append(random.uniform(0,1))    #k10a
    new_set.append(random.uniform(0,1))    #k12
    new_set.append(random.uniform(0,1))    #k13#
    count = 0
    for k in new_set:
        i = round(k, 4)
        new_set[count]= i
        count += 1

    return new_set

def create_new_population(size):
    pop_size = size

    pop_list = []
    for i in range(pop_size):
        newparam = create_new_set()
        pop_list.append(newparam)
    return pop_list

def test_population(pop, best, second, one, two):
    print " "
    print "********"
    print "%-40s %-40s" % ('best', 'second')
    print "%-40s %-40s" % (best, second)
    print "********"
    print " "
    best_fitness = best[1]
    second_fitness = second[1]

    fittest_set = one
    second_set = two

    print fittest_set
    print second_set

    #print "best: " + str(best_fitness)

    #switching between the tuple and value is confusing and i'm getting upset


    for i in pop:
        try:
            result = multi_core_test(cores, max, i)

            fitness = result[1]

            if fitness < best_fitness:
                print str(fitness) + str(best_fitness)
                #move current best to second best
                second = best
                second_set = fittest_set

                best = result
                fittest_set = i

            elif fitness < second_fitness and fitness != best_fitness:
                second = result
                second_set = i


            #these should be tuples
            print "%-40s %-40s" % ('best', 'second')
            print "%-40s %-40s" % (best, second)
        except:
            result = (99, 99, 99)
            print "except"
            print " "

    output = (fittest_set, best, second_set, second)
    print "output"
    print output

    return output

def mutate_population(children, fittest, second, mutants):
    pop_list = []

    def mutate_chromosome(chrome):
        b = random.random()
        c = len(fittest)
        c = 1 / c
        if b < (c/2):
            chrome = chrome * np.random.normal(1, 0.3)
        elif b < c:
            chrome = chrome * np.random.normal(1, 0.1)
        else:
            chrome = chrome * 1
        return chrome


    #breed parents to create children
    def breed(sprogs, p1, p2):
        for i in range(sprogs):
            child = []
            count = 0
            for k in p1:
                a = random.random()
                if a < 0.5:
                    k = p2[count]
                    k = mutate_chromosome(k)
                    child.append(k)
                else:
                    k = mutate_chromosome(k)
                    child.append(k)

                count +=1
            pop_list.append(child)

    breed(children, fittest, second)

    rand1 = create_new_set()
    rand2 = create_new_set()
    breed(2, fittest, rand1)

    breed(2, fittest, rand2)

    #create mutants of fittest
    for i in range(mutants):
        mutant = []
        for k in fittest:
            b = random.random()
            if b < 0.2:
                mut_factor = 0.3
            else:
                mut_factor = 0.1
            k = k * np.random.normal(1, mut_factor)
            k = round(k, 4)
            mutant.append(k)
        pop_list.append(mutant)

    return pop_list

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
    bias = sum([thing[2] for thing in results]) / cores

    # "%-15s %-15s" % (rms, meds)
    data = (rms, meds, bias)

    #return meds
    return data

if __name__ == '__main__':
    min     = 1
    max     = int(os.getenv('MAX', 10))
    pop     = int(os.getenv('POP', 5))
    cores   = int(os.getenv('CORES', 1))
    gens    = int(os.getenv('GENERATIONS', 3))

    PROCESSES = cores
    pool = Pool(PROCESSES)

    print "%-15s %-15s %-15s %-45s" % ('Number', 'pop size', 'Cores', 'Generations')
    print "%-15s %-15s %-15s %-45s" % (max, pop, cores, gens)


    fittest_set = []
    second_set = []

    best_fitness = (10,10,10)
    second_fitness = (10,10,10)

    timestr = time.strftime("%Y%m%d-%H%M%S")
    folder = 'results/'
    fileloc = os.path.join(folder, timestr)

    with open('%s.csv' % (fileloc), 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)

        new_pop = create_new_population(pop)
        fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)


        fittest_set = fit_results[0]
        best_fitness = fit_results[1]
        second_set = fit_results[2]
        second_fitness = fit_results[3]
        sec_fit = second_fitness[1]

        while sec_fit > 9.9:
            new_pop = create_new_population(pop)
            fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)
            print " "
            print "results: " +  str(fit_results)
            print " "
            fittest_set = fit_results[0]
            best_fitness = fit_results[1]
            #best_fitness = best_fitness[1]

            second_set = fit_results[2]
            second_fitness = fit_results[3]
            sec_fit = second_fitness[1]

            #print "%-5s %-45s %-5s %-45s" % (best_fitness, fittest_set, second_fitness, second_set)
            time.sleep(2)
            print "trying again"

        gen = 0
        print "%-5s %-15s %-15s %-45s" % ('Gen', 'Best', 'Second', 'Set')
        print "%-5s %-15s %-15s %-45s" % (gen, best_fitness, second_fitness, fittest_set)

        for i in range(gens):

            def pick_random_set():
                not_fittest = 1
                while not_fittest == 1:
                    randset = random.randint(0,9)
                    randset = new_pop[randset]
                    if randset != fittest_set:
                        not_fittest = 0
                return randset

            new_pop = mutate_population(4, fittest_set, second_set, 4)

            gen +=1
            fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)
            fittest_set = fit_results[0]
            best_fitness = fit_results[1]
            second_set = fit_results[2]
            second_fitness = fit_results[3]

            print "%-15s %-15s %-15s %-45s" % (gen, best_fitness, second_fitness, fittest_set)
            wr.writerow(fit_results)
