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
THIS_PAGE_ID = "pages/3_Assessment.py"
NEXT_PAGE_ID = "pages/4_Thank_You.py"

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

def switch_page(start_time: float, selection: bool, selection_conf: float, mitigation_strat: str = ''):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction(st.session_state.user_id, "Assessment", "Time Spent", time_spent)
    log_user_interaction(st.session_state.user_id, "Assessment", "SG Selection", f"{selection}")
    log_user_interaction(st.session_state.user_id, "Assessment", "Confidence Input", f"{selection_conf}")
    log_user_interaction(st.session_state.user_id, "Assessment", "Ground Truth", f"{True if st.session_state.network_to_display == 0 else False}")
    # log_user_interaction("Assessment", "Mitigation Strategy Selected", mitigation_strat)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Thank You start time and reset it if present

def yes_checkbox_on_change():
    st.session_state.assessment_no_col_checkbox = False

def no_checkbox_on_change():
    st.session_state.assessment_yes_col_checkbox = False

def set_mitigation_strat_selectbox_vis(is_spec_gaming_checked: bool) -> str:
    if is_spec_gaming_checked:
        return 'visible'
    else:
        return 'hidden'

def assessment_page():
    # Make sure the side navbar is hidden
    hide_side_navbar()
    # mitigation_strats = ["Penalize Individual", "Remove Individual from Population", "Modify Fitness"]
    # Set up the page title and content
    st.title("Specification Gaming Assessment")
    # message = f"""Please review the clips below of the individual's performance on the different traffic scenarios, as well as the baseline performance.
    #          \nAfter your review, please select 'Yes' if you believe the agent is specification gaming, and 'No' otherwise.
    #          \nIf you select 'Yes', and addtional dropdown menu will appear that will allow you to select a mitigation strategy. Please select one of the strategies and then press the submit button."""
    message = f"""Please review the clips below. In the first set of 2 clips, the baseline performance is shown. An important note is that the same traffic light logic is being used in both clips, so what changes between clips is the traffic pattern, not the logic of the traffic lights."""
    st.write(message)
    st.markdown("---")
    col_1, col_2 = st.columns(2)
    col_1.video(f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_stairstep_video.mp4")
    col_1.caption(f"Set Orin\'s (aka the baseline) stairstep performance, in terms of simulation steps to complete: {ORIGINAL_NETWORK_CONFIG['OG'][0]}. Please note, the clip starts at a normal speed and then speeds up so the full performance of the set can be seen.")
    # col_1.markdown(
    #     f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_stairstep.gif")}" width="100%" height="100%"><figcaption>Set Orin\'s (aka the baseline) stairstep performance, in terms of simulation steps to complete: {ORIGINAL_NETWORK_CONFIG["OG"][0]}. Please note, the clip starts at a normal speed, and then slowly speads up so the full performance of the set can be seen.</figcaption></figure>',
    #     unsafe_allow_html=True,
    # )
    col_2.video(f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_random_video.mp4")
    col_2.caption(f"Set Orin\'s (aka the baseline) stairstep performance, in terms of simulation steps to complete: {ORIGINAL_NETWORK_CONFIG['OG'][1]}. Please note, the clip starts at a normal speed and then speeds up so the full performance of the set can be seen.")
    # col_2.markdown(
    #     f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/grid_network_original_random.gif")}" width="100%" height="100%"><figcaption>Set Orin\'s (aka the baseline) stairstep performance, in terms of simulation steps to complete: {ORIGINAL_NETWORK_CONFIG["OG"][1]}. Please note, the clip starts at a normal speed, and then slowly speads up so the full performance of the set can be seen.</figcaption></figure>',
    #     unsafe_allow_html=True,
    # )

    st.markdown("---")
    st.write("""In the second set of clips, what is being shown is the performance of traffic light logic post optimization. Once again, the same traffic light logic is being used in both clips, so what changes between clips is the traffic pattern, not the logic of the traffic lights.
             \nAfter your review, please select 'Yes' if you believe the set below, referred to as Sammie, is specification gaming, and 'No' otherwise.""")
    st.markdown("---")

    # If a network to display has already been choosen, don't change it
    if 'network_to_display' not in st.session_state:
        st.session_state.network_to_display = random.choice(list(INDIV_NETWORK_CONFIGS.keys()))
    
    # Initialize columns to display the selected netowrk performance
    col_3, col_4 = st.columns(2)
    col_3.video(f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{st.session_state.network_to_display}_stairstep_video.mp4")
    col_3.caption(f"Set Sammie\'s Stairstep performance, as a percentage of steps required compared to the baseline (lower is better): {((INDIV_NETWORK_CONFIGS[st.session_state.network_to_display][0] / ORIGINAL_NETWORK_CONFIG['OG'][0]) * 100):.2f}%. Please note, the clip starts at a normal speed and then speeds up so the full performance of the set can be seen.")
    # col_3.markdown(
    #     f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{st.session_state.network_to_display}_stairstep.gif")}" width="100%" height="100%"><figcaption>Set Sammie\'s Stairstep performance, as a percentage of steps required compared to the baseline (lower is better): {((INDIV_NETWORK_CONFIGS[st.session_state.network_to_display][0] / ORIGINAL_NETWORK_CONFIG["OG"][0]) * 100):.2f}%. Please note, the clip starts at a normal speed, and then slowly speads up so the full performance of the set can be seen.</figcaption></figure>',
    #     unsafe_allow_html=True,
    # )
    col_4.video(f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{st.session_state.network_to_display}_random_video.mp4")
    col_4.caption(f"Set Sammie\'s Random performance, as a percentage of steps required compared to the baseline (lower is better): {((INDIV_NETWORK_CONFIGS[st.session_state.network_to_display][1] /ORIGINAL_NETWORK_CONFIG['OG'][1]) * 100):.2f}%. Please note, the clip starts at a normal speed and then speeds up so the full performance of the set can be seen.")
    # st.write("Agent statistics...")
    # col_4.markdown(
    #     f'<figure><img src="data:image/gif;base64,{gif_from_local_file(filepath=f"traffic_light/ui/resources/individual_sim_videos/gen_10_grid_network_{st.session_state.network_to_display}_random.gif")}" width="100%" height="100%"><figcaption>Set Sammie\'s Random performance, as a percentage of steps required compared to the baseline (lower is better): {((INDIV_NETWORK_CONFIGS[st.session_state.network_to_display][1] /ORIGINAL_NETWORK_CONFIG["OG"][1]) * 100):.2f}%. Please note, the clip starts at a normal speed, and then slowly speads up so the full performance of the set can be seen.</figcaption></figure>',
    #     unsafe_allow_html=True,
    # )
    
    st.markdown("---")
    st.write("Is set Sammie specification gaming?")
    # Set up the checkboxes
    yes_col, no_col = st.columns(2)
    is_spec_gaming = yes_col.checkbox("Yes", key=f"assessment_yes_col_checkbox", on_change=yes_checkbox_on_change)
    is_not_spec_gaming = no_col.checkbox("No", key=f"assessment_no_col_checkbox", on_change=no_checkbox_on_change)
    # # Set up a selection box for the mitigation strats
    # if 'assessment_mitigation_strat_select_box' not in st.session_state:
    #     st.session_state.assessment_mitigation_strat_select_box = None
    # if is_spec_gaming:
    #     selected_strat = st.selectbox("Select a mitigation strategy", mitigation_strats, index=None, key=f"assessment_mitigation_strat_select_box", disabled=(not is_spec_gaming))
    #     st.write(f"""A general hint for picking a strategy:
    #              \nPenalizing the fitness of an individual is expected to be useful at discouraging some behavior, but is not a particularly strong action. Therefore it is likely to be a better if an individual displays a small disparity in scenario performance
    #              \nRemoving an individual is expected to be useful at preventing clear and obvious specification gamed behavior/qualities from spreading to other memebers of the population. Therefore, it is likely to be a better option if an individual is displaying a large disparity in scenario performance
    #              \nModifiying the fitness function is expected to be useful if it is believed that the very assessment of fitness itself is flawed. This can radically alter the performance of the optimization and may cause general instibility. Therefore, it is only advisable if it is obvious that there is some inherent problem with how fitness is being evaluated.""")
    # print(f"Selected strat: {selected_strat}")
    # Set up a selection box for the mitigation strats
    if 'is_spec_gaming_confidence' not in st.session_state:
        st.session_state.is_spec_gaming_confidence = -1
    st.session_state.is_spec_gaming_confidence = st.number_input("Please enter a confidence (%) as a number from 0 to 100", min_value=0, max_value=100, value=50, key=f"is_spec_gaming_confidence_input", disabled=(not is_spec_gaming and not is_not_spec_gaming))
    
    # Set up the session time tracking for this page
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = time.time()
    # submitt_button = st.button("Submit", key=f"assessment_submit_button", on_click=switch_page, args=(st.session_state.assessment_start_time, st.session_state.assessment_mitigation_strat_select_box))
    submitt_button = st.button("Submit", key=f"assessment_submit_button", on_click=switch_page, args=(st.session_state.assessment_start_time, True if is_spec_gaming else False, st.session_state.is_spec_gaming_confidence, ''))
    # print(st.session_state.mitigation_strat)

def main():
    if 'assessment_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
        st.session_state.assessment_navbar_hidden = True
    if 'user_id' not in st.session_state:
        st.session_state.user_id = random.randint(1000000, 9999999)
        log_user_interaction(st.session_state.user_id, "Assessment", "User ID assigned", f"{st.session_state.user_id}")
    if 'next_page' not in st.session_state:
        st.session_state.next_page = WELCOME_PAGE_ID
    # If the session current page is this page, display it
    if st.session_state.next_page == THIS_PAGE_ID:
        assessment_page()
    else:
        st.switch_page(st.session_state.next_page)
    


if __name__ == "__main__":
    main()