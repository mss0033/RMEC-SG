import json
import streamlit as st
import time
import logging
import random
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

WELCOME_PAGE_ID = "Welcome.py"
THIS_PAGE_ID = "pages/1_Tutorial.py"
NEXT_PAGE_ID = "pages/2_Examples.py"

# Set up logging
logging.basicConfig(filename='user_interactions.log', level=logging.INFO) 

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

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction(st.session_state.user_id, "Tutorial", "Time Spent", time_spent)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Examples start time and reset it if present

def tutorial_pages():
    hide_side_navbar()
    st.title("Tutorial")
    st.write(f"""This project aims to tackle a problem commonly found in optimization functions, such as those used in Machine Learning, Artificial Intelligence, and Evolutionary Computing.
             \n This problem has a few names, but for our purposes, it will hereby be referred to as Specification Gaming.
             \nSpecification Gaming, for this project, is defined as a situation where an optimization system, such as a Neural Network or Evolutionary Algorithm, produces a result that performs well according to some objective (i.e,\"maximize fitness\"\solution quality) by doing something unexpected or undesired.
             \nBelow are some visual examples of specification gaming.""")
    
    st.markdown("---")
    col_1, col_2, col_3 = st.columns(3)
    col_1.image("traffic_light/ui/resources/SG_example_images/block_flip.gif", caption=f"A robot trained to stack blocks was scored based on whether the bottom of one block was at the same height as the top of the other block. The robot learned to simply flip over a block.")
    col_2.image("traffic_light/ui/resources/SG_example_images/boat_race.gif", caption=f"A boat race game-playing agent was scored based on the score of the game. The agent learned it could achieve a higher score by simply collecting the power-ups repeatedly.")
    col_3.image("traffic_light/ui/resources/SG_example_images/slide_to_the_right.gif", caption=f"An evolved creature \'discovered\' an exploit in the physics engine that allowed it to simply glide to the side, instead of running.")
    st.image("traffic_light/ui/resources/SG_example_images/quilt_of_sg.gif", caption=f"A collection of similar instances across a wide range of optimization systems.")

    st.markdown("---")
    st.write(f"""From the above examples, a common theme emerges. All of the products of optimization found unexpected and undesirable methods of technically satisfying their optimization function while not having the desired emergent properties or behaviors.
             \nWhile some of these examples may be amusing, unfortunately, not all examples are so funny. In more serious situations agents trained to drive cars or control planes may adopt niche behavior that scores well according to some optimization process but would put people at dire risk.
             \nTo go further, when these issues occur typically they are discovered at the end of long and expensive optimization processes such as evolutionary runs or neural network training. Therefore, specification gaming can also represent a significant and expensive time loss when it occurs. 
             \nSo, to address this issue, this project seeks to investigate whether human-in-the-loop interactions can help identify and mitigate this Specification Gaming problem.""")
    # Set up the session time tracking for this page
    if 'tutorial_start_time' not in st.session_state:
        st.session_state.tutorial_start_time = time.time()
    
    st.markdown("---")
    st.button("Next", key=f"tutorial_next_button", on_click=switch_page, args=(st.session_state.tutorial_start_time,))

def main():
    if 'tutorial_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
        st.session_state.tutorial_navbar_hidden = True
    if 'user_id' not in st.session_state:
        st.session_state.user_id = random.randint(1000000, 9999999)
        log_user_interaction(st.session_state.user_id, "Tutorial", "User ID assigned", f"{st.session_state.user_id}")
    if 'next_page' not in st.session_state:
        st.session_state.next_page = WELCOME_PAGE_ID
    # If the session current page is this page, display it
    if st.session_state.next_page == THIS_PAGE_ID:
        tutorial_pages()
    else:
        st.switch_page(st.session_state.next_page)

if __name__ == "__main__":
    main()