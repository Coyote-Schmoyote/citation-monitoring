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
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q3_03022025.xlsx"]
geo_url =  ['https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q3map.xlsx']                     

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

#------INTRO-----------
st.write(f"This section presents the findings and analysis of the quarterly reports {formatted_months} 2024.")
            
st.markdown("""
The presentation is organised as follows:

- Number of mentions to EIGE (3.1);
- EIGE’s output that has been referenced (3.2);
- Documents that have referenced EIGE (3.3);

""")
#-----------3.1 NUMBER OF MENTIONS
st.subheader("3.1 Number of mentions")

st.write("In general, the number of mentions to EIGE (12) by academia seems limited when compared to the number of mentions to EIGE made by other institutions. It has slightly decreased when compared with Q2 (17). The 12 citations identified correspond to ten different articles, including one article with two citations to EIGE.")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        Download the charts by hovering over the image and clicking on the 📷 symbol in the top panel. 
    </div>
""", unsafe_allow_html=True)
st.plotly_chart(citation_stack(data, formatted_months, 2024))

#----------3.2 EIGE's output cited
st.subheader("3.2 EIGE's output cited")
st.markdown("""
The academic articles identified refer to six different EIGE’s outputs (reports, good practice, thesaurus, web sections (index and GBV), gender statistics database, and general reference to EIGE). The most frequently used output in Q3  is a report (4 citations). 
When compared to the previous monitoring period (Q2) it is worth noting the decrease in the citations to EIGE’s web section – index and gender statistics database.
""")
#------MOST FREQUENT OUTPUT TYPE
st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(trend_line_chart(data, formatted_months, 2024, 7, 8, 9))

st.subheader("3.2.1 Monthly data")

st.write(f"The following figures present the types of EIGE output mentioned in the period {formatted_months} 2024.")

st.plotly_chart(output_type_bar_chart(data, 2024))

st.markdown("""
The sunburst chart in Figure 4 breaks down each output category into specific outputs. 
""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Click on an element too expand the category and  see the breakdown of EIGE's outputs cited. 
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(sunburst_chart(data, formatted_months, 2024))


st.subheader("3.3 Documents citing EIGE")
st.markdown("""
Due to the nature of the academic publications monitored, it is not surprising to find that this type of documents are all research articles (except for one report). For Q3 we have not identified any books or monographs.""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Drag the columns to adjust the table size.
    </div>
""", unsafe_allow_html=True)

selected_columns = ['name_of_the_document_citing_eige', 'name_of_the_journal_citing_eige', 'name_of_the_institution'] 

st.write(f"**Figure 5. Academic publications and journals citing EIGE, {formatted_months}, 2024**")

with st.container():
    st.write(data[selected_columns].drop_duplicates().dropna().rename(columns={
        'name_of_the_document_citing_eige': 'Document Citing EIGE',
        'name_of_the_journal_citing_eige': 'Journal Citing EIGE',
        'name_of_the_institution': 'Institution Citing EIGE'
        }))

st.markdown("""
The academic publications have been prepared by 29 different authors in nine different journals, most of them from the EU.
""")

st.markdown("""
The following map shows the location of the institutions that cite EIGE’s outputs.
""")

geo_data = load_geospatial_data(geo_url)
st.write(f"**Figure 6. Location of institutions that cited EIGE, {formatted_months}, 2024**")
st.map(data=geo_data, size=100)

#-------SPLIT BY AUTHOR
# Split the 'name_of_the_author/organisation_citing_eige' by commas
split_values = data["name_of_the_author/organisation_citing_eige"].str.split(",", expand=True)
# Stack the resulting DataFrame to get a single column of values
stacked_values = split_values.stack()
# Count the unique values and how many times each appears
value_counts = stacked_values.value_counts()
# Filter to show only the values that appear more than once (i.e., repeating values)
repeating_values = value_counts[value_counts > 1]

#--------SPLIT BY UNIVERSITY
# Split the 'name_of_the_universities' column by commas
split_values_universities = data["name_of_the_institution"].str.split(",", expand=True)
# Stack the resulting DataFrame to get a single column of university names
stacked_values_universities = split_values_universities.stack()
# Count the unique university names and how many times each appears
value_counts_universities = stacked_values_universities.value_counts()
# Filter to show only the universities that appear more than once (i.e., repeating universities)
repeating_universities = value_counts_universities[value_counts_universities > 1]

st.markdown("""
With the exception of one research institution in the United States, and one institution in South Africa, all the authors belong to different EU universities in Iceland, Norway, Finland, Poland, Germany, Belgium, Spain, Italy, and Croatia. Belgium (2), Norway (2), and Germany (2) are the countries with most universities with publications citing EIGE (3).
""")

# Create two columns
col1, col2 = st.columns(2)
# Display the repeating universities in the first column
with col1:
    st.write("Repeating Universities:")
    st.write(repeating_universities)
# Display the count of repeating universities in the second column
with col2:
    st.write("Repeating Authors:")
    st.write(repeating_values)

st.subheader("3.4 Impact evaluation of documents citing EIGE")
st.markdown("""
In addition to quantitative analysis of EIGE citation monitoring, quarterly and yearly reports also include a qualitative analysis that aims to assess the importance and impact of citations. Impact evaluation consists of four principal metrics: number of citations of a particular article, impact factor of a journal an article is published in, and sentiment of the citation, and location of the citation in an article.
""")
st.markdown("""
The following figure shows the impact evaluation of articles citing EIGE, for Q3 2024.
            """)
st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(radar_chart(data, formatted_months, 2024))

st.markdown("""
Overall, the sentiment of all citations in Q3 2024 was evaluated as positive. Furthermore, the majority of citations (7) were located in the body of the article, rather than just in the abstract or references. 
For Q3, the impact factor of the journals that include citations to EIGE vary from respectable (2), strong (2), and very strong (2), although it was not possible to record the impact factor of five journals, as they have not been recorded on the tool that is used for allocating the impact factor, i.e. Scopus.
""")

st.markdown("""
Regarding the use of the citations to EIGE by social media, we have observed that the most frequent media used for citing EIGE’s outputs is X (formerly Twitter) with a total of five posts by X users. Additionally, one of the publications in Q3 was posted one a Facebook page. 
These rankings will serve as a baseline and will be used for trend comparison in future reports, as the monitoring team collects more data.
""")

st.subheader("3.4.1 Impact ranking")
st.markdown("While the impact metrics described above provide us with a micro view on the academic and social impact of the articles citing EIGE, it does not allow us to conduct a less granular analysis. To ensure comparability between the articles, we attributed a weight to each metric: 0,3 for number of citations, 0,2 for the impact factor and the altmetric, and 0,15 for location and category of the citation. ")
with st.container():
    st.dataframe(
        data[[
            'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference', 
            'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)',
            'number_of_mentions_in_social_media_using_altmetric',
            'ranking/weight'
        ]]
        .drop_duplicates()
        .dropna()
        .rename(columns={
            'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'Location of the citation',
            'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'Impact factor',
            'number_of_mentions_in_social_media_using_altmetric': 'Altmetric',
            'ranking/weight': 'Weight'
        }),
        use_container_width=True  # ✅ Expands to fit container width
    )

#-----DOWNLOAD
# Save the reoport
# Path to your existing .docx file
doc_file_path = "data/2025-02-010_Q32024_report.docx"
# Open the file in binary mode
with open(doc_file_path, "rb") as file:
    file_data = file.read()

# Path to your existing Excel file
excel_file_path = "data/2024Q3_03022025.xlsx"
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
        file_name="2024Q3_03022025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )