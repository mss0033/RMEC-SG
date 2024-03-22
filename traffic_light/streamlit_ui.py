import streamlit as st
import os
import json
from traffic_light_ec import evolutionary_algorithm, read_in_tllogic_set_from_file, TLLogicSet, parse_tl_logic

# Directory to store snapshots
SNAPSHOTS_DIR = "snapshots"

def load_snapshot(generation):
    snapshot_file = os.path.join(SNAPSHOTS_DIR, f"snapshot_{generation}.json")
    with open(snapshot_file, "r") as file:
        snapshot = json.load(file)
    return snapshot

def save_snapshot(generation, population, flagged_individuals):
    snapshot = {
        "generation": generation,
        "population": [indiv.__dict__ for indiv in population],
        "flagged_individuals": flagged_individuals
    }
    snapshot_file = os.path.join(SNAPSHOTS_DIR, f"snapshot_{generation}.json")
    with open(snapshot_file, "w") as file:
        json.dump(snapshot, file)

def main():
    st.title("Evolutionary Algorithm for Traffic Light Optimization")

    # Sidebar for selecting the starting generation
    st.sidebar.title("Evolutionary Algorithm Controls")
    start_generation = st.sidebar.number_input("Select Starting Generation", min_value=0, value=0, step=1)
    resume_button = st.sidebar.button("Resume from Selected Generation")

    if resume_button:
        snapshot = load_snapshot(start_generation)
        population = [TLLogicSet(tllogics=parse_tl_logic(json.dumps(indiv))) for indiv in snapshot["population"]]
        flagged_individuals = snapshot["flagged_individuals"]
        current_generation = snapshot["generation"]
    else:
        population = []
        flagged_individuals = {}
        current_generation = 0

    # Main content area
    st.header(f"Generation {current_generation}")

    # Display flagged individuals for specification gaming
    st.subheader("Flagged Individuals for Specification Gaming")
    for index, individual in flagged_individuals.items():
        st.write(f"Individual {index}")
        st.write(individual)
        is_spec_gaming = st.checkbox(f"Is Individual {index} Specification Gaming?")
        if is_spec_gaming:
            mitigation_option = st.selectbox(f"Mitigation Option for Individual {index}",
                                             options=["Remove", "Adjust Fitness", "Change Weighting"])
            if mitigation_option == "Remove":
                # Remove the individual from the population
                population.pop(index)
            elif mitigation_option == "Adjust Fitness":
                adjusted_fitness = st.number_input(f"Adjusted Fitness for Individual {index}", value=individual.fitness)
                individual.fitness = adjusted_fitness
            elif mitigation_option == "Change Weighting":
                new_weighting = st.number_input(f"New Weighting for Individual {index}", value=1.0)
                # Apply the new weighting to the fitness function
                # (Implement the logic based on your specific fitness function)

    # Button to start the evolutionary algorithm
    start_button = st.button("Start Evolutionary Algorithm")

    if start_button:
        # Call the evolutionary_algorithm method with the current population and generation
        best_individual = evolutionary_algorithm()

        st.header("Evolutionary Algorithm Completed")
        st.write("Best Individual:")
        st.write(best_individual)

if __name__ == "__main__":
    main()