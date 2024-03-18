import datetime
import libsumo as traci
import random
import traci.constants as tc

from copy import deepcopy
from math import log
from multiprocessing import Manager, Process
from parse_traffic_light_logic_xml import parse_tl_logic, write_tl_logic
from statistics import mean, stdev
from time import time
from tllogic_indiv import TLLogic
from tllogic_set import TLLogicSet
from typing import List

# Number of concurrent simulations to run
NUM_SIMS = 24

# Sumo commands
SUMO_BINARY = "/usr/bin/sumo"
SUMO_ROUTE = "traffic_light/route_configs/grid_network_0_routes_stairstep.rou.xml"
SUMO_CMD = [SUMO_BINARY, "-r", SUMO_ROUTE, "--no-warnings", "true"]

# Evolutionary algorithm parameters
population_size = 100
tournament_size = 20
mutation_rate = 0.25
recombination_rate = 0.7
num_generations = 50

# Read in the original network file with decent traffic light phases
xml_file = 'traffic_light/network_configs/grid_network_original.net.xml'
with open(xml_file, 'r') as file:
    xml_string = file.read()

# Create an original logic set from which futher sets will be born
if xml_string:
    original_set = TLLogicSet(tllogics=parse_tl_logic(xml_string))
    # print(test_set)

# Randomizes the phases of a given TLLogic object
def apply_entropy_to_tllogic(tllogic: 'TLLogic'):
    # for phase in tllogic.phases:
        # phase.apply_entropy()
    return tllogic

# Create traffic light logic sets from the original
def create_tllogic_set_from_template(template_tllogic_set: 'TLLogicSet'):
    tllogics = []
    for tllogic in template_tllogic_set.tllogics:
        new_tllogic = deepcopy(tllogic)
        # apply_entropy_to_tllogic(new_tllogic)
        tllogics.append(new_tllogic)
    return TLLogicSet(tllogics)

# Method used to initialize the population
def initialize_population(population_size: 'int', template_tllogics: 'TLLogicSet'):
    population = []
    for _ in range(population_size):
        tllogic_set = create_tllogic_set_from_template(template_tllogics)
        population.append(tllogic_set)

    # Write the population to the config files
    for id, indiv in enumerate(population):
        updated_xml_string = write_tl_logic(xml_string, indiv.tllogics)
        with open(f"traffic_light/network_configs/grid_network_{id}_modified.net.xml", 'w') as file:
            file.write(updated_xml_string)
        # print(f"{indiv}")
    return population

# Method used to initialize the population from existing network files
def initialize_population_from_exiting(population_size: 'int'):
    population = []
    # Read in the original network file with decent traffic light phases
    for i in range(population_size):
        with open(f"traffic_light/network_configs/grid_network_{i}_modified.net.xml", 'r') as file:
            xml_string = file.read()

        # Create an original logic set from which futher sets will be born
        if xml_string:
            population.append(TLLogicSet(tllogics=parse_tl_logic(xml_string)))

    return population

