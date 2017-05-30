#playing around with genetics with the deap library

from deap import base, creator, tools
from crosscorrelate import test_against_real_data
import random

# params = {
#     'k10a': 0.443,
#     'k10b': 0.0107,
#     'k10c': -0.0159,
#     'k10d': 0.0062,
#     'k12a': 0.302,
#     'k12b': -0.0056,
#     'k13': 0.196,
#     'k21a': 1.29,
#     'k21b': -0.024,
#     'k21c': 18.9,
#     'k21d': -0.391,
#     'k31': 0.0035,
#     'v1': 4.27,
#     'v3': 238,
#     'age_offset': 53,
#     'weight_offset': 77,
#     'lbm_offset': 59,
#     'height_offset': 177
# }

#params = (0.443, 0.0107, -0.0159, 0.0062, 0.302, -0.0056, 0.196, 1.29, -0.024, 18.9, -0.391, 0.0035, 4.27, 238, 53, 77, 59, 177)

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform(-0.5, 1))
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=18)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", test_against_real_data, 1, 10 ) #numbers are min and max patient number


def main():
    pop = toolbox.population(n=10)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 40
    print pop
    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for g in range(NGEN):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = map(toolbox.clone, offspring)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring
        pop[:] = offspring

    return pop

print main()
