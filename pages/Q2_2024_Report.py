import streamlit as st
from io import BytesIO
from docx import Document
import pandas as pd
from utils.data_loader import get_data,load_geospatial_data
from utils.charts import output_type_bar_chart, sunburst_chart, trend_line_chart, citation_stack, radar_chart, scatterplot

# Sidebar navigation using native hamburger menu
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

#load data
# File URLs (GitHub raw URLs)
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q2_29012025.xlsx"]
geo_url =  ['https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q2_map.xlsx']                     

# Fetch data using the modified get_data function
data = get_data(file_urls)

st.header("Analysis")

#------EXTRACT DATE-------
data["month"] = data["date_of_publication"].dt.strftime('%B')
#group by year and a month
# Get unique months, ignoring NaN, and sort them in calendar order
unique_months = sorted(
    [month for month in data["month"].unique() if pd.notna(month)],  # Ignore NaN values
    key=lambda x: pd.to_datetime(x, format='%B').month  # Sort by month order
)
# Join formatted months
formatted_months = " - ".join(unique_months)

#-----INTRO

st.markdown("""
This section presents the findings and analysis of the quarterly reports (April-June 2024).
            
The presentation is organised as follows:

- Number of mentions to EIGE (3.1);
- EIGE’s output that has been referenced (3.2);
- Documents that have referenced EIGE (3.3);

""")
#-----------3.1 NUMBER OF MENTIONS
st.subheader("3.1 Number of mentions")

st.markdown("""
In general, the number of mentions to EIGE (17) by academia seems limited when compared to the number of mentions to EIGE made by other institutions.  However, it has slightly increased when compared with Q1 (15).
The 17 citations identified correspond to eight different articles, including one article with seven citations to EIGE.
            """)

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        Download the charts by hovering over the image and clicking on the 📷 symbol in the top panel. 
    </div>
""", unsafe_allow_html=True)
st.plotly_chart(citation_stack(data, formatted_months, 2024))

#st.markdown("""
#The 15 citations identified correspond to 10 different articles, which means that most of them only include one citation to EIGE or EIGE’s outputs.
#""")

#----------3.2 EIGE's output cited
st.subheader("3.2 EIGE's output cited")

st.markdown("""
#The academic articles identified refer to six different EIGE’s outputs (reports, good practice, thesaurus, web sections (index and GBV), gender statistics database, and general reference to EIGE). The most frequently used are equally gender statistics data base and web section – index (5 citations to each). 
It is interesting to note that the reports cited (2) also refer to the gender equality index. 
""")

st.markdown("""
When compared to the previous monitoring period (Q1) it is worth noting the decrease in the citations to EIGE’s reports. """)

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(trend_line_chart(data, formatted_months, 2024,  4, 5, 6))

st.subheader("3.2.1 Monthly data")

st.markdown("""
The following figures present the types of EIGE output mentioned in the period April-May 2024.""")

st.plotly_chart(output_type_bar_chart(data, 2024))

st.markdown("""
The sunburst chart below breaks down each output category into specific outputs. 
""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Click on an element too expand the category and  see the breakdown of EIGE's outputs cited. 
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(sunburst_chart(data, formatted_months, 2024))


st.subheader("3.3 Documents citing EIGE")
st.markdown("""
Due to the nature of the academic publications monitored, it is not surprising to find that this type of documents are all research articles (except for one report). For Q2 we have not identified any books or monographs. 
""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Drag the columns to adjust the table size.
    </div>
""", unsafe_allow_html=True)

selected_columns = ['name_of_the_document_citing_eige', 'name_of_the_journal_citing_eige', 'name_of_the_institution'] 

st.write(data[selected_columns].drop_duplicates().dropna().rename(columns={
    'name_of_the_document_citing_eige': 'Document Citing EIGE',
    'name_of_the_journal_citing_eige': 'Journal Citing EIGE',
    'name_of_the_institution': 'Institution Citing EIGE'
}))

st.markdown("""
The academic publications have been prepared by 17 different authors. With the exception of one research institution in Brasil, all the authors belong to different EU universities in Austria, Belgium, Italy, Poland, Romania, Spain and Sweden. Spain is the country with most universities with publications citing EIGE (3).
There are neither any repeated authors nor repeated universities. 
The following map shows the location of the institutions that cite EIGE’s outputs.
""")

geo_data = load_geospatial_data(geo_url)
st.map(data=geo_data, size=100)

st.markdown("""
The articles citing EIGE have been published in eight different journals, most of them from the EU (3).""")

st.subheader("3.4 Impact evaluation of documents citing EIGE")
st.markdown("""
In addition to quantitative analysis of EIGE citation monitoring, quarterly and yearly reports also include a qualitative analysis that aims to assess the importance and impact of citations. Impact evaluation consists of four principal metrics: number of citations of a particular article, impact factor of a journal an article is published in, and sentiment of the citation, and location of the citation in an article.""")

st.markdown("""
The following figure shows the impact evaluation of articles citing EIGE, for Q2 2024. """)

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(radar_chart(data, formatted_months, 2024))

st.markdown("""
Overall, the sentiment of all citations in Q2 2024 was evaluated as positive. Furthermore, the majority of citations were located in the body of the article, rather than just in the abstract or references. 
For Q2 it is not possible to assess the impact factor of the journals that include citations to EIGE, as none of them has been recorded on the tool that is used for allocating the impact factor, i.e. Scopus. 
""")

st.markdown("Regarding the use of the citations to EIGE by social media, we have observed that the most frequent media used for citing EIGE’s outputs is X (formerly Twitter) with a total of 32 posts by X users. ")

st.subheader("3.4.1 Impact ranking")

st.markdown("""
While the impact metrics described above provide us with a micro view on the academic and social impact of the articles citing EIGE, it does not allow us to conduct a less granular analysis. To ensure comparability between the articles, we attributed a weight to each metric: 0,3 for number of citations, 0,2 for the impact factor and the altmetric, and 0,15 for location and category of the citation. 
These rankings will serve as a baseline and will be used for trend comparison in future reports, as the monitoring team collects more data. """)


#-----DOWNLOAD
# Save the reoport
# Path to your existing .docx file
doc_file_path = "data/2025-01-15 2024 report.docx"
# Open the file in binary mode
with open(doc_file_path, "rb") as file:
    file_data = file.read()

# Path to your existing Excel file
excel_file_path = "data/2024Q2_29012025.xlsx"
# Open the Excel file in binary mode
with open(excel_file_path, "rb") as file:
    excel_data = file.read()


#two cols
col1, col2 = st.columns(2)

with col1:
        # Create a report download button
    st.download_button(
        label="Download the Q2 2024 report",
        data=file_data,
        file_name="Q12024_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )
with col2:
    # Create data download button
    st.download_button(
        label="Download the monitoring data",
        data=excel_data,
        file_name="2024Q2_29012025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )