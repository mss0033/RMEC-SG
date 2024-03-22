import streamlit as st
import os
import json
from traffic_light_ec import evolutionary_algorithm, read_in_tllogic_set_from_file, TLLogicSet, parse_tl_logic

# Directory to store snapshots
SNAPSHOTS_DIR = "snapshots"

def main():
    st.title("Evolutionary Algorithm for Traffic Light Optimization")

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