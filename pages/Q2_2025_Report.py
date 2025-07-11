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
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_data/2025Q2.xlsx"]
geo_url =  ['https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q2_map.xlsx']                     

# Fetch data using the modified get_data function
data = get_data(file_urls)

unique_articles = data.dropna(subset=["name_of_the_document_citing_eige"])\
                      .drop_duplicates(subset="name_of_the_document_citing_eige", keep="first")


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
st.markdown("""
This section presents the findings for the second quarterly report of 2025.  
The presentation is organised as follows:

- **Number of mentions to EIGE**
- **EIGE’s output that has been referenced**
- **Documents that have referenced EIGE**
- **Impact evaluation of documents citing EIGE**
- **Impact ranking**
""")
            
#-----------3.1 NUMBER OF MENTIONS
st.subheader("3.1 Number of mentions")

st.markdown("""In general, the number of mentions to EIGE (26) by academia has decreased when compared to Q1 2025 (33). However, when comparing it with the same period of 2024 (Q2) the number of citations has increased, compared to 17 citations to EIGE from 8 different documents.
The 26 citations identified correspond to 8 different articles, including one article with 13 citations to EIGE.""")

total_citations = pd.to_numeric(data["number_of_citations_(using_google_scholar)"], errors='coerce').fillna(0).astype(int).sum()

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
st.subheader("EIGE's output cited")

st.markdown("""
The academic articles identified refer to 10 different EIGE’s outputs (reports, good practice, work programme, factsheet, toolkit, thesaurus, web section (index), gender statistics database, and general reference to EIGE). The most frequently used output in Q2 is a report (seven citations). 
            """)

#st.markdown("""
#Regarding the reports cited, it is worth noting that (a) there are no repeated reports cited, and (b) the dates of the reports correspond to the past 10 years. 
#Being the current monitoring (Q1) the first one of this monitoring assignment, the monitoring team has no previous data to compare with or to allow the production of trends. 
#            """)

#------MOST FREQUENT OUTPUT TYPE
# Get the most frequent type and its count
most_frequent_type = data["type_of_eige's_output_cited"].value_counts().idxmax()
count = data["type_of_eige's_output_cited"].value_counts().max()

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(trend_line_chart(data, formatted_months, 2025, 4, 5, 6))

st.markdown("""
When compared to the previous monitoring period (Q1 2025), it is worth noting the similarity in the number of the most frequently used output (6 reports in Q1 2025 versus 7 reports in Q2 2025).
""")

st.write(f"The following figures present the types of EIGE output mentioned in the period {formatted_months} 2025.")

st.plotly_chart(output_type_bar_chart(data, 2025))

#st.markdown("""
#February was the most active month, with 5 publications citing various EIGE’s outputs, including reports, BfPA, and thesaurus. Overall, reports (6) were the most commonly cited type of EIGE’s outputs in January-March 2024, followed by gender equality index (2).
#            """)

st.markdown("""
The sunburst chart below breaks down each output category into specific outputs. 
""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Click on an element too expand the category and  see the breakdown of EIGE's outputs cited. 
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(sunburst_chart(data, formatted_months, 2025))


st.subheader("Documents citing EIGE")
st.markdown("""
Due to the nature of the academic publications monitored, it is not surprising to find that this type of documents are all research articles. For Q2 we have not identified any reports, books or monographs. 
The academic publications have been prepared by 37 different authors mostly from universities (21) in 8 different journals.
            """)
st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Drag the columns to adjust the table size.
    </div>
""", unsafe_allow_html=True)

selected_columns = ['name_of_the_document_citing_eige', 'name_of_the_journal_citing_eige', 'name_of_the_institution_citing_eige'] 

st.write(f"**Figure 5. Academic publications and journals citing EIGE, {formatted_months}, 2025**")
st.write(data[selected_columns].drop_duplicates().dropna().rename(columns={
    'name_of_the_document_citing_eige': 'Document Citing EIGE',
    'name_of_the_journal_citing_eige': 'Journal Citing EIGE',
    'name_of_the_institution_citing_eige': 'Institution Citing EIGE'
}),
use_container_width=True)


st.markdown("""
The majority of authors belonged to research institutions in the EU: Italy, Spain, Netherlands, Sweden, Switzerland, Poland, and Cyprus. Italy is the country with the highest number of authors from different universities (6) with publications citing EIGE. Additionally, there were 2 institutes located in Canada, 1 in the United States, and 1 in Australia.
The following map shows the location of the institutions that cite EIGE’s outputs.

""")

