import datetime
import libsumo
import traci
import numpy as np
import random
import re
import os
import traci.constants as tc

from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from math import log
from multiprocessing import Manager
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
TLLOGIC_SEED_INDIV_CONFIG = "grid_network_original.net.xml"

# Number of concurrent simulations to run
NUM_SIMS = 24

# Number of steps the original TLS took to run a given route
STEPS_OG_STAIRSTEP = 17903
STEPS_OG_RANDOM_LIST = [3792, 3758, 3813, 3801, 5952, 3792, 3747, 3767, 3756]

# Sumo commands
SUMO_BINARY = f"/usr/bin/sumo"
SUMO_GUI_BINARY = f"/usr/bin/sumo-gui"
SUMO_STAIRSTEP_ROUTE = f"{ROUTE_CONFIGS_DIR}/grid_network_0_routes_stairstep.rou.xml"
SUMO_RANDOM_ROUTE = f"{ROUTE_CONFIGS_DIR}/grid_network_0_routes_random_4.rou.xml"
SUMO_CMD_STAIRSTEP = [SUMO_BINARY, "-r", SUMO_STAIRSTEP_ROUTE, "--no-warnings", "true"]
SUMO_CMD_RANDOM = [SUMO_BINARY, "--no-warnings", "true"]
SUMO_GUI_CMD = [SUMO_GUI_BINARY, "-r", SUMO_STAIRSTEP_ROUTE, "--no-warnings", "true"]
SUMO_GUI_CMD_RANDOM = [SUMO_GUI_BINARY, "-r", SUMO_RANDOM_ROUTE, "--no-warnings", "true"]

# Evolutionary algorithm parameters
POPULATION_SIZE = 100
TOURNAMENT_SIZE = 50
MUTATION_RATE = 0.50
NUM_GENERATIONS = 50
STAIRSTEP_FITNESS_SCALAR = 100
RANDOM_FITNESS_SCALAR = 10

# SG Mitigation Strats
STRAT_REPLACE = 'Replace'
STRAT_PENALIZE = 'Penalize'
STRAT_MOD_FITNESS = 'Mod_Fitness'

# def read_in_tllogic_set_from_file(filename: str) -> TLLogicSet:
# # Read in the original network file with decent traffic light phases
#     with open(filename, 'r') as file:
#         xml_string_og = file.read()
#         file.close()

#     # Create an original logic set from which futher sets will be born
#     if xml_string_og:
#         return TLLogicSet(tllogics=parse_tl_logic(xml_string_og))

# # Randomizes the phases of a given TLLogic object
# def apply_entropy_to_tllogic(tllogic: 'TLLogic'):
#     # for phase in tllogic.phases:
#         # phase.apply_entropy()
#     return tllogic

# # Create traffic light logic set from the original
# def get_deepcopy_of_tllogic_set(template_tllogic_set: 'TLLogicSet'):
#     return deepcopy(template_tllogic_set)

# def beautify_xml(xml_str: str) -> str:
#     # Parse the XML string
#     dom = parseString(xml_str)
#     # Beautify the XML with toprettyxml
#     pretty_xml = dom.toprettyxml()
#     # Use a regular expression to remove blank lines
#     pretty_xml_without_blanks = re.sub(r'^\s*\n', '', pretty_xml, flags=re.MULTILINE)

#     return pretty_xml_without_blanks

# # Writes a list of indices of potentially SG indivs to a file 
# def write_potential_sg_indivs_to_file(potential_sg_indivs: dict[int, TLLogicSet], 
#                                       generation: int, 
#                                       run_label: 'str'):
#     # Create a file in the generations dir that will hold the list of indices of potentially SG indivs form that generation
#     sg_file = f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/potential_sg_indiv_indexs.txt"
#     # Create the directory to ensure it exists when we try to open it for writing
#     os.makedirs(os.path.dirname(sg_file), exist_ok=True)
#     try:
#         with open(sg_file, 'w') as file:
#             file.write(', '.join([str(key) for key in list(potential_sg_indivs.keys())]))
#     except FileNotFoundError as fnfe:
#         print("Unable to write list of index of potential SG indivs")

