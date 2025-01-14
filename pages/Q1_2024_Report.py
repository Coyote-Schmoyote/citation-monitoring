import streamlit as st
from io import BytesIO
import pandas as pd
from utils.data_loader import get_data
from utils.charts import output_type_bar_chart, sunburst_chart, trend_line_chart, citation_stack, radar_chart, scatterplot

# Sidebar navigation using native hamburger menu
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

#load data
# File URLs (GitHub raw URLs)
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/Q12024_13012025.xlsx"]

# Fetch data using the modified get_data function
data = get_data(file_urls)

st.header("Analysis")

st.markdown("""
This section presents the findings and analysis of the quarterly reports (January-March 2024).
            
The presentation is organised as follows:

- Number of mentions to EIGE (3.1);
- EIGE’s output that has been referenced (3.2);
- Documents that have referenced EIGE (3.3);

""")
#-----------3.1 NUMBER OF MENTIONS
st.subheader("3.1 Number of mentions")
st.markdown("""
In general, the number of mentions to EIGE (15) by academia seems limited when compared to the number of mentions to EIGE made by other institutions. However, due to the nature of the academic publications, the ‘rhythm’ of publishing in general is considerably slower and it is not possible to compare them with other type of publications that do not have such a lengthy and controlled procedure. 
The 15 citations identified correspond to 10 different articles, which means that most of them only include one citation to EIGE or EIGE’s outputs.

            """)

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        You can download this chart by clicking on 📷 symbol. 
    </div>
""", unsafe_allow_html=True)
st.plotly_chart(citation_stack(data))

#----------3.2 EIGE's output cited
st.subheader("3.2 EIGE's output cited")

st.markdown("""
The academic articles identified refer to five different EIGE’s outputs:
            - Reports 
            - Gender Equality Index
            - Thesaurus
            - Gender Statistics Database
            - Beijing Platform of Action (BPfA)
        
Reports are the most frequently used (7).
            """)

st.markdown("""
Regarding the reports cited, it is worth noting that (a) there are no repeated reports cited, and (b) the dates of the reports correspond to the past 10 years. 
Being the current monitoring (Q1) the first one of this monitoring assignment, the monitoring team has no previous data to compare with or to allow the production of trends. 
            """)

st.plotly_chart(trend_line_chart(data))

st.subheader("3.2.1 Monthly data")

st.markdown("""
The following figures present the type of institutions or organisations that have mentioned EIGE in the period January-March 2024. Please note that the table refers to the number of documents published, which is usually different from the number of references.
            """)

st.plotly_chart(output_type_bar_chart(data))

st.markdown("""
February was the most active month, with 5 publications citing EIGE’s outputs.  
            """)

st.markdown("""
Trend of the type of EIGE’s output cited, January-March 2024
""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 This graph is interactive. When you click on an element, it expands. 
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(sunburst_chart(data))


st.subheader("3.3 Documents citing EIGE")
st.markdown("""
Due to the nature of the academic publications monitored, it is not surprising to find that type of documents are all research articles (except for one report). For Q1 we have not identified any books or monographs.  
            
The academic publications have been prepared by 34 different authors. Most of them belong to different EU universities (except for one research institution in Mexico, and one in the United Kingdom). There are neither anyo repeated authors nor neither repeated universities.
            """)
st.plotly_chart(scatterplot(data))

st.markdown("""
The articles citing to EIGE have been published in 9 different journals, most of them from the EU (7).
            """)
st.write(data)
    
selected_columns = ['name_of_the_document_citing_eige', 'name_of_the_journal_citing_eige', 'name_of_the_institution_citing_eige'] 
st.write(data[selected_columns])

st.markdown("""
For Q1 it is not possible to assess the impact factor of the journals that include citations to EIGE, as most of them have not been recorded on the tool that is used for allocating the impact factor, i.e. Scopus. There are only three journals where the impact factor is publicly available, and they show three different impact factors, being ‘average’ (1), ‘strong’ (1), and ‘very strong’ (1). 
            """)

st.plotly_chart(radar_chart(data))

st.markdown("""
Regarding the use of the citations to EIGE by social media, we have observed that the most frequent media used for citing EIGE’s outputs is X (before Twitter) with a total of 32 posts by X users. 
            """)


#-----DOWNLOAD
# Save the DataFrame to an Excel file in memory
excel_file = BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    data.to_excel(writer, index=False, sheet_name='Sheet1')
excel_file.seek(0)

# Create a download button
st.download_button(
    label="Download the monitoring data",
    data=excel_file,
    file_name="Q12024_13012025.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary"
)