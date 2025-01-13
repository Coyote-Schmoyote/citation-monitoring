import streamlit as st
from utils.data_loader import get_data

# Set the page configuration
st.set_page_config(
    page_title="EIGE Citation Monitoring in Academia: Analytical Report",
    page_icon=":bar_chart:",
    layout="centered"
)

# Sidebar navigation using native hamburger menu
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")


st.header("About this project")
st.markdown("""
   EIGE contracted Blomeyer & Sanz, in partnership with Policy Impact Lab, on 24 September 2024 to conduct periodic impact monitoring reports and their analysis corresponding to the period 2024. The Terms of Reference (ToR) refer to a general objective and to five specific objectives: 

- **General**: to allow EIGE to better comprehend stakeholders’ use of EIGE data, evidence and outputs and thereby to produce more targeted outputs which fit better the needs of its stakeholders’. enable EIGE produce outputs which are used by its intended stakeholders.
- **Specific**: to provide EIGE with information on 
    1.  which EIGE outputs are cited in academia; 
    2. what are the main articles citing EIGE’s outputs; 
    3. what are the main research fields (topics) where citations to EIGE are found; 
    4. what is the importance of the citations identified; and 
    5. what is the trend observed in the citations to EIGE.
            
This analytical report presents the main findings regarding the data on academia citing EIGE’s outputs during the period January to March 2024. The analytical report includes a statistical overview of the recorded references.
""")

st.divider()

st.header("How to use this app")
st.markdown("""
This monitoring report is compiled on Streamlit platform using Python programming language. 

### Navigation
- Methodology and our overall approach is described in detail in the **Methodology** page.
- Reports are also available from the navigation menu on the left, titled in a format "Qx_YYYY_Report".         

### Report
- Most of the charts and graphs in the report have interactive elements. Feel free to explore the data by clicking and hovering on different elements.
- It is possible to collapse the navigaiton on the left side by clicking on <, and expand it again by clicking on >.
- You can export the report as a .pdf file by clicking on ⋮ symbol in the top right corner, and selecting "Print".
- You can adjust the visual theme of the report (light or dark) by clicking on ⋮ and going to "Settings".
- The excel file with monitoring data is available to download at the bottom of each quarterly report.        
            """)