# # Writes the population to the config files
# def write_population_to_files(population: List[TLLogicSet], 
#                               generation: int, 
#                               run_label: 'str'):
#     # Write the population to the config files
#     for id, indiv in enumerate(population):
#         indiv_prev_gen_file = f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation - 1}/grid_network_{id}_modified.net.xml"
#         indiv_next_gen_file = f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{id}_modified.net.xml"
#         # Try to open an exisiting file for the specific individual
#         try:
#             # If the file is present, read the contents, update them, and write the update back to the file
#             with open(indiv_prev_gen_file, 'r') as file:
#                 indiv_xml_string = file.read()
#                 file.close()
#             if indiv_xml_string:
#                 updated_xml_string = write_tl_logic(indiv_xml_string, indiv.tllogics)
#                 os.makedirs(os.path.dirname(indiv_next_gen_file), exist_ok=True)
#                 with open(indiv_next_gen_file, 'w') as file:
#                     file.write(beautify_xml(xml_str=updated_xml_string))
#                     file.flush()
#                     file.close()
#         # If an corresponding file for the given id of an individual is not present, try to open the original file
#         except FileNotFoundError as fnfe:
#             # Open the 
#             original_file = f"{NETWORK_CONFIGS_DIR}/originals/grid_network_original.net.xml"
#             with open(original_file, 'r') as file:
#                 original_xml_string = file.read()
#                 file.close()
#             if original_xml_string:
#                 updated_xml_string = write_tl_logic(original_xml_string, indiv.tllogics)
#                 os.makedirs(os.path.dirname(indiv_next_gen_file), exist_ok=True)
#                 with open(indiv_next_gen_file, 'w') as file:
#                     file.write(beautify_xml(xml_str=updated_xml_string))
#                     file.flush()
#                     file.close()

# # Writes the best individual found by evolution to a marked file so it can easily be used or recovered
# def write_best_indiv_to_file(index: int, 
#                              generation: int, 
#                              run_label: str, 
#                              best_indiv: TLLogicSet):
#     with open(f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{index}_modified.net.xml", 'r') as file:
#         best_indiv_xml_string = file.read()
#         file.close()
#     if best_indiv_xml_string:
#         updated_xml_string = write_tl_logic(best_indiv_xml_string, best_indiv.tllogics)
#         path = f"{NETWORK_CONFIGS_DIR}/{run_label}/{BEST_INDIVIDUALS_DIR}/grid_network_best_indiv_{run_label}_{datetime.datetime.now()}.net.xml"
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         with open(path, 'w') as file:
#             file.write(beautify_xml(xml_str=updated_xml_string))
#             file.flush()
#             file.close()

# # Method used to initialize the population
# def initialize_population(population_size: 'int', 
#                           generation: int, 
#                           run_label: 'str', 
#                           template_tllogics: 'TLLogicSet') -> List[TLLogicSet]:
#     population = []
#     for _ in range(population_size):
#         tllogic_set = get_deepcopy_of_tllogic_set(template_tllogics)
#         population.append(tllogic_set)

#     # Write the population to the config files
#     write_population_to_files(population=population, run_label=run_label, generation=generation)
#     return population

# # Method used to initialize the population from existing network files
# def initialize_population_from_exiting(population_size: 'int', 
#                                        generation: int, 
#                                        run_label: str, 
#                                        template_tllogics: 'TLLogicSet') -> List[TLLogicSet]:
#     population = []
#     # Read in the original network file with decent traffic light phases
#     for i in range(population_size):
#         try:
#             with open(f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{i}_modified.net.xml", 'r') as file:
#                 xml_string = file.read()
#                 file.close()

