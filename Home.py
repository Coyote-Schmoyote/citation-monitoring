import streamlit as st
from pages.Introduction import show_introduction
from pages.Methodology import show_methodology
from pages.Q4_2024_Report import show_q4_2024
from pathlib import Path
from utils.data_loader import get_data

# Set the page configuration
st.set_page_config(
    page_title="EIGE Citation Monitoring in Academia: Analytical Report",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar menu with buttons for navigation
st.sidebar.title("EIGE Citation Monitoring")

# Add buttons for each page
show_intro_button = st.sidebar.button("Introduction")
show_methodology_button = st.sidebar.button("Methodology")
show_q4_2024_button = st.sidebar.button("Q4 2024")

# Initialize session state if not already set
if 'page' not in st.session_state:
    st.session_state.page = 'Introduction'  # Default page

# Update session state based on the button clicked
if show_intro_button:
    st.session_state.page = 'Introduction'
elif show_methodology_button:
    st.session_state.page = 'Methodology'
elif show_q4_2024_button:
    st.session_state.page = 'Q4 2024'

# Display the correct page based on the session state
if st.session_state.page == 'Introduction':
    show_introduction()
elif st.session_state.page == 'Methodology':
    show_methodology()
elif st.session_state.page == 'Q4 2024':
    # Define data path
    data_path = Path("/workspaces/citation-monitoring/data/2024Q4_20250109.xlsx")
    # Load data
    data = get_data([data_path])
    show_q4_2024(data)
