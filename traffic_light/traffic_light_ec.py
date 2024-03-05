# Let's create a basic Python file that sets up the framework for an Evolutionary Computing (EC) approach to optimizing traffic light timing.
# This script will outline the structure for initializing the population, evaluating fitness, and evolving the population over generations.
import random
import matplotlib.pyplot as plt
import numpy as np

# Parameters
population_size = 50
num_intersections = 5
max_light_duration = 120
min_light_duration = 10
initial_mutation_rate = 0.1
num_generations = 100
vehicles_per_minute = [15, 25, 20, 30, 10]  # Variable traffic flow at different intersections

# Initialize population
def initialize_population():
    return [[random.randint(min_light_duration, max_light_duration) for _ in range(num_intersections)] for _ in range(population_size)]

# Enhanced fitness evaluation
def evaluate_fitness(individual):
    total_throughput = 0
    total_waiting_time = 0
    for i, light_duration in enumerate(individual):
        vehicles_passed = (vehicles_per_minute[i] / 60) * light_duration
        waiting_time = (sum(individual) - light_duration) * vehicles_per_minute[i]
        total_throughput += vehicles_passed
        total_waiting_time += waiting_time
    # Use a more nuanced fitness calculation
    fitness = total_throughput - np.log(1 + total_waiting_time)
    return fitness

# Improved selection mechanism
def tournament_selection(population, fitnesses, k=3):
    selected_indices = np.random.choice(range(len(population)), k, replace=False)
    best_index = selected_indices[0]
    for index in selected_indices[1:]:
        if fitnesses[index] > fitnesses[best_index]:
            best_index = index
    return population[best_index]

# Crossover
def crossover(parent1, parent2):
    crossover_point = random.randint(1, num_intersections-1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

# Mutation with dynamic rate
def mutate(individual, mutation_rate):
    if random.random() < mutation_rate:
        mutation_point = random.randint(0, num_intersections-1)
        individual[mutation_point] = random.randint(min_light_duration, max_light_duration)
    return individual


# Dynamic mutation rate
def adjust_mutation_rate(generation):
    return initial_mutation_rate * (1 - (generation / num_generations))

# Evolution loop with elitism and dynamic mutation rate
def evolve() -> list:
    population = initialize_population()
    best_individual = None
    best_fitness = float('-inf')
    
    for generation in range(num_generations):
        fitnesses = [evaluate_fitness(individual) for individual in population]
        new_population = [population[np.argmax(fitnesses)]]  # Elitism: carry over the best
        
        if max(fitnesses) > best_fitness:
            best_fitness = max(fitnesses)
            best_individual = population[np.argmax(fitnesses)]
        
        while len(new_population) < population_size:
            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)
            child1, child2 = crossover(parent1, parent2)
            mutation_rate = adjust_mutation_rate(generation)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])
        population = new_population
        print(f"Generation {generation+1}: Best Fitness = {best_fitness}")
    print(f"Best individual: {best_individual}")
    return best_individual

# Visualize an individual
def visualize_traffic_flow(best_individual):
    """
    Visualizes traffic flow for the best individual.
    """
    num_intervals = 10  # Number of time intervals to simulate
    interval_duration = 30  # Duration of each time interval in seconds
    
    # Initialize traffic flow and queue for each intersection
    traffic_flow = np.zeros((num_intersections, num_intervals))
    queue_lengths = np.zeros((num_intersections, num_intervals))
    
    for i in range(num_intersections):
        green_time_remaining = best_individual[i]
        for j in range(num_intervals):
            # Simulate arrival of vehicles
            arrivals = np.random.poisson(vehicles_per_minute[i] * (interval_duration / 60))
            
            if green_time_remaining > 0:
                # All vehicles pass through if the light is green
                traffic_flow[i, j] = arrivals
                green_time_remaining -= interval_duration
            else:
                # Vehicles queue up if the light is red
                queue_lengths[i, j] = arrivals
            
            # Reset green time after a full cycle
            if green_time_remaining <= 0:
                green_time_remaining = sum(best_individual) - best_individual[i]
    
    # Plotting
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    
    for i in range(num_intersections):
        axs[0].plot(range(num_intervals), traffic_flow[i, :], label=f'Intersection {i+1} Flow')
        axs[1].plot(range(num_intervals), queue_lengths[i, :], label=f'Intersection {i+1} Queue')
    
    axs[0].set_title('Traffic Flow Over Time')
    axs[0].set_xlabel('Time Interval')
    axs[0].set_ylabel('Vehicles Passed')
    
    axs[1].set_title('Queue Length Over Time')
    axs[1].set_xlabel('Time Interval')
    axs[1].set_ylabel('Vehicles Queued')
    
    axs[0].legend()
    axs[1].legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_traffic_flow(evolve())