#             # Create an original logic set from which futher sets will be born
#             if xml_string:
#                 population.append(TLLogicSet(tllogics=parse_tl_logic(xml_string)))
#         except FileNotFoundError as fnfe:
#             tllogic_set = get_deepcopy_of_tllogic_set(template_tllogics)
#             population.append(tllogic_set)

#     return population

# # Only take the top % of individuals
# def max_fitness_selection(population: List[TLLogicSet]) -> List[TLLogicSet]:
#     population.sort(key=lambda x: x.fitness)
#     return [deepcopy(indiv) for indiv in population[:POPULATION_SIZE // 10]]

# def tournament_selection(population: List['TLLogicSet'], 
#                          tournament_size: 'int') -> List['TLLogicSet']:
#     selected_individuals = []
#     for _ in range(len(population)):
#         tournament = random.sample(population, tournament_size)
#         best_individual = min(tournament, key=lambda x: x.fitness)
#         selected_individuals.append(deepcopy(best_individual))
#     return selected_individuals

# def run_simulation(index: 'int', 
#                    generation: int, 
#                    run_label: str, 
#                    return_dict: dict):
#     # Start SUMO simulation for the stairstep route
#     libsumo.start(SUMO_CMD_STAIRSTEP + ["-n", f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{index}_modified.net.xml"], label=f"{index}")
#     # Counter for the number of steps a simulation takes
#     steps_stairstep = 0
#     # Run the first simulation
#     while libsumo.simulation.getMinExpectedNumber() > 0:
#         libsumo.simulationStep()
#         steps_stairstep += 1
#     # Close SUMO simulation
#     libsumo.close()
#     # Select a random route from the list of random routes
#     random_route_index = 4
#     steps_random = 0
#     # Start SUMO simulation for a random route
#     libsumo.start(SUMO_CMD_RANDOM + ["-r", f"{ROUTE_CONFIGS_DIR}/grid_network_0_routes_random_{random_route_index}.rou.xml", "-n", f"{NETWORK_CONFIGS_DIR}/{run_label}/generation_{generation}/grid_network_{index}_modified.net.xml"], label=f"{index}")
#     while libsumo.simulation.getMinExpectedNumber() > 0:
#         libsumo.simulationStep()
#         steps_random += 1
#     # Close SUMO simulation
#     libsumo.close()
#     # Calculate fitness based on how many steps the simulation took
#     return ((steps_stairstep / (STEPS_OG_STAIRSTEP)) * STAIRSTEP_FITNESS_SCALAR) + ((steps_random / STEPS_OG_RANDOM_LIST[random_route_index]) * RANDOM_FITNESS_SCALAR)

# def process_task(index: int, generation: int, run_label: str, return_dict: dict):
#     return_dict[index] = run_simulation(index=index, generation=generation, run_label=run_label, return_dict=return_dict)

# def evaluate_population(population: List[TLLogicSet], 
#                         generation: int, 
#                         run_label: str):
#     manager = Manager()
#     return_dict = manager.dict()

#     # Use ProcessPoolExecutor to manage a pool of worker processes
#     with ProcessPoolExecutor(max_workers=24) as executor:
#         # Submit tasks for each individual in the population
#         futures = [executor.submit(process_task, index, generation, run_label, return_dict) for index, _ in enumerate(population)]
        
#         # Wait for all tasks to complete (optional here since exiting the 'with' block will wait automatically)
#         for future in futures:
#             future.result()  # Accessing the result will also re-raise any exceptions caught during execution

#     # Update the fitness values in the population based on the results stored in return_dict
#     for (key, value) in return_dict.items():
#         population[key].fitness = value

# # Identify potentially specification gamed individuals
# def identify_specification_gaming_individuals(population: List[TLLogicSet]) -> dict[int, TLLogicSet]:
#     indiv_to_consider = [individual for individual in population if individual.fitness <= (STAIRSTEP_FITNESS_SCALAR + RANDOM_FITNESS_SCALAR)]
#     fitness_values = [individual.fitness for individual in indiv_to_consider]
#     mean_fitness = np.mean(fitness_values)
#     std_dev_fitness = np.std(fitness_values)
    
