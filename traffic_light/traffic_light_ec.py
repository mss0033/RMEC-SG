import datetime
import libsumo as traci
import numpy as np
import random
import re
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
from xml.dom.minidom import parseString

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

def read_in_tllogic_set_from_file(filename: str) -> TLLogicSet:
# Read in the original network file with decent traffic light phases
    with open(filename, 'r') as file:
        xml_string_og = file.read()
        file.close()

    # Create an original logic set from which futher sets will be born
    if xml_string_og:
        return TLLogicSet(tllogics=parse_tl_logic(xml_string_og))

# Randomizes the phases of a given TLLogic object
def apply_entropy_to_tllogic(tllogic: 'TLLogic'):
    # for phase in tllogic.phases:
        # phase.apply_entropy()
    return tllogic

# Create traffic light logic set from the original
def get_deepcopy_of_tllogic_set(template_tllogic_set: 'TLLogicSet'):
    return deepcopy(template_tllogic_set)

def beautify_xml(xml_str: str) -> str:
    # Parse the XML string
    dom = parseString(xml_str)
    # Beautify the XML with toprettyxml
    pretty_xml = dom.toprettyxml()
    # Use a regular expression to remove blank lines
    pretty_xml_without_blanks = re.sub(r'^\s*\n', '', pretty_xml, flags=re.MULTILINE)

    return pretty_xml_without_blanks

# Writes the population to the config files
def write_population_to_files(population: List[TLLogicSet]):
    # Write the population to the config files
    for id, indiv in enumerate(population):
        indiv_file = f"traffic_light/network_configs/grid_network_{id}_modified.net.xml"
        with open(indiv_file, 'r') as file:
            indiv_xml_string = file.read()
            file.close()
        if indiv_xml_string:
            updated_xml_string = write_tl_logic(indiv_xml_string, indiv.tllogics)
            with open(indiv_file, 'w') as file:
                file.write(beautify_xml(xml_str=updated_xml_string))
                file.flush()
                file.close()

# Writes the best individual found by evolution to a marked file so it can easily be used or recovered
def write_best_indiv_to_file(index: int, best_indiv: TLLogicSet):
    with open(f"traffic_light/network_configs/grid_network_{index}_modified.net.xml", 'r') as file:
        best_indiv_xml_string = file.read()
        file.close()
    if best_indiv_xml_string:
        updated_xml_string = write_tl_logic(best_indiv_xml_string, best_indiv.tllogics)
        with open(f"traffic_light/network_configs/grid_network_best_indiv_{datetime.datetime.now()}.net.xml", 'w') as file:
            file.write(beautify_xml(xml_str=updated_xml_string))
            file.flush()
            file.close()

# Method used to initialize the population
def initialize_population(population_size: 'int', template_tllogics: 'TLLogicSet') -> List[TLLogicSet]:
    population = []
    for _ in range(population_size):
        tllogic_set = get_deepcopy_of_tllogic_set(template_tllogics)
        population.append(tllogic_set)

    # Write the population to the config files
    write_population_to_files(population=population)
    return population

# Method used to initialize the population from existing network files
def initialize_population_from_exiting(population_size: 'int') -> List[TLLogicSet]:
    population = []
    # Read in the original network file with decent traffic light phases
    for i in range(population_size):
        with open(f"traffic_light/network_configs/grid_network_{i}_modified.net.xml", 'r') as file:
            xml_string = file.read()
            file.close()

        # Create an original logic set from which futher sets will be born
        if xml_string:
            population.append(TLLogicSet(tllogics=parse_tl_logic(xml_string)))

    return population

