import base64
import streamlit as st
import time
import logging
import os
import uuid

WELCOME_PAGE_ID = "Welcome.py"
THIS_PAGE_ID = "pages/2_Examples.py"
NEXT_PAGE_ID = "pages/3_Assessment.py"

# Set up logging
logging.basicConfig(filename='user_interactions.log', level=logging.INFO)

def gif_from_local_file(filepath: str):
    file = open(file=filepath, mode="rb")
    contents = file.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file.close()
    return data_url

def hide_side_navbar():
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {
                display: none
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def log_user_interaction(page, interaction_type, data=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Page: {page}, Interaction: {interaction_type}, Data: {data}"
    logging.info(log_entry)
    print(log_entry)

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction("Examples", "Time Spent", time_spent)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Assessment start time and reset it if present

def example_pages():
    indiv_network_configs = {0: (11799, 20369), 1: (15350, 10689), 2: (17808, 4007), 3:(12859, 21382), 4: (13197, 19226), 5: (13485, 18657), 6: (12967, 21235), 7: (12847, 20249), 30: (13571, 19907), 145: (13621, 22518)}
    hide_side_navbar()
    st.title("What you should be looking for")
    st.write(f"""Below will be a series of items that where evolved to optimize traffic flow in a city. The individual(s) being optimized then are the logic of the traffic lights. Traffic light logic here refer to the duration and state (phase) of the traffic lights at each intersection.
             \nTraffic light logic determines the behavior of traffic lights such as when lights are green, how long they stay green, when they turn yellow, how long they stay yellow, when they turn red, how long they stay red, when a turn signal is active, and so on.
             \nAll the lights at all the intersections in the city are grouped together and considered an individual. The individuals are scored based on how long it takes a sequence of vehicles to travel through the city. Here, a lower score means a shorter total time, which is better (lower score = shorter time => higher fitness, higher score = longer time => lower fitness).
             \nEach individual is run through two traffic senarios. One is a hand crafted route where vehicles travel in a \'stairstep\' pattern from the bottom left to the upper right coner and then return to the bottom left of the simulated city, the other is a pattern of randomly generated traffic.
             \nTo make compairison easier, a baseline individual has been created that has what should be considered 'normal' or 'nominal' performance. Individuals performing better should be subject to your scrutiny, while individuals that perform worse can be safely ignored as they would not be selected over the baseline for deployment.
             \nFirst you will be asked to identify if the individual, the traffic lights logic, is specification gaming. In this situation specification gaming is likely manifest as having a much higher performance when compared to the baseline in one situtation, but the same or even worse performance, compared to the baseline, in another situation.
             \nPlease take a look at the individuals below and try to get an idea of what an individual that is specification gaming may perform on the traffic senarios.
             \nLastly, please keep in mind that this experiment was specifically constructed in such a way that specification gaming would occur with a high degree of predictability and regularity.""")
    col_1, col_2 = st.columns(2)
    # col_1.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Not Specifiaction Gaming: While the individual performs better than the baseline, it performs well in both traffic senarios")
    col_1.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{2}_stairstep.gif")}" width="100%" height="100%"><figcaption>Not Specifiaction Gaming: While the individual performs better than the baseline, it performs well in both traffic senarios</figcaption></figure>',
        unsafe_allow_html=True,
    )
    # col_2.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Not Specifiaction Gaming: While the individual performs better than the baseline, it performs well in both traffic senarios")
    col_2.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{2}_random.gif")}" width="100%" height="100%"><figcaption>Not Specifiaction Gaming: While the individual performs better than the baseline, it performs well in both traffic senarios</figcaption></figure>',
        unsafe_allow_html=True,
    )
    col_3, col_4 = st.columns(2)
    # col_3.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Specifiaction Gaming: The individual demonstraits a much higher than baseline performance in this traffic senario")
    col_3.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{0}_stairstep.gif")}" width="100%" height="100%"><figcaption>Specifiaction Gaming: The individual demonstraits a much higher fitness (completes sim in shorter time) than baseline performance in this traffic senario, at the expense of performance in the random senario</figcaption></figure>',
        unsafe_allow_html=True,
    )
    # col_4.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Specifiaction Gaming: The individual demonstraits a much lower than baseline performance in this traffic senario")
    col_4.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{0}_random.gif")}" width="100%" height="100%"><figcaption>Specifiaction Gaming: The individual demonstraits a much lower fitness (completes sim in longer time) than baseline performance in this traffic senario in order to gain signficant performance in the stairstep senario</figcaption></figure>',
        unsafe_allow_html=True,
    )
    # Set up the session time tracking for this page
    if 'examples_start_time' not in st.session_state:
        st.session_state.examples_start_time = time.time()
    st.button("Next", key=f"examples_next_button", on_click=switch_page, args=(st.session_state.examples_start_time,))

def main():
    if 'examples_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
        st.session_state.examples_navbar_hidden = True
    if 'next_page' not in st.session_state:
        st.session_state.next_page = WELCOME_PAGE_ID
    # If the session current page is this page, display it
    if st.session_state.next_page == THIS_PAGE_ID:
        example_pages()
    else:
        st.switch_page(st.session_state.next_page)

if __name__ == "__main__":
    main()