#     potential_gaming_individuals = {
#         population.index(individual): individual for individual in population if individual.fitness <= (mean_fitness - std_dev_fitness)
#     }
    
#     return potential_gaming_individuals

# # Attempt to mitigate specification gaming indivs by replacing them with clones
# def replace_indiv_with_clone(population: List[TLLogicSet], index_to_replace: int, invalid_indices: List[int]):
#     valid_indices = [i for i in range(len(population)) if i not in invalid_indices and i != index_to_replace]
#     population[index_to_replace] = deepcopy(population[random.choice(valid_indices)])

# # Attempt to mitigate specification gaming indivis by penalizing their fitness
# def penalize_indiv_fitness(population: List[TLLogicSet], index_to_penalize: int, penalty: int):
#     population[index_to_penalize].fitness += penalty

# # Attempt to mitigate specification gaming indivs by modifying the fitness function
# def modify_fitness_function():
#     RANDOM_FITNESS_SCALAR = STAIRSTEP_FITNESS_SCALAR

# # Take actions against SG individuals
# def mitigate_sg_individuals(population: List[TLLogicSet], generation: int, run_label: str, strategy: str):
#     # Identify the individuals to mitigate
#     individuals_to_mitigate = identify_specification_gaming_individuals(population=population)
#     # Make a record of them
#     write_potential_sg_indivs_to_file(potential_sg_indivs=individuals_to_mitigate, generation=generation, run_label=run_label)
#     if not strategy or strategy == STRAT_REPLACE:
#         # For each one, replce it with a clone of an indiv not identified as SG
#         for index, _ in individuals_to_mitigate.items():
#             replace_indiv_with_clone(population=population, index_to_replace=index, invalid_indices=list(individuals_to_mitigate.keys()))
#     if strategy == STRAT_PENALIZE:
#         for index, _ in individuals_to_mitigate.items():
#             penalize_indiv_fitness(population=population, index_to_penalize=index, penalty=(population[index].fitness * 0.5))
#     if strategy == STRAT_MOD_FITNESS:
#         modify_fitness_function()
#     # Write the mitigated population back to the files
#     write_population_to_files(population=population, generation=generation, run_label=run_label)

# # Main body function for the overall evolutionary algorithm
# def evolutionary_algorithm(population_size: int = POPULATION_SIZE, 
#                            num_generations: int = NUM_GENERATIONS, 
#                            initialize_from_existing: tuple[bool, int] = (False, 0),
#                            run_label: str = (f"Run_" + datetime.datetime.now().strftime("%Y_%m_%d_%HH%MM%SS"))):
#     # Initialize population
#     population = []
#     template = read_in_tllogic_set_from_file(filename=f"{NETWORK_CONFIGS_DIR}/{ORIGINALS_DIR}/{TLLOGIC_SEED_INDIV_CONFIG}")
#     if initialize_from_existing[0]:
#         population = initialize_population_from_exiting(population_size=population_size, generation=initialize_from_existing[1] - 1, run_label=run_label, template_tllogics=template)
#     else:
#         if not template:
#             print("Unable to read in template file, exiting")
#             return
#         population = initialize_population(population_size, generation=0, run_label=run_label, template_tllogics=template)
#     if len(population) <= 0:
#         print(f"Error initializing population, unable to meaningfully fun EC")
#         return
#     if initialize_from_existing[0]:
#         # Evaluate fitness of each individual
#         evaluate_population(population=population, generation=initialize_from_existing[1] - 1, run_label=run_label)
#         # Mitigate any specification gamed individuals
#         if initialize_from_existing[1] % 10 == 0:
#             mitigate_sg_individuals(population=population, generation=initialize_from_existing[1] - 1, run_label=run_label, strategy=STRAT_REPLACE)
#     else:
#         evaluate_population(population=population, generation=0, run_label=run_label)
#     # Print some population stats
#     print(f"Generation {initialize_from_existing[1]}")
#     print(f"Best fitness: {min([inidiv.fitness for inidiv in population])}")
#     print(f"Average fitness: {mean([inidiv.fitness for inidiv in population])}")
#     print(f"Standard Deviation fitness: {stdev([inidiv.fitness for inidiv in population])}")

