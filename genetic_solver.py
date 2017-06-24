from crosscorrelate import multi_core_test
import numpy as np
import random

def create_population(size):
    params = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]
    pop_size = size

    pop_list = []
    for i in range(pop_size):
        newparam = []
        for k in params:
            k = k * np.random.normal(1, 0.1)
            k = round(k, 4)
            newparam.append(k)

        pop_list.append(newparam)
    return pop_list

def create_new_set():
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
    best_fitness = best
    second_fitness = second

    fittest_set = one
    second_set = two

    for i in pop:
        try:
            fitness = multi_core_test(min, max, i)
        except:
            fitness = 1

        print fitness
        if fitness < best_fitness:
            #move current best to second best
            second_fitness = best_fitness
            second_set = fittest_set

            best_fitness = fitness
            fittest_set = i
        elif fitness < second_fitness:
            second_fitness = fitness
            second_set = i

    print "best_fitness"
    print best_fitness
    print " "
    return (fittest_set, best_fitness, second_set, second_fitness)

def mutate_population(children, fittest, second, mutants):
    pop_list = []

    #breed parents to create children
    def breed(sprogs, p1, p2):
        for i in range(sprogs):
            child = []
            count = 0
            for k in p1:
                a = random.random()
                if a < 0.5:
                    k = p2[count]
                    child.append(k)
                else:
                    child.append(k)

                count +=1
            pop_list.append(child)

    breed(children, fittest, second)

    rand1 = create_new_set()
    rand2 = create_new_set()
    breed(2, fittest, rand1)

    breed(2, fittest, rand2)
    #create mutants
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

if __name__ == '__main__':
    min = 40
    max = 70
    #params = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]

    #best_fitness =  multi_core_test(min, max, params)
    #second_fitness =  0.259090961264
    second_fitness =  0.28
    fittest_set = []
    second_set = []

    new_pop = create_new_population(10)
    fit_results = test_population(new_pop, 10, 10, fittest_set, second_set)
    fittest_set = fit_results[0]
    print fittest_set
    best_fitness = fit_results[1]
    print best_fitness
    second_set = fit_results[2]
    new_pop = mutate_population(4, fittest_set, second_set, 6 )

    for i in range(10):
        fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)
        fittest_set = fit_results[0]
        print fittest_set
        best_fitness = fit_results[1]
        print best_fitness
        second_set = fit_results[2]
        second_fitness = fit_results[3]
        new_pop = mutate_population(4, fittest_set, second_set, 6 )