# Only take the top % of individuals
def max_fitness_selection(population: List[TLLogicSet]) -> List[TLLogicSet]:
    population.sort(key=lambda x: x.fitness)
    return [deepcopy(indiv) for indiv in population[:population_size // 10]]

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
    # Initialize the fitness for the index
    return_dict[index] = 0
    # start_time = time()
    steps = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        steps += 1

    # Calculate fitness based on how long the simulation took
    # return_dict[index] = traci.simulation.getTime()
    simulation_time = traci.simulation.getTime()
    return_dict[index] = steps
    # Close SUMO simulation
    # traci.simulation.close()
    traci.close()
    return steps

# Facilitate multiprocessing of inidividuals
def evaluate_population(population: List[TLLogicSet]):
    manager = Manager()
    return_dict = manager.dict()
    for (index, indiv) in enumerate(population):
        indiv.fitness = run_simulation(index=index, return_dict=return_dict)
    # processes = []
    # for (index, indiv) in enumerate(population):
    #     process = Process(target=run_simulation, args=(index, return_dict))
    #     processes.append(process)
    #     process.start()
    
    # for process in processes:
    #     process.join()

    # for (key, value) in return_dict.items():
    #     population[key].fitness = value
        
def identify_specification_gaming_individuals(population: List[TLLogicSet]):
    fitness_values = [individual.fitness for individual in population]
    mean_fitness = np.mean(fitness_values)
    std_dev_fitness = np.std(fitness_values)
    
    potential_gaming_individuals = [
        individual for individual in population
        if individual.fitness < mean_fitness - 2 * std_dev_fitness or
           individual.fitness > mean_fitness + 2 * std_dev_fitness
    ]
    
    return potential_gaming_individuals

def evolutionary_algorithm():
    # Initialize population
    template = read_in_tllogic_set_from_file(filename=f"traffic_light/network_configs/grid_network_best_indiv_saved_1.net.xml")
    if not template:
        print("Unable to read in template file, exiting")
        return
    population = initialize_population(population_size, template_tllogics=template)
    # population = initialize_population_from_exiting(population_size=population_size)
    # Evaluate fitness of each individual
    evaluate_population(population)
    # Print some population stats
    print("Generation 0")
    print(f"Best fitness: {min([inidiv.fitness for inidiv in population])}")
    print(f"Average fitness: {mean([inidiv.fitness for inidiv in population])}")
    print(f"Standard Deviation fitness: {stdev([inidiv.fitness for inidiv in population])}")

    for generation in range(num_generations):
        print(f"Generation {generation + 1}")
        # Maximize selective pressure
        # Create new population; ensure survival of top n individuals
        new_population = max_fitness_selection(population)
        # Tournament selection
        selected_individuals = tournament_selection(population, tournament_size)
        # Fill the population in with some recombined and mutated individuals 
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected_individuals, 2)
            child1, child2 = parent1.recombine(parent2)
            child1.mutate(mutation_rate)
            child2.mutate(mutation_rate)
            new_population.extend([child1, child2])

        # Deepcopy for safety
        population = [deepcopy(indiv) for indiv in new_population[:population_size]]
        # Write the population to the config files
        write_population_to_files(population=population)
        # Evaluate the population
        evaluate_population(population=population)
        # Print some population stats
        print(f"Best fitness: {min([inidiv.fitness for inidiv in population])}")
        print(f"Average fitness: {mean([inidiv.fitness for inidiv in population])}")
        print(f"Standard Deviation fitness: {stdev([inidiv.fitness for inidiv in population])}")
        # # Find the best individual
        # best_individual = min(population, key=lambda x: x.fitness)
        # # Write the best individual to a config files
        # write_best_indiv_to_file(index=population.index(best_individual), best_indiv=best_individual)

    # Find the best individual
    best_individual = min(population, key=lambda x: x.fitness)
    # Write the best individual to a config files
    write_best_indiv_to_file(index=population.index(best_individual), best_indiv=best_individual)
        
    return best_individual

# Overwrite the main function cause that seems to be the thing to do in python
if __name__ == "__main__":
    print(str(evolutionary_algorithm()))

# print(f"Phases: {[phase for sublist in [tllogic.phases for tllogic in test_set.tllogics] for phase in sublist]}")

# traci.set_phases(phases=[phase for sublist in [tllogic.phases for tllogic in test_set.tllogics] for phase in sublist])

# traci.start(SUMO_CMD + ["-n", f"traffic_light/network_configs/grid_network_best_indiv_saved_1.net.xml"])
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