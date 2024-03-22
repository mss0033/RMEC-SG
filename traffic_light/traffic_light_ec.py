import datetime
import libsumo as traci
import numpy as np
import random
import re
import os
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

# Some commonly used directory paths
NETWORK_CONFIGS_DIR = "traffic_light/network_configs"
ROUTE_CONFIGS_DIR = "traffic_light/route_configs"
SUMO_CONFIGS_DIR = "traffic_light/sumo_configs"
ORIGINALS_DIR = "originals"
BEST_INDIVIDUALS_DIR = "best_individuals"

# Number of concurrent simulations to run
NUM_SIMS = 24

# Sumo commands
SUMO_BINARY = f"/usr/bin/sumo"
SUMO_ROUTE = f"{ROUTE_CONFIGS_DIR}/grid_network_0_routes_stairstep.rou.xml"
SUMO_CMD = [SUMO_BINARY, "-r", SUMO_ROUTE, "--no-warnings", "true"]

# Evolutionary algorithm parameters
POPULATION_SIZE = 100
TOURNAMENT_SIZE = 20
MUTATION_RATE = 0.25
NUM_GENERATIONS = 50

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
def write_population_to_files(population: List[TLLogicSet], 
                              generation: int, 
                              run_label: 'str'):
    # Write the population to the config files
    for id, indiv in enumerate(population):
        indiv_prev_gen_file = f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation - 1}/grid_network_{id}_modified.net.xml"
        indiv_next_gen_file = f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{id}_modified.net.xml"
        # Try to open an exisiting file for the specific individual
        try:
            # If the file is present, read the contents, update them, and write the update back to the file
            with open(indiv_prev_gen_file, 'r') as file:
                indiv_xml_string = file.read()
                file.close()
            if indiv_xml_string:
                updated_xml_string = write_tl_logic(indiv_xml_string, indiv.tllogics)
                os.makedirs(os.path.dirname(indiv_next_gen_file), exist_ok=True)
                with open(indiv_next_gen_file, 'w') as file:
                    file.write(beautify_xml(xml_str=updated_xml_string))
                    file.flush()
                    file.close()
        # If an corresponding file for the given id of an individual is not present, try to open the original file
        except FileNotFoundError as fnfe:
            # Open the 
            original_file = f"{NETWORK_CONFIGS_DIR}/originals/grid_network_original.net.xml"
            with open(original_file, 'r') as file:
                original_xml_string = file.read()
                file.close()
            if original_xml_string:
                updated_xml_string = write_tl_logic(original_xml_string, indiv.tllogics)
                os.makedirs(os.path.dirname(indiv_next_gen_file), exist_ok=True)
                with open(indiv_next_gen_file, 'w') as file:
                    file.write(beautify_xml(xml_str=updated_xml_string))
                    file.flush()
                    file.close()

