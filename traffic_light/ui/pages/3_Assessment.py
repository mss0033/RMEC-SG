import streamlit as st
import time
import logging
import os
import uuid

WELCOME_PAGE_ID = "Welcome.py"
THIS_PAGE_ID = "pages/3_Assessment.py"
NEXT_PAGE_ID = "pages/4_Thank_You.py"

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

def yes_checkbox_on_change():
    st.session_state.assessment_no_col_checkbox = False

def no_checkbox_on_change():
    st.session_state.assessment_yes_col_checkbox = False

def set_mitigation_strat_selectbox_vis(is_spec_gaming_checked: bool) -> str:
    if is_spec_gaming_checked:
        return 'visible'
    else:
        return 'hidden'

def log_user_interaction(page, interaction_type, data=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Page: {page}, Interaction: {interaction_type}, Data: {data}"
    logging.info(log_entry)

def switch_page(start_time: float, mitigation_strat: str):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction("Assessment", "Time Spent", time_spent)
    log_user_interaction("Assessment", "Mitigation Strategy Selected", mitigation_strat)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Thank You start time and reset it if present

def assessment_page():
    # Make sure the side navbar is hidden
    hide_side_navbar()
    mitigation_strats = ["Strategy 1", "Strategy 2", "Strategy 3"]
    # Set up the page title and content
    st.title("Specification Gaming Assessment")
    st.write("Video clip of agent performance...")
    st.write("Agent statistics...")
    st.write("Is this individual specification gaming?")
    # Set up the checkboxes
    yes_col, no_col = st.columns(2)
    with yes_col:
        is_spec_gaming = st.checkbox("Yes", key=f"assessment_yes_col_checkbox", on_change=yes_checkbox_on_change)
    with no_col:
        is_not_spec_gaming = st.checkbox("No", key=f"assessment_no_col_checkbox", on_change=no_checkbox_on_change)
    # Set up a selection box for the mitigation strats
    if 'assessment_mitigation_strat_select_box' not in st.session_state:
        st.session_state.assessment_mitigation_strat_select_box = None
    if is_spec_gaming:
        selected_strat = st.selectbox("Select a mitigation strategy", mitigation_strats, index=None, key=f"assessment_mitigation_strat_select_box", disabled=(not is_spec_gaming))
    # print(f"Selected strat: {selected_strat}")
    # Set up the session time tracking for this page
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = time.time()
    submitt_button = st.button("Submit", key=f"assessment_submit_button", on_click=switch_page, args=(st.session_state.assessment_start_time, st.session_state.assessment_mitigation_strat_select_box))
    # print(st.session_state.mitigation_strat)

def main():
    if 'assessment_navbar_hidden' not in st.session_state:
        # Hide the side navbar, users need to flow through using the buttons and forms
        st.set_page_config(initial_sidebar_state="collapsed")
        st.session_state.assessment_navbar_hidden = True
    if 'next_page' not in st.session_state:
        st.session_state.next_page = WELCOME_PAGE_ID
    # If the session current page is this page, display it
    if st.session_state.next_page == THIS_PAGE_ID:
        assessment_page()
    else:
        st.switch_page(st.session_state.next_page)

if __name__ == "__main__":
    main()