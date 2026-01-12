import streamlit as st
from io import BytesIO
from docx import Document
import pandas as pd
from utils.data_loader import get_data,load_geospatial_data
from utils.charts import annual_bar, output_type_bar_chart, sunburst_chart, trend_line_chart, radar_chart

# Sidebar navigation using native hamburger menu
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

#load data
# File URLs (GitHub raw URLs)
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_data/2025_all.xlsx"
             ]
geo_url =  ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q1_map.xlsx",
            "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q2_map.xlsx",
            "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q3_map.xlsx",
            "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q4_map.xlsx"]                      

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
st.write(f"This section presents the findings for the four quarterly reports of 2025.")
            
st.markdown("""
The presentation is organised as follows:

- Number of mentions to EIGE (2.1);
- EIGE’s output that has been referenced (2.2);
- Documents that have referenced EIGE (2.3);

""")
#-----------3.1 NUMBER OF MENTIONS
st.subheader("2.1 Number of mentions")
#st.markdown("""
#In general, the number of mentions to EIGE (15) by academia seems limited when compared to the number of mentions to EIGE made by other institutions. However, due to the nature of the academic publications, the ‘rhythm’ of publishing in general is considerably slower and it is not possible to compare them with other types of publications that do not have such a lengthy and controlled procedure.
#            """)
st.write(
    "The monitoring team has identified 69 mentions to EIGE or EIGE’s outputs in 41 different publications. The Q4 has been the most active quarter both in terms of number of publications (13) and of mentions to EIGE (27).")

data_summary = {
    "Quarter": ["Q1", "Q2", "Q3", "Q4", "Total 2025"],
    "Number of publications": [10, 8, 10, 13, 41],
    "Number of mentions": [15, 17, 10, 27, 69]
}

st.dataframe(data_summary)

st.subheader("2.2 EIGE's output cited")
st.markdown("""
The academic articles identified refer to different EIGE’s outputs (reports, factsheet, research notes, thesaurus, web sections (index, BPfA, GM, and GBV), gender statistics database, and general reference to EIGE). Excluding the identified documents citing EIGE that are not publicly available, we have noted that the most frequently used output in 2024 are the reports (17) followed by the gender statistics database (6).
The following figures show the different outputs mentioned in 2024 (figure 3), and the trends by type per quarter (figure 4), and by type per month (figure 5).

#            """)


st.plotly_chart(output_type_bar_chart(data, 2025))

st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        Download the charts by hovering over the image and clicking on the 📷 symbol in the top panel. 
    </div>
""", unsafe_allow_html=True)
st.plotly_chart(annual_bar(data, 2025))


#st.markdown("""
#The 15 citations identified correspond to 10 different articles, which means that most of them only include one citation to EIGE or EIGE’s outputs.
#""")

#----------3.2 EIGE's output cited




#st.markdown("""
#Regarding the reports cited, it is worth noting that (a) there are no repeated reports cited, and (b) the dates of the reports correspond to the past 10 years. 
#Being the current monitoring (Q1) the first one of this monitoring assignment, the monitoring team has no previous data to compare with or to allow the production of trends. 
#            """)

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

st.plotly_chart(trend_line_chart(data, formatted_months, 2025, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))


st.write(f"The sunburst chart in Figure 6 breaks down each output category into specific outputs for 2025.")




st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Click on an element too expand the category and  see the breakdown of EIGE's outputs cited. 
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(sunburst_chart(data, formatted_months, 2025))


st.subheader("2.3 Documents citing EIGE")
st.markdown("""
Due to the nature of the academic publications monitored, it is not surprising to find that this type of documents are all research articles (except for one report). For Q1 we have not identified any books or monographs. 
            """)



