import streamlit as st
from utils.data_loader import get_data
from utils.charts import output_type_bar_chart, sunburst_chart, trend_line_chart

# Sidebar navigation using native hamburger menu
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

#load data
# File URLs (GitHub raw URLs)
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/blob/main/data/2024Q4_20250109.xlsx"]

# Fetch data using the modified get_data function
data = get_data(file_urls)


st.header("The Analysis")
st.markdown("""
This section presents the findings and analysis of the quarterly reports (January-March 2023).
The presentation is organised as follows:
- Type of output – or the type of EIGE’s output that has been referenced (1.1);
- Type of document – or the type of document that has referenced EIGE (1.2);
- Journal – journal publishing the document citing EIGE (1.3)
""")

st.markdown("""
## 1.1 Type of output
            """)
# Bar Chart
st.plotly_chart(output_type_bar_chart(data))
    
st.subheader("1.2 Type of output referenced")
st.markdown("...")
    
# Sunburst Chart
st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 This graph is interactive. When you click on an element, it expands. 
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(sunburst_chart(data))
    
st.subheader("1.3 Type of document mentioning EIGE’s outputs")
st.markdown("...")
    
# Line Chart
st.plotly_chart(trend_line_chart(data))

st.markdown("""
## 1.2 Type of the document that referenced EIGE
            """)

st.markdown("""
## 1.3 Journal – journal publishing the document citing EIGE
            """)

