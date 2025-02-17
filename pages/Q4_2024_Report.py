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
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q4_20250203.xlsx"]
geo_url =  ['https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q4map.xlsx']                     

# Fetch data using the modified get_data function
data = get_data(file_urls)

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

st.header("Analysis")


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
st.markdown("""
In general, the number of mentions to EIGE (22) by academia in Q4 seems to be higher than in previous quarters Q2 (17), Q3 (12).
The 22 citations identified correspond to fourteen different articles, including one article with eight, and one article with two citations to EIGE.
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
The academic articles identified refer to eight different EIGE’s outputs (reports, factsheet, thesaurus, web sections (index, BPfA, GM, and GBV), gender statistics database, and general reference to EIGE). It is impossible to determine the most frequently used output in Q4 due to the limited access. However, the second most cited type of output in Q4 is a report (4).  """)

st.markdown("""
When compared to the previous monitoring period (Q3) it is worth noting that a wider variety of EIGE outputs was cited.  """)

#------MOST FREQUENT OUTPUT TYPE
# Get the most frequent type and its count
most_frequent_type = data["type_of_eige's_output_cited"].value_counts().idxmax()
count = data["type_of_eige's_output_cited"].value_counts().max()

st.write(f"Most frequent output type is {most_frequent_type} and it appears {count} times.")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(trend_line_chart(data, formatted_months, 2024, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

st.subheader("3.2.1 Monthly data")

st.write(f"The following figures present the types of EIGE output mentioned in the period {formatted_months} 2024. The yellow bar represents the articles the monitoring team was not able to access fully. ")

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
Due to the nature of the academic publications monitored, it is not surprising to find that this type of documents are all research articles (except for one report on the OSF Platform, and one reference entry in an encyclopaedia). For Q4 we have not identified any books or monographs. """)

st.write(f"The articles appeared in {data['name_of_the_journal_citing_eige'].nunique()} different journals.")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Drag the columns to adjust the table size.
    </div>
""", unsafe_allow_html=True)

selected_columns = ['name_of_the_document_citing_eige', 'name_of_the_journal_citing_eige', 'name_of_the_institution'] 

st.write(f"**Figure 5. Academic publications and journals citing EIGE, {formatted_months}, 2024**")
st.write(data[selected_columns].drop_duplicates().dropna().rename(columns={
    'name_of_the_document_citing_eige': 'Document Citing EIGE',
    'name_of_the_journal_citing_eige': 'Journal Citing EIGE',
    'name_of_the_institution': 'Institution Citing EIGE'
}),
use_container_width=True)


st.markdown("""
The academic publications have been prepared by 42 different authors in thirteen different journals.
With the exception of one research institution in Canada, Turkey, and the UK, all the authors belong to different EU universities in Sweden, Finland, Belgium, Germany (2), Austria, Spain (2), Italy (4), and Cyprus.
 """)

geo_data = load_geospatial_data(geo_url)
st.write(f"**Figure 6. Location of institutions that cited EIGE, {formatted_months}, 2024**")
st.map(data=geo_data, size=100)

#-------SPLIT BY AUTHOR
# Split the column by commas
split_values = data["name_of_the_author/organisation_citing_eige"].str.split(",", expand=True)
# Remove leading/trailing spaces
split_values = split_values.apply(lambda x: x.str.strip())
# Stack the DataFrame to get a single column
stacked_values = split_values.stack()
# Filter out single-letter values (including those with periods, like "P.")
stacked_values = stacked_values[stacked_values.str.len() > 2]
# Count unique values and their occurrences
value_counts = stacked_values.value_counts()
# Filter to show only values that appear more than once
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

# Display the result
st.write(f"The academic publications were prepared by {len(value_counts)} different authors from {len(value_counts_universities)} different universities. There are {len(repeating_values)} repeating authors, and {len(repeating_universities)} repeating universities:")

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

#st.markdown("""
#The articles citing to EIGE have been published in 9 different journals, most of them from the EU (7).
#            """)
st.subheader("3.4 Impact evaluation of documents citing EIGE")
st.markdown("""
In addition to quantitative analysis of EIGE citation monitoring, quarterly and yearly reports also include a qualitative analysis that aims to assess the importance and impact of citations. Impact evaluation consists of four principal metrics: number of citations of a particular article, impact factor of a journal an article is published in, and sentiment of the citation, and location of the citation in an article.
The following figure shows the impact evaluation of articles citing EIGE, for Q4 2024.
""")

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(radar_chart(data, formatted_months, 2024))

st.markdown("""
Overall, the sentiment of all citations in Q4 2024 was evaluated as positive. Furthermore, the majority of citations (12) were located in the body of the article, rather than just in the abstract.
For Q4, the impact factor of the journals that include citations to EIGE was generally stronger than in previous quarters, with 4 mentions being published in journals with very strong impact factor, and 9 mentions unpublished in journals with strong impact factor. However, it was not possible to record the impact factor of seven out of thirteen journals, as they have not been recorded on the tool that is used for allocating the impact factor, i.e. Scopus.
 """)

st.markdown("""
Regarding the use of the citations to EIGE by social media, we have observed that while  X (formerly Twitter) remains the most frequent media used for citing EIGE’s outputs in Q4 (30), there was more presence in other social media channels, such as Mendeley (14), and Bluesky (12). Overall in 2024, Q4 was the strongest in terms of reposts on social media.
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
        .rename(columns={
            'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'Location of the citation',
            'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'Impact factor',
            'number_of_mentions_in_social_media_using_altmetric': 'Altmetric',
            'ranking/weight':'Weight'
        }),
        use_container_width=True  #
    )

st.markdown("""
While the impact metrics described above provide us with a micro view on the academic and social impact of the articles citing EIGE, it does not allow us to conduct a less granular analysis. To ensure comparability between the articles, we attributed a weight to each metric: 0,3 for number of citations, 0,2 for the impact factor and the altmetric, and 0,15 for location and category of the citation. 
""")

#-----DOWNLOAD
# Save the reoport
# Path to your existing .docx file
doc_file_path = "data/2025-02-012_Q42024_report.docx"
# Open the file in binary mode
with open(doc_file_path, "rb") as file:
    file_data = file.read()

# Path to your existing Excel file
excel_file_path = "data/2024Q4_20250203.xlsx"
# Open the Excel file in binary mode
with open(excel_file_path, "rb") as file:
    excel_data = file.read()


#two cols
col1, col2 = st.columns(2)

with col1:
        # Create a report download button
    st.download_button(
        label="Download the Q4 2024 report",
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
        file_name="2024Q4_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )