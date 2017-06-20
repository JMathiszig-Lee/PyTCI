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
    for i in range(children):
        child = []
        count = 0
        for k in fittest:
            a = random.random()
            if a < 0.5:
                k = second[count]
                child.append(k)
            else:
                child.append(k)

            count +=1

        pop_list.append(child)

    #creat mutants
    for i in range(mutants):
        mutant = []
        for k in params:
            b = random.random()
            if b < 0.3:
                mut_factor = 0.3
            else:
                mut_factor = 0.1
            k = k * np.random.normal(1, mut_factor)
            k = round(k, 4)
            mutant.append(k)

        pop_list.append(mutant)

    return pop_list

if __name__ == '__main__':
    min = 1
    max = 50
    params = [0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177]

    best_fitness =  multi_core_test(min, max, params)
    #second_fitness =  0.259090961264
    second_fitness =  0.28
    print best_fitness
    fittest_set = params
    second_set = params

    new_pop = create_population(10)

    for i in range(10):
        fit_results = test_population(new_pop, best_fitness, second_fitness, fittest_set, second_set)
        fittest_set = fit_results[0]
        print fittest_set
        best_fitness = fit_results[1]
        second_set = fit_results[2]
        second_fitness = fit_results[3]
        new_pop = mutate_population(4, fittest_set, second_set, 6 )