#     for generation in range(initialize_from_existing[1], num_generations):
#         # Maximize selective pressure
#         # Create new population; ensure survival of top n individuals
#         new_population = max_fitness_selection(population)
#         # Tournament selection
#         selected_individuals = tournament_selection(population, TOURNAMENT_SIZE)
#         # Fill the population in with some recombined and mutated individuals 
#         while len(new_population) < population_size:
#             parent1, parent2 = random.sample(selected_individuals, 2)
#             child1, child2 = parent1.recombine(parent2)
#             child1.mutate(MUTATION_RATE)
#             child2.mutate(MUTATION_RATE)
#             new_population.extend([child1, child2])

#         # Deepcopy for safety
#         population = [deepcopy(indiv) for indiv in new_population[:population_size]]
#         # Write the population to the config files
#         write_population_to_files(population=population, run_label=run_label, generation=generation)
#         # Evaluate the population
#         evaluate_population(population=population, generation=generation, run_label=run_label)
#         # Mitigate any specification gamed individuals
#         if (generation + 1) % 10 == 0:
#             mitigate_sg_individuals(population=population, generation=generation, run_label=run_label, strategy=STRAT_REPLACE)
#         # Print some population stats
#         print(f"Generation {generation + 1}")
#         print(f"Best fitness: {np.min([inidiv.fitness for inidiv in population])}")
#         print(f"Average fitness: {np.mean([inidiv.fitness for inidiv in population])}")
#         print(f"Standard Deviation fitness: {np.std([inidiv.fitness for inidiv in population])}")
#         # Identify specification gaming individuals
#         print(f"Potentially specification gaming individuals: {list(identify_specification_gaming_individuals(population=population).keys())}")

#     # Find the best individual
#     best_individual = min(population, key=lambda x: x.fitness)
#     # Write the best individual to a config files
#     write_best_indiv_to_file(index=population.index(best_individual), generation=num_generations - 1, run_label=run_label, best_indiv=best_individual)
        
#     return best_individual

# # Overwrite the main function cause that seems to be the thing to do in python
# if __name__ == "__main__":
#     print(str(evolutionary_algorithm(population_size=250, num_generations=50, initialize_from_existing=(True, 10), run_label="Golden_Run_Attempt_6_Gen_10_Replace_SG_Indivs")))

traci.start(SUMO_GUI_CMD_RANDOM + ["-n", f"{NETWORK_CONFIGS_DIR}/{ORIGINALS_DIR}/grid_network_original.net.xml"])
# pick an arbitrary junction
# junctionID = traci.junction.getIDList()[0]
# # subscribe around that junction with a sufficiently large
# # radius to retrieve the speeds of all vehicles in every step
# traci.junction.subscribeContext(
#     junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 1000000,
#     [tc.VAR_SPEED, tc.VAR_ALLOWED_SPEED]
# )
# Get the step length
# stepLength = traci.simulation.getDeltaT()
sim_start_time = time()
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    # scResults = traci.junction.getContextSubscriptionResults(junctionID)
    # halting = 0
    # if scResults:
    #     relSpeeds = [d[tc.VAR_SPEED] / d[tc.VAR_ALLOWED_SPEED] for d in scResults.values()]
    #     # compute values corresponding to summary-output
    #     running = len(relSpeeds)
    #     halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1])
    #     meanSpeedRelative = sum(relSpeeds) / running
    #     timeLoss = (1 - meanSpeedRelative) * running * stepLength
print(traci.simulation.getTime())
print(f"Time taken by simulation: {time() - sim_start_time}")
traci.close()