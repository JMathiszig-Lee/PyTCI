import random
import numpy as np

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

def creat_new_population(size):
    pop_size = size

    pop_list = []
    for i in range(pop_size):
        newparam = create_new_set()
        pop_list.append(newparam)
    return pop_list

if __name__ == '__main__':
    psize = 3
    print create_population(psize)
    print creat_new_population(psize)
