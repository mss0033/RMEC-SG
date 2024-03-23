import streamlit as st
import time
import logging
import os
import uuid

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

def log_user_interaction(page, interaction_type, data=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Page: {page}, Interaction: {interaction_type}, Data: {data}"
    logging.info(log_entry)

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction("Tutorial", "Time Spent", time_spent)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Examples start time and reset it if present

def tutorial_pages():
    hide_side_navbar()
    st.title("Tutorial")
    st.write("Brief explanation of specification gaming...")
    st.write("Visual examples of specification gaming...")
    # Set up the session time tracking for this page
    if 'tutorial_start_time' not in st.session_state:
        st.session_state.tutorial_start_time = time.time()
    st.button("Next", key=f"tutorial_next_button", on_click=switch_page, args=(st.session_state.tutorial_start_time,))

def main():
    if 'tutorial_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed")
        st.session_state.tutorial_navbar_hidden = True
    if 'next_page' not in st.session_state:
        st.session_state.next_page = WELCOME_PAGE_ID
    # If the session current page is this page, display it
    if st.session_state.next_page == THIS_PAGE_ID:
        tutorial_pages()
    else:
        st.switch_page(st.session_state.next_page)

if __name__ == "__main__":
    main()