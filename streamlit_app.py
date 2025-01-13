import streamlit as st
import toml
from pages.Introduction import show_introduction  # Import correctly
from pages.Methodology import show_methodology
from pages.Q4_2024_Report import show_q4_2024
from pathlib import Path
from utils.data_loader import get_data

# Set the page configuration
st.set_page_config(
    page_title="EIGE Citation Monitoring in Academia: Analytical Report",
    page_icon=":bar_chart:",
    layout="centered"
)

# Sidebar navigation using native hamburger menu
st.sidebar.title("EIGE Citation Monitoring")


st.write("Hello")