st.markdown("""
Due to the nature of the academic publications monitored, it is not surprising to find that this type of documents are all research articles (except for three documents).
The documents citing EIGE have been published in 39 different journals, most of them based in the EU. 
Regarding the authors of the articles citing EIGE, we have identified 121 different authors that belong to 77 different research centres (the large majority being EU based universities). Only one repeating author published two documents citing EIGE. 
Except for some research institutions in Canada, Turkey, the UK, Australia, Brasil, Mexico, Iceland and EEUU, the large majority of the authors belong to different EU universities EU Member States.
The following map shows the location of the institutions that cite EIGE’s outputs.

""")

geo_data = load_geospatial_data(geo_url)
st.write(f"**Figure 6. Location of institutions that cited EIGE, 2025**")
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
st.subheader("2.4 Impact evaluation of documents citing EIGE")
#st.markdown("""
#In addition to quantitative analysis of EIGE citation monitoring, quarterly and yearly reports also include a qualitative analysis that aims to assess the importance and impact of citations. Impact evaluation consists of four principal metrics: number of citations of a particular article, impact factor of a journal an article is published in, and sentiment of the citation, and location of the citation in an article.
#""")
st.markdown("""
In addition to quantitative analysis of EIGE citation monitoring, quarterly and yearly reports also include a qualitative analysis that aims to assess the importance and impact of citations. Impact evaluation consists of four principal metrics: number of citations of a particular article, impact factor of a journal an article is published in, and sentiment of the citation, and location of the citation in an article.
            """)
st.markdown("""
    <div style="background-color: #949494; color: white; padding: 10px; border-radius: 8px;">
        💡 Use the legend on the right side of the graph to remove or add the elements.
    </div>
""", unsafe_allow_html=True)

st.plotly_chart(radar_chart(data, formatted_months, 2025))

st.markdown("""
Overall, the sentiment of all citations in 2024 was evaluated as positive. Furthermore, the majority of citations (34) were located in the body of the article, rather than just in the abstract.
The impact factor of the publishing journals for 2024 was not always publicly available. However, when available, most of the publishing journals (7) were classified  as journals with a high impact factor. 
In general, in 2024 there was a limited use of the citations to EIGE by social media. However, X appears to be the most frequent media used for citing EIGE’s outputs.
""")

st.subheader("2.5 Impact ranking")
st.markdown("""
            To ensure comparability between the publications, we attributed a weight to each metric: 0,3 for number of citations, 0,2 for the impact factor and the altmetric, and 0,15 for location and category of the citation. Figure 9 shows all the publications that include mentions to EIGE in 2024, organised by their allocated weight. 
Considering the allocated weights, the publications citing EIGE with the highest impact are the article titled “Evidence-based policy-making in normatively divided policy fields: European Institute for Gender Equality, Agency for Fundamental Rights and Slovak policies tackling violence against women” published on 31.10.2024 by a researcher from the University of Antwerpen, followed by the “Multidimensional domestic gender inequality and the global diffusion of women’s ministries, 1975–2015” published on 31.12.2024 by a researcher from the University Carlos III Madrid
""")

with st.container():
    st.dataframe(
        data[[
            'name_of_the_document_citing_eige', 

            'ranking/weight'
        ]]
        .rename(columns={

            'name_of_the_document_citing_eige': 'Document citing EIGE',
            'ranking/weight':'Weight'
        }),
        use_container_width=True  #
    )



#-----DOWNLOAD
# Save the reoport
# Path to your existing .docx file
doc_file_path = "data/2024_report.docx"
# Open the file in binary mode
with open(doc_file_path, "rb") as file:
    file_data = file.read()

# Path to your existing Excel file
excel_file_path = "data/ALLQ2024_upd.xlsx"
# Open the Excel file in binary mode
with open(excel_file_path, "rb") as file:
    excel_data = file.read()


#two cols
col1, col2 = st.columns(2)

with col1:
        # Create a report download button
    st.download_button(
        label="Download the 2025 report",
        data=file_data,
        file_name="2024_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )
with col2:
    # Create data download button
    st.download_button(
        label="Download the monitoring data",
        data=excel_data,
        file_name="2024_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )