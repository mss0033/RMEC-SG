import streamlit as st
import time
import logging
import os
import uuid

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

def log_user_interaction(page, interaction_type, data=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Page: {page}, Interaction: {interaction_type}, Data: {data}"
    # logging.info(log_entry)
    print(log_entry)

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction("Thank You", "Time Spent", time_spent)
    st.session_state.next_page = WELCOME_PAGE_ID
    # If they go back around, reset the welcome start time
    st.session_state.welcome_start_time = time.time()

def thank_you_page():
    # Make sure the side navbar is hidden
    hide_side_navbar()
    # Set up the page title and content
    st.title("The End")
    st.write("Thank you for your participation!")
    # Set up the session time tracking for this page
    if 'thank_you_start_time' not in st.session_state:
        st.session_state.thank_you_start_time = time.time()
    # st.button("Restart", key=f"thank_you_restart_button", on_click=switch_page, args=(st.session_state.thank_you_start_time,))

def main():
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