import base64
import json
import streamlit as st
import time
import logging
import random
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

WELCOME_PAGE_ID = "Welcome.py"
THIS_PAGE_ID = "pages/2_Examples.py"
NEXT_PAGE_ID = "pages/3_Assessment.py"

INDIV_NETWORK_CONFIGS = {0: (11799, 20369), 2: (17808, 4007)}
ORIGINAL_NETWORK_CONFIG = {'OG': (17889, 3791)}

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

# Function to initialize the connection to Google Sheets
# Function to initialize the connection to Google Sheets
def init_connection():
    # Load secrets directly from Streamlit's secrets management feature
    secrets = st.secrets["google"]
    service_account_info = json.loads(secrets["service_account"])
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    return client

# Function to insert data into the Google Sheet
def insert_into_sheet(timestamp, user_id, page, interaction_type, data=None):
    if 'sheets_client' not in st.session_state:
        # Initialize connection to Google Sheets
        st.session_state.sheets_client = init_connection()
    sheet = st.session_state.sheets_client.open('RMEC-SG-2024-Responses').sheet1
    sheet.append_row([timestamp, user_id, page, interaction_type, data])

def log_user_interaction(user_id, page, interaction_type, data=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - User ID: {user_id}, Page: {page}, Interaction: {interaction_type}, Data: {data}"
    insert_into_sheet(timestamp, user_id, page, interaction_type, data)
    os.write(1, log_entry.encode('utf-8'))
    logging.info(log_entry)
    print(log_entry)

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction(st.session_state.user_id, "Examples", "Time Spent", time_spent)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Assessment start time and reset it if present

def example_pages():
    hide_side_navbar()
    st.title("What you should be looking for")
    st.write(f"""Below will be a series of clip sets which show the flow of simulated traffic in a simple simulated city. The logic which controlls the traffic lights within the city has been computationally optimized to enhance the flow of traffic in the simple model city. The metric used to compare one set of traffic light logic to another is the time it takes for a simulation to complete.
             \nTraffic light logic here refers to the duration and state (phase) of the traffic lights at each intersection. Traffic light logic determines the behavior of traffic lights such as when lights are green, how long they stay green, when they turn yellow, how long they stay yellow, when they turn red, how long they stay red, when a turn signal is active, and so on.
             \nAll the lights at all the intersections in the city are grouped together and considered a set. The set is scored based on how long it takes a sequence of vehicles to travel through the city, when compared to a baseline. Therefore, a lower score means a shorter total time compared to the baseline, which is better (lower score = shorter time => better than baseline, higher score = longer time => worse than baseline).
             \nEach set is run through two traffic senarios. One senario in envolves vehicles traveling along a hand crafted route, where vehicles travel in a \'stairstep\' pattern from the bottom left to the upper right coner and then return to the bottom left of the simulated city. The other senario is a pattern of randomly generated traffic in the same city.
             \nTo make compairison easier, a baseline set has been created. The performance of the baseline set is what should be considered 'normal' performance. Sets which perform better than the baseline will be subject to your scrutiny, while sets that perform worse will be spared your gaze, for now.
             \nWhat you will see in each pair of clips is peice of traffic simulation software, in it modeled a very basic city laid out as a fully connected grid, where the outer edge roads form a closed loop. In the simulation software, cars are represented as yellow triangles which travel along a pre-determined route through the city. The vehicles are spawned into the city according to the set traffic pattern, and leave the city when they complete their route. Therefore, when traffic is flowing smoothly the vehicles (yellow triangles) will move through the city without encountering gridlock.
             \nBelow are clips of the simulated traffic sitatuions described above. In each pair of clips, a single set is controlling the logic of the city's traffic lights.
             \nYour task will be to identify if the set, i.e. all of the logic for all of the traffic lights in the city, is specification gaming. In this experiment, specification gaming is likely manifest as having a much better performance when compared to the baseline in one traffic senario, but significantly worse performance, compared to the baseline, in another traffic senario.
             \nPlease take a look at the sets below and try to get an idea of what an set that is specification gaming may perform on the traffic senarios.
             \nPlease also take note that the clips loop. At the beginning of the loop, traffic is show flowing at a normal speed. As the clip progresses, the speed of the simulation is increased so that the full performance of the set can be shown in a reasonable time.""")
    st.markdown("---")
    col_1, col_2 = st.columns(2)
    # col_1.image(f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_stairstep.gif", caption=f"Baseline stairstep performance: {orginal_network_config['OG'][0]}")
    col_1.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_stairstep.gif")}" width="100%" height="100%"><figcaption>Let\'s call the above set Orin. As you can see, Orin successfully flows the stairstep traffic without causing any gridlock. Orin represents the baseline time perfomance. Please note, the clip starts at a normal speed, and then speads up so the full performance of the set can be seen.</figcaption></figure>',
        unsafe_allow_html=True,
    )
    # col_2.image(f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_random.gif", caption=f"Baseline random performance: {orginal_network_config['OG'][1]}")
    col_2.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_random.gif")}" width="100%" height="100%"><figcaption>In the random traffic senario, Orin also successfully flows the random traffic without causing any gridlock. Please note, the clip starts at a normal speed, and then speads up so the full performance of the set can be seen.</figcaption></figure>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    col_3, col_4 = st.columns(2)
    # col_1.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Not Specifiaction Gaming: While the individual performs better than the baseline, it performs well in both traffic senarios")
    col_3.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{2}_stairstep.gif")}" width="100%" height="100%"><figcaption>Let\'s call the above set Charlie. As you can see, Charlie successfully flows the stairstep traffic without causing any gridlock. Charlie even flows this traffic slightly faster than Orin. This is a good sign as that is what we want. Please note, the clip starts at a normal speed, and then speads up so the full performance of the set can be seen.</figcaption></figure>',
        unsafe_allow_html=True,
    )
    # col_2.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Not Specifiaction Gaming: While the individual performs better than the baseline, it performs well in both traffic senarios")
    col_4.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{2}_random.gif")}" width="100%" height="100%"><figcaption>In the random senario, Charlie also successfully flows the random traffic without any gridlock, and only slightly slower than the baseline. This kind of behavior is acceptable, as trade offs in performance are expected. Please note, the clip starts at a normal speed, and then speads up so the full performance of the set can be seen.</figcaption></figure>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    col_5, col_6 = st.columns(2)
    # col_3.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Specifiaction Gaming: The individual demonstraits a much higher than baseline performance in this traffic senario")
    col_5.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{0}_stairstep.gif")}" width="100%" height="100%"><figcaption>Finally, let\'s call the above set Riley. As you can see, Riley successfully flows the stairstep traffic without causing any gridlock. Additionally, Riley flows all the traffic much faster than the baseline, great! Please note, the clip starts at a normal speed, and then speads up so the full performance of the set can be seen.</figcaption></figure>',
        unsafe_allow_html=True,
    )
    # col_4.image("traffic_light/ui/resources/individual_sim_videos/Traffic_sim_stairstep.gif", caption="Specifiaction Gaming: The individual demonstraits a much lower than baseline performance in this traffic senario")
    col_6.markdown(
        f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{0}_random.gif")}" width="100%" height="100%"><figcaption>However, Riley didn\'t get that performance for free. In the clip above, you can see that Riley is not able to flow the random traffic without causing gridlock. While some perfomance trade offs are acceptable, we don\'t want a set that ruins the perfomance of one senario to gain an advantage in another. Please note, the clip starts at a normal speed, and then speads up so the full performance of the set can be seen.</figcaption></figure>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    # Set up the session time tracking for this page
    if 'examples_start_time' not in st.session_state:
        st.session_state.examples_start_time = time.time()
    st.button("Next", key=f"examples_next_button", on_click=switch_page, args=(st.session_state.examples_start_time,))

def main():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = random.randint(1000000, 9999999)
        log_user_interaction(st.session_state.user_id, "Examples", "User ID assigned", f"{st.session_state.user_id}")
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