# Writes the best individual found by evolution to a marked file so it can easily be used or recovered
def write_best_indiv_to_file(index: int, 
                             generation: int, 
                             run_label: str, 
                             best_indiv: TLLogicSet):
    with open(f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{index}_modified.net.xml", 'r') as file:
        best_indiv_xml_string = file.read()
        file.close()
    if best_indiv_xml_string:
        updated_xml_string = write_tl_logic(best_indiv_xml_string, best_indiv.tllogics)
        path = f"{NETWORK_CONFIGS_DIR}/{run_label}/{BEST_INDIVIDUALS_DIR}/grid_network_best_indiv_{run_label}_{datetime.datetime.now()}.net.xml"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            file.write(beautify_xml(xml_str=updated_xml_string))
            file.flush()
            file.close()

# Method used to initialize the population
def initialize_population(population_size: 'int', 
                          generation: int, 
                          run_label: 'str', 
                          template_tllogics: 'TLLogicSet') -> List[TLLogicSet]:
    population = []
    for _ in range(population_size):
        tllogic_set = get_deepcopy_of_tllogic_set(template_tllogics)
        population.append(tllogic_set)

    # Write the population to the config files
    write_population_to_files(population=population, run_label=run_label, generation=generation)
    return population

# Method used to initialize the population from existing network files
def initialize_population_from_exiting(population_size: 'int', 
                                       generation: int, 
                                       run_label: str, 
                                       template_tllogics: 'TLLogicSet') -> List[TLLogicSet]:
    population = []
    # Read in the original network file with decent traffic light phases
    for i in range(population_size):
        try:
            with open(f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{i}_modified.net.xml", 'r') as file:
                xml_string = file.read()
                file.close()

            # Create an original logic set from which futher sets will be born
            if xml_string:
                population.append(TLLogicSet(tllogics=parse_tl_logic(xml_string)))
        except FileNotFoundError as fnfe:
            tllogic_set = get_deepcopy_of_tllogic_set(template_tllogics)
            population.append(tllogic_set)

    return population

# Only take the top % of individuals
def max_fitness_selection(population: List[TLLogicSet]) -> List[TLLogicSet]:
    population.sort(key=lambda x: x.fitness)
    return [deepcopy(indiv) for indiv in population[:POPULATION_SIZE // 10]]

def tournament_selection(population: List['TLLogicSet'], 
                         tournament_size: 'int') -> List['TLLogicSet']:
    selected_individuals = []
    for _ in range(len(population)):
        tournament = random.sample(population, tournament_size)
        best_individual = min(tournament, key=lambda x: x.fitness)
        selected_individuals.append(deepcopy(best_individual))
    return selected_individuals

def run_simulation(index: 'int', 
                   generation: int, 
                   run_label: str, 
                   return_dict: dict):
    # Start SUMO simulation
    traci.start(SUMO_CMD + ["-n", f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{index}_modified.net.xml"], label=f"{index}")
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
def evaluate_population(population: List[TLLogicSet], 
                        generation: int, 
                        run_label: str):
    manager = Manager()
    return_dict = manager.dict()
    # for (index, indiv) in enumerate(population):
    #     indiv.fitness = run_simulation(index=index, return_dict=return_dict)
    processes = []
    for (index, indiv) in enumerate(population):
        process = Process(target=run_simulation, args=(index, generation, run_label, return_dict))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

    for (key, value) in return_dict.items():
        population[key].fitness = value

# Identify potentially specification gamed individuals
def identify_specification_gaming_individuals(population: List[TLLogicSet]) -> dict[int, TLLogicSet]:
    fitness_values = [individual.fitness for individual in population]
    mean_fitness = np.mean(fitness_values)
    std_dev_fitness = np.std(fitness_values)
    
    potential_gaming_individuals = {
        population.index(individual): individual for individual in population
        if individual.fitness < mean_fitness - 2 * std_dev_fitness or
           individual.fitness > mean_fitness + 2 * std_dev_fitness
    }
    
    return potential_gaming_individuals

# Take actions against SG individuals
def mitigate_sg_individuals(potentially_sg_indiv: dict[int, TLLogicSet]):
    pass

# Main body function for the overall evolutionary algorithm
def evolutionary_algorithm(population_size: int = POPULATION_SIZE, 
                           num_generations: int = NUM_GENERATIONS, 
                           initialize_from_existing: tuple[bool, int] = (False, 0),
                           run_label: str = (f"Run_" + datetime.datetime.now().strftime("%Y_%m_%d_%HH%MM%SS"))):
    # Initialize population
    population = []
    template = read_in_tllogic_set_from_file(filename=f"{NETWORK_CONFIGS_DIR}/{ORIGINALS_DIR}/grid_network_original.net.xml")
    if initialize_from_existing[0]:
        population = initialize_population_from_exiting(population_size=population_size, generation=initialize_from_existing[1] - 1, run_label=run_label, template_tllogics=template)
    else:
        if not template:
            print("Unable to read in template file, exiting")
            return
        population = initialize_population(population_size, generation=0, run_label=run_label, template_tllogics=template)
    if len(population) <= 0:
        print(f"Error initializing population, unable to meaningfully fun EC")
        return
    if initialize_from_existing[0]:
        # Evaluate fitness of each individual
        evaluate_population(population=population, generation=initialize_from_existing[1] - 1, run_label=run_label)
    else:
        evaluate_population(population=population, generation=0, run_label=run_label)
    # Print some population stats
    print(f"Generation {initialize_from_existing[1]}")
    print(f"Best fitness: {min([inidiv.fitness for inidiv in population])}")
    print(f"Average fitness: {mean([inidiv.fitness for inidiv in population])}")
    print(f"Standard Deviation fitness: {stdev([inidiv.fitness for inidiv in population])}")

    for generation in range(initialize_from_existing[1], num_generations):
        print(f"Generation {generation + 1}")
        # Maximize selective pressure
        # Create new population; ensure survival of top n individuals
        new_population = max_fitness_selection(population)
        # Tournament selection
        selected_individuals = tournament_selection(population, TOURNAMENT_SIZE)
        # Fill the population in with some recombined and mutated individuals 
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected_individuals, 2)
            child1, child2 = parent1.recombine(parent2)
            child1.mutate(MUTATION_RATE)
            child2.mutate(MUTATION_RATE)
            new_population.extend([child1, child2])

        # Deepcopy for safety
        population = [deepcopy(indiv) for indiv in new_population[:population_size]]
        # Write the population to the config files
        write_population_to_files(population=population, run_label=run_label, generation=generation)
        # Evaluate the population
        evaluate_population(population=population, generation=generation, run_label=run_label)
        # Print some population stats
        print(f"Best fitness: {min([inidiv.fitness for inidiv in population])}")
        print(f"Average fitness: {mean([inidiv.fitness for inidiv in population])}")
        print(f"Standard Deviation fitness: {stdev([inidiv.fitness for inidiv in population])}")
        # Identify specification gaming individuals
        print(f"Potentially specification gaming individuals: {identify_specification_gaming_individuals(population=population).keys}")

        # # Find the best individual
        # best_individual = min(population, key=lambda x: x.fitness)
        # # Write the best individual to a config files
        # write_best_indiv_to_file(index=population.index(best_individual), best_indiv=best_individual)

    # Find the best individual
    best_individual = min(population, key=lambda x: x.fitness)
    # Write the best individual to a config files
    write_best_indiv_to_file(index=population.index(best_individual), generation=num_generations - 1, run_label=run_label, best_indiv=best_individual)
        
    return best_individual

# Overwrite the main function cause that seems to be the thing to do in python
if __name__ == "__main__":
    print(str(evolutionary_algorithm()))

# print(f"Phases: {[phase for sublist in [tllogic.phases for tllogic in test_set.tllogics] for phase in sublist]}")

# traci.set_phases(phases=[phase for sublist in [tllogic.phases for tllogic in test_set.tllogics] for phase in sublist])

# traci.start(SUMO_CMD + ["-n", f"{NETWORK_CONFIGS_DIR}/grid_network_best_indiv_saved_1.net.xml"])
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