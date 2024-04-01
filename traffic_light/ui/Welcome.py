import streamlit as st
import time
import logging
import random
import os
import uuid

WELCOME_PAGE_ID = "Welcome.py"
THIS_PAGE_ID = WELCOME_PAGE_ID
NEXT_PAGE_ID = "pages/1_Tutorial.py"

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

def log_user_interaction(user_id, page, interaction_type, data=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - User ID: {user_id}, Page: {page}, Interaction: {interaction_type}, Data: {data}"
    os.write(1, log_entry.encode('utf-8'))
    logging.info(log_entry)
    print(log_entry)

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction(st.session_state.user_id, "Welcome", "Time Spent", time_spent)
    st.session_state.next_page = "pages/1_Tutorial.py"
    # TODO check for the Tutorial start time and reset it if present

def welcome_page():
    hide_side_navbar()
    st.title("Mitigating Specification Gaming with Interactive Evolution")
    st.write("Thank you for participating in this project. What follows will be a breif tutorial which covers the basic ideas and concepts necessary to perform the required task")
    # Set up the session time tracking for this page
    if 'welcome_start_time' not in st.session_state:
        st.session_state.welcome_start_time = time.time()
    st.button("Next", key=f"welcome_next_button", on_click=switch_page, args=(st.session_state.welcome_start_time,))

def main():
    if 'welcome_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed")
        st.session_state.welcome_navbar_hidden = True
    if 'user_id' not in st.session_state:
        st.session_state.user_id = random.randint(1000000, 9999999)
        log_user_interaction(st.session_state.user_id, "Welcome", "User ID assigned", f"{st.session_state.user_id}")
    # If the current page is not stored in the session state, set it to the welcome page
    if 'next_page' not in st.session_state:
        st.session_state.next_page = "Welcome.py"
    # If the session current page is this page, display it
    if st.session_state.next_page == "Welcome.py":
        welcome_page()
    else:
        st.switch_page(st.session_state.next_page) 

if __name__ == "__main__":
    main()