# Only take the top % of individuals
def max_fitness_selection(population: List[TLLogicSet]):
    population.sort(key=lambda x: x.fitness)
    return population[:population_size // 3]

def tournament_selection(population: List['TLLogicSet'], tournament_size: 'int') -> List['TLLogicSet']:
    selected_individuals = []
    for _ in range(len(population)):
        tournament = random.sample(population, tournament_size)
        best_individual = min(tournament, key=lambda x: x.fitness)
        selected_individuals.append(deepcopy(best_individual))
    return selected_individuals

def run_simulation(index: 'int', return_dict: dict):
    # Start SUMO simulation
    traci.start(SUMO_CMD + ["-n", f"traffic_light/network_configs/grid_network_{index}_modified.net.xml"], label=f"{index}")
    # Get the step length
    # stepLength = traci.simulation.getDeltaT()
    # # Get the junction IDs
    # junctionID = traci.junction.getIDList()[traci.junction.getIDCount()//2]
    # # Subscribe to each junction
    # traci.junction.subscribeContext(
    #         junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 1000000,
    #         [tc.VAR_SPEED, tc.VAR_ALLOWED_SPEED]
    # )
    # Initialize the fitness for the index
    return_dict[index] = 0
    # start_time = time()
    while traci.simulation.getMinExpectedNumber() > 0:
    # num_steps = 0
    # while num_steps < 1_000:
        # num_steps += 1
        # Step the sim
        traci.simulationStep()
        # # For each junction
        # # Get the junction stats
        # scResults = traci.junction.getContextSubscriptionResults(junctionID)
        # halting = 0
        # if scResults:
        #     relSpeeds = [d[tc.VAR_SPEED] / d[tc.VAR_ALLOWED_SPEED] for d in scResults.values()]
        #     # compute values corresponding to summary-output
        #     running = len(relSpeeds)
        #     halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1])
        #     meanSpeedRelative = sum(relSpeeds) / running
        #     timeLoss = (1 - meanSpeedRelative) * running * stepLength
        #     # print(f"Sim time: {traci.simulation.getTime()}, timeloss: {timeLoss}, haulting: {halting}")
        #     if (timeLoss + halting <= 0):
        #         return_dict[index] += 0
        #     else:
        #         return_dict[index] += log(timeLoss + halting)

    # Calculate fitness based on how long the simulation took
    return_dict[index] = traci.simulation.getTime()
    # Close SUMO simulation
    traci.close()

# Facilitate multiprocessing of inidividuals
def evaluate_population(population: List[TLLogicSet]):
    manager = Manager()
    return_dict = manager.dict()
    # for (index, indiv) in enumerate(population):
    #     run_simulation(index=index, return_dict=return_dict)
    processes = []
    for (index, indiv) in enumerate(population):
        process = Process(target=run_simulation, args=(index, return_dict))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

    for (key, value) in return_dict.items():
        population[key].fitness = value

def evolutionary_algorithm():
    # Initialize population
    # population = initialize_population(population_size, template_tllogics=original_set)
    population = initialize_population_from_exiting(population_size=population_size)
    # Evaluate fitness of each individual
    evaluate_population(population)

    for generation in range(num_generations):
        print(f"Generation {generation + 1}")

        # Tournament selection
        selected_individuals = tournament_selection(population, tournament_size)
        # Maximize selective pressure
        # selected_individuals = max_fitness_selection(population=population)

        # Create new population
        new_population = []
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected_individuals, 2)
            child1, child2 = parent1.recombine(parent2)
            child1.mutate(mutation_rate)
            child2.mutate(mutation_rate)
            new_population.extend([child1, child2])

        population = new_population[:population_size]
        evaluate_population(population=population)
        print(f"Best fitness: {min([inidiv.fitness for inidiv in population])}")
        print(f"Average fitness: {mean([inidiv.fitness for inidiv in population])}")
        print(f"Standard Deviation fitness: {stdev([inidiv.fitness for inidiv in population])}")
        # Write the population to the config files
        for id, indiv in enumerate(population):
            updated_xml_string = write_tl_logic(xml_string, indiv.tllogics)
            with open(f"traffic_light/network_configs/grid_network_{id}_modified.net.xml", 'w') as file:
                file.write(updated_xml_string)


    # Find the best individual
    best_individual = min(population, key=lambda x: x.fitness)
    # Write the best individual to a config files
    updated_xml_string = write_tl_logic(xml_string, best_individual.tllogics)
    with open(f"traffic_light/network_configs/grid_network_best_indiv_{datetime.datetime.now()}.net.xml", 'w') as file:
        file.write(updated_xml_string)
        
    return best_individual

# Overwrite the main function cause that seems to be the thing to do in python
if __name__ == "__main__":
    print(str(evolutionary_algorithm()))

# print(f"Phases: {[phase for sublist in [tllogic.phases for tllogic in test_set.tllogics] for phase in sublist]}")

# traci.set_phases(phases=[phase for sublist in [tllogic.phases for tllogic in test_set.tllogics] for phase in sublist])

# traci.start(SUMO_CMD + ["-n", f"traffic_light/network_configs/grid_network_best_indiv_saved_0.net.xml"])
# # pick an arbitrary junction
# # junctionID = traci.junction.getIDList()[0]
# # # subscribe around that junction with a sufficiently large
# # # radius to retrieve the speeds of all vehicles in every step
# # traci.junction.subscribeContext(
# #     junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 1000000,
# #     [tc.VAR_SPEED, tc.VAR_ALLOWED_SPEED]
# # )
# # Get the step length
# # stepLength = traci.simulation.getDeltaT()
# sim_start_time = time()
# while traci.simulation.getMinExpectedNumber() > 0:
#     traci.simulationStep()
#     # scResults = traci.junction.getContextSubscriptionResults(junctionID)
#     # halting = 0
#     # if scResults:
#     #     relSpeeds = [d[tc.VAR_SPEED] / d[tc.VAR_ALLOWED_SPEED] for d in scResults.values()]
#     #     # compute values corresponding to summary-output
#     #     running = len(relSpeeds)
#     #     halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1])
#     #     meanSpeedRelative = sum(relSpeeds) / running
#     #     timeLoss = (1 - meanSpeedRelative) * running * stepLength
# print(traci.simulation.getTime())
# print(f"Time taken by simulation: {time() - sim_start_time}")
# traci.close()