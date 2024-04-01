import json
import streamlit as st
import time
import logging
import random
import pyperclip
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

WELCOME_PAGE_ID = "Welcome.py"
THIS_PAGE_ID = "pages/4_Thank_You.py"
NEXT_PAGE_ID = WELCOME_PAGE_ID

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
    log_user_interaction(st.session_state.user_id, "Thank You", "Time Spent", time_spent)
    st.session_state.next_page = WELCOME_PAGE_ID
    # If they go back around, reset the welcome start time
    st.session_state.welcome_start_time = time.time()

def thank_you_page():
    # Make sure the side navbar is hidden
    hide_side_navbar()
    # Set up the page title and content
    st.title("The End")
    st.write("Thank you for your participation! Please provide the code below to get credit for completing the study.")
    st.write(f"Completion code: {st.session_state.user_id}")
    # Add a button to copy the text to the clipboard
    copy_button = st.button('Copy to Clipboard', on_click=pyperclip.copy(st.session_state.user_id))

    # Set up the session time tracking for this page
    if 'thank_you_start_time' not in st.session_state:
        st.session_state.thank_you_start_time = time.time()
    # st.button("Restart", key=f"thank_you_restart_button", on_click=switch_page, args=(st.session_state.thank_you_start_time,))

def main():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = random.randint(1000000, 9999999)
        log_user_interaction(st.session_state.user_id, "Thank you", "User ID assigned", f"{st.session_state.user_id}")
    if 'thanks_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed", layout="wide")
        st.session_state.thanks_navbar_hidden = True
    # If the current page is not stored in the session state, set it to the welcome page
    if 'next_page' not in st.session_state:
        st.session_state.next_page = WELCOME_PAGE_ID
    # If the session current page is this page, display it
    if st.session_state.next_page == THIS_PAGE_ID:
        thank_you_page()
    else:
        st.switch_page(st.session_state.next_page)

if __name__ == "__main__":
    main()