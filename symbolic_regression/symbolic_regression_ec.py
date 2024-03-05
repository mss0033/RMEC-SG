import numpy as np
import random
from deap import base, creator, gp, tools 
import operator

# Defining Functions (Our Building Blocks)
def protected_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1

pset = gp.PrimitiveSet("MAIN", 1)  # 'MAIN' is the name of the function 
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protected_div, 2)
pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1)) 
pset.renameArguments(ARG0='x')  

# Fitness Function and Individual/Population Setup
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimize error
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2) 
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def evaluate(individual, points):
    func = toolbox.compile(expr=individual)
    mse = np.mean((func(*x) - y)**2 for x, y in points)  
    return mse,

# Generating Data
x_data = np.linspace(-1, 1, 50)
y_data = x_data**2 + np.random.rand(len(x_data)) * 0.2  # True function with noise
data_points = list(zip(x_data, y_data))

# Basic Evolutionary Setup
pop = toolbox.population(n=500)
toolbox.register("evaluate", evaluate, points=data_points)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

# Basic Evolutionary Loop
NUM_GENERATIONS = 20  # Adjust as needed

for gen in range(NUM_GENERATIONS):
    offspring = tools.selTournament(pop, len(pop), tournsize=3)
    offspring = [toolbox.clone(ind) for ind in offspring]

    # Apply crossover and mutation
    for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.7:  # Sample crossover probability
            toolbox.mate(ind1, ind2)
            del ind1.fitness.values
            del ind2.fitness.values

    for mutant in offspring:
        if random.random() < 0.2:  # Sample mutation probability
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Evaluate fitness of the new individuals
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    pop[:] = offspring

# Placeholder for Examining Results 
best_individual = tools.selBest(pop, 1)[0]
print("Best Individual:", best_individual)
print("Fitness:", best_individual.fitness.values[0])

# *** Placeholder for HITL Integration ***
# You'll add code to:
# 1. Present solutions to human reviewers
# 2. Capture feedback 
# 3. Modify the evolution process (e.g., fitness, selection) based on feedback 
