import streamlit as st
from utils.data_loader import get_data
from utils.charts import output_type_bar_chart, sunburst_chart, trend_line_chart

# Sidebar navigation using native hamburger menu
st.sidebar.title("EIGE Citation Monitoring")

#load data
data = get_data(["/workspaces/citation-monitoring/data/2024Q4_20250109.xlsx"])

st.header("Overview of EIGE Outputs Q4 2024")
st.subheader("1.1 Type of Institution")
st.markdown("...")

# Bar Chart
st.plotly_chart(output_type_bar_chart(data))
    
st.subheader("1.2 Type of output referenced")
st.markdown("...")
    
# Sunburst Chart
st.plotly_chart(sunburst_chart(data))
    
st.subheader("1.3 Type of document mentioning EIGE’s outputs")
st.markdown("...")
    
# Line Chart
st.plotly_chart(trend_line_chart(data))

