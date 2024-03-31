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
    # logging.info(log_entry)
    print(log_entry)

def switch_page(start_time: float):
    end_time = time.time()
    time_spent = end_time - start_time
    log_user_interaction("Tutorial", "Time Spent", time_spent)
    st.session_state.next_page = NEXT_PAGE_ID
    # TODO check for the Examples start time and reset it if present

def tutorial_pages():
    hide_side_navbar()
    st.title("Tutorial")
    st.write(f"""This project aims to tackle a problem commonly found in optimization functions, such as those used in Machine Learning, Artificial Intellegence, and Evolutionary Computing.
             \n This problem as a few names, but for our purposes it will hereby be referred to as Specification Gaming.
             \nSpecification Gaming, for the purpose of this project, is defined as: A situation where an optimization system, such as a Neural Network or Evolutionary Computing, produces a result which performs well according to some objective (i.e.\"maximize fitness\") by doing something unexpected or undesired.
             \nBelow are some visual examples of specification gaming""")
    col_1, col_2, col_3 = st.columns(3)
    col_1.image("traffic_light/ui/resources/SG_example_images/block_flip.gif", caption=f"A robot trained to stack blocks was scored based on if the bottom of one block was at the same height as the top of the other block. The robot learned to simply flip over a block")
    col_2.image("traffic_light/ui/resources/SG_example_images/boat_race.gif", caption=f"A boat race game playing agent was scored based on the score of the game. The agent learned it could achieve a higher score by simply collecting the power ups repeatedly.")
    col_3.image("traffic_light/ui/resources/SG_example_images/slide_to_the_right.gif", caption=f"An evovled created \'discovered\' and exploit in the physics engine that allowed it to simply glide to the side instead of running")
    st.image("traffic_light/ui/resources/SG_example_images/quilt_of_sg.gif", caption=f"A collection of similar instances across a wide range of optimization systems.")
    st.write(f"""From the above examples a common theme emerges. All of the products of optimization found unexpected, and nominally undesirable, methods of technicnally satisfying their optimization function while not having the desired emergent properties or behaviors.
             \nWhile some of these exmaples may be ammusing, unfortunately not all examples are so funny. In more serious sitations agents trained to drive cars or control planes may adopt niche behavior that scores well according to some optimization process but would put people at dire risk.
             \nTo go further, when these issues occur typically they are discovered at the end of long and expensive optimization processes such as evolutionary runs or neural network trainings. Therefore, specification gaming can also represent a significat and expensive time loss when it occurs. 
             \nSo, to address this issue, this project seeks to investigate whether human-in-the-loop interactions can help identify and mitigate this Specification Gaming problem.""")
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