geo_data = load_geospatial_data(geo_url)
st.write(f"**Figure 6. Location of institutions that cited EIGE, {formatted_months}, 2025**")
st.map(data=geo_data, size=100)

#-------SPLIT BY AUTHOR
# Split the 'name_of_the_author/organisation_citing_eige' by commas
split_values = unique_articles["name_of_the_author/organisation_citing_eige"].str.split(",", expand=True)
# Stack the resulting DataFrame to get a single column of values
stacked_values = split_values.stack()
# Count the unique values and how many times each appears
value_counts = stacked_values.value_counts()
# Filter to show only the values that appear more than once (i.e., repeating values)
repeating_values = value_counts[value_counts > 1]

#--------SPLIT BY UNIVERSITY
# Split the 'name_of_the_universities' column by commas
split_values_universities = unique_articles["name_of_the_institution_citing_eige"].str.split(",", expand=True)
# Stack the resulting DataFrame to get a single column of university names
stacked_values_universities = split_values_universities.stack()
# Count the unique university names and how many times each appears
value_counts_universities = stacked_values_universities.value_counts()
# Filter to show only the universities that appear more than once (i.e., repeating universities)
repeating_universities = value_counts_universities[value_counts_universities > 1]

# Display the result
# st.write(f"The academic publications were prepared by {len(value_counts_universities)} different universities and institutions.")
# Create two columns
#col1, col2 = st.columns(2)
# Display the repeating universities in the first column
#with col1:
#    st.write("Repeating Universities:")
#    st.write(repeating_universities)
# Display the count of repeating universities in the second column
#with col2:
#    st.write("Repeating Authors:")
#    st.write(repeating_values)

#st.markdown("""
#The articles citing to EIGE have been published in 9 different journals, most of them from the EU (7).
#            """)
st.subheader("Impact evaluation of documents citing EIGE")
st.markdown("""
For Q2 it is not possible to assess the impact factor of the journals that include citations to EIGE, as most of them have not been recorded on the tool that is used for allocating the impact factor, i.e. Scopus. The following figure shows the impact evaluation of articles citing EIGE, for Q2 2025.

""")
#st.markdown("""
#For Q1 it is not possible to assess the impact factor of the journals that include citations to EIGE, as most of them have not been recorded on the tool that is used for allocating the impact factor, i.e. Scopus. There are only three journals where the impact factor is publicly available, and they show three different impact factors, being ‘average’ (1), ‘strong’ (1), and ‘very strong’ (1). 
#            """)
st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(radar_chart(data, formatted_months, 2024))

st.markdown("""
Overall, the sentiment of all citations in Q2 2025 was evaluated as positive. Furthermore, the majority of citations (8) were in the body of the article, rather than just in the abstract or references. 
Regarding the use of the citations to EIGE by social media, we have observed that the most frequent media used for citing EIGE’s outputs is X with a total of 6 posts by X users, followed by 3 posts by BlueSky users. In general, the use of social media seems rather limited. 
            """)

st.subheader("Impact ranking")
st.markdown("While the impact metrics described above provide us with a micro view on the academic and social impact of the articles citing EIGE, it does not allow us to conduct a less granular analysis. To ensure comparability between the articles, we attributed a weight to each metric: 0,3 for number of citations, 0,2 for the impact factor and the altmetric, and 0,15 for location and category of the citation. ")
with st.container():
    st.dataframe(
        data[[
            'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference', 
            'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)',
            'number_of_mentions_in_social_media_using_altmetric',
            'ranking/weight'
        ]]
        .rename(columns={
            'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'Location of the citation',
            'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'Impact factor',
            'number_of_mentions_in_social_media_using_altmetric': 'Altmetric',
            'ranking/weight':'Weight'
        }),
        use_container_width=True  #
    )

#-----DOWNLOAD
# Save the reoport
# Path to your existing .docx file
doc_file_path = "data/2025-01-15 2024 report.docx"
# Open the file in binary mode
with open(doc_file_path, "rb") as file:
    file_data = file.read()

# Path to your existing Excel file
excel_file_path = "data/2025_data/2025Q2.xlsx"
# Open the Excel file in binary mode
with open(excel_file_path, "rb") as file:
    excel_data = file.read()


#two cols
col1, col2 = st.columns(2)

with col1:
        # Create a report download button
    st.download_button(
        label="Download the Q2 2025 report",
        data=file_data,
        file_name="Q42024_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )
with col2:
    # Create data download button
    st.download_button(
        label="Download the monitoring data",
        data=excel_data,
        file_name="data/2025_data/2025Q1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )