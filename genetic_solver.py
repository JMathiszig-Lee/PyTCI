from crosscorrelate import multi_core_test
import numpy as np
import random
import time

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

def test_population(pop, best, second, one, two):
    best_fitness = best
    second_fitness = second

    fittest_set = one
    second_set = two

    for i in pop:
        try:
            fitness = multi_core_test(min, max, i)
        except:
            fitness = 1

        #print fitness
        if fitness < best_fitness:
            #move current best to second best
            second_fitness = best_fitness
            second_set = fittest_set

            best_fitness = fitness
            fittest_set = i
        elif fitness < second_fitness and fitness != best_fitness:
            second_fitness = fitness
            second_set = i

    # print "best_fitness"
    # print best_fitness
    # print " "
    return (fittest_set, best_fitness, second_set, second_fitness)

def mutate_population(children, fittest, second, mutants, rand1, rand2):
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
    for i in range(children):
        child = []
        count = 0
        for k in fittest:
            a = random.random()
            if a < 0.5:
                k = second[count]
                k = mutate_chromosome(k)
                child.append(k)
            else:
                k = mutate_chromosome(k)
                child.append(k)

            count +=1

        pop_list.append(child)


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

    #breed fittest with randoms
    for i in range(5):
        child = []
        count = 0
        for k in fittest:
            a = random.random()
            if a < 0.5:
                k = rand1[count]
                k = mutate_chromosome(k)
                child.append(k)
            else:
                k = mutate_chromosome(k)
                child.append(k)

            count +=1

        pop_list.append(child)
    for i in range(5):
        child = []
        count = 0
        for k in fittest:
            a = random.random()
            if a < 0.5:
                k = rand2[count]
                k = mutate_chromosome(k)
                child.append(k)
            else:
                k = mutate_chromosome(k)
                child.append(k)

            count +=1

        pop_list.append(child)

    return pop_list

if __name__ == '__main__':
    startTime = time.time()
    min = 1
    max = 150
    params = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]
    gen = 0
    best_fitness =  multi_core_test(min, max, params)
    #second_fitness =  0.259090961264
    second_fitness =  float(best_fitness)
    print "%-15s %-15s %-15s" % ('Generation', 'Best', 'Second')
    print "%-15s %-15s %-15s" % (gen, best_fitness, second_fitness)
    fittest_set = params
    second_set = params

    new_pop = create_population(40)
    gen +=1
    fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)
    fittest_set = fit_results[0]

    best_fitness = fit_results[1]
    second_set = fit_results[2]
    second_fitness = fit_results[3]

    print "%-15s %-15s %-15s" % (gen, best_fitness, second_fitness)

    for i in range(15):

        def pick_random_set():
            not_fittest = 1
            while not_fittest == 1:
                randset = random.randint(0,9)
                randset = new_pop[randset]
                if randset != fittest_set:
                    not_fittest = 0
            return randset

        randset1 = pick_random_set()
        randset2 = pick_random_set()

        new_pop = mutate_population(20, fittest_set, second_set, 5, randset1, randset2 )

        gen +=1
        fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)
        fittest_set = fit_results[0]

        best_fitness = fit_results[1]
        second_set = fit_results[2]
        second_fitness = fit_results[3]

        print "%-15s %-15s %-15s" % (gen, best_fitness, second_fitness)

    print fittest_set
    endtime = time.time()
    worktime = endtime - startTime
    print worktime
