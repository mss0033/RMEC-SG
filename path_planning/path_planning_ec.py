import numpy as np
import matplotlib.pyplot as plt 
from deap import base, creator, algorithms, tools
import random

# Environment Setup
MAZE_SIZE = (20, 20)
START = (0, 0)
GOAL = (MAZE_SIZE[0] - 1, MAZE_SIZE[1] - 1)
maze = np.zeros(MAZE_SIZE)
maze[3:8, 5] = 1  
maze[10:15, 12] = 1

# Path Representation
def generate_path(length):
    path = [START]
    for _ in range(length):
        x, y = path[-1]
        possible_moves = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        valid_moves = [(dx, dy) for dx, dy in possible_moves if 0 <= dx < MAZE_SIZE[0] and 0 <= dy < MAZE_SIZE[1] and maze[dx, dy] == 0]
        next_move = random.choice(valid_moves)
        path.append(next_move)
    return path

# Fitness Evaluation
def evaluate_path(individual):
    path = individual
    distance_to_goal = np.linalg.norm(np.array(path[-1]) - np.array(GOAL))
    collisions = sum(maze[x, y] for x, y in path)
    fitness =  distance_to_goal + collisions * 5 
    return fitness,  

# Evolutionary Setup (DEAP)
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("path", generate_path, length=30) 
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.path)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_path)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", tools.cxOnePoint) 
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)

# Visualization 
def plot_maze_and_path(path):
    plt.imshow(maze, cmap='gray')
    plt.plot(*zip(*path), color='red')
    plt.scatter(*START, color='green', s=80)
    plt.scatter(*GOAL, color='blue', s=80)
    plt.show()

# Basic Evolutionary Loop
NUM_GENERATIONS = 50 
POPULATION_SIZE = 100

pop = toolbox.population(n=POPULATION_SIZE)

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

best_individual = tools.selBest(pop, 1)[0]
plot_maze_and_path(best_individual)
print("Fitness:", best_individual.fitness.values[0])

# *** Placeholder for HITL Integration *** 
