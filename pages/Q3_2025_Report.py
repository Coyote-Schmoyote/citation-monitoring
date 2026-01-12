import streamlit as st
import pandas as pd
from utils.data_loader import get_data, load_geospatial_data
from utils.charts import output_type_bar_chart, sunburst_chart, trend_line_chart, citation_stack, radar_chart

# ---------- Load data ----------
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_data/2025Q3.xlsx"]
geo_url = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q3_map.xlsx"]
data = get_data(file_urls)
unique_articles = data.drop_duplicates(subset="name_of_the_document_citing_eige")

# ---------- Months formatting ----------
data["month"] = data["date_of_publication"].dt.strftime('%B')
unique_months = sorted([m for m in data["month"].unique() if m], key=lambda x: pd.to_datetime(x, format='%B').month)
formatted_months = " - ".join(unique_months)

# ---------- Header ----------
st.header(f"Q3 2025 Report ({formatted_months})")
st.write(f"Number of mentions: {len(data)}")
st.write(f"Number of unique documents: {data['name_of_the_document_citing_eige'].nunique()}")

# ---------- Stacked bar ----------
st.subheader("Mentions per document")
st.plotly_chart(citation_stack(data, months=formatted_months, year=2025))

# ---------- Trend line ----------
st.subheader("Trend of EIGE output citations")
# Get sorted months from your data
months_names = data['date_of_publication'].dt.strftime('%B').dropna().unique()
months_names_sorted = sorted(months_names, key=lambda x: pd.to_datetime(x, format='%B').month)
months = " - ".join(months_names_sorted)

# Call trend line
st.subheader("Trend of EIGE Output Citations")
st.plotly_chart(trend_line_chart(data, months, 2025))


# ---------- Bar chart ----------
st.subheader("EIGE Output Type")
st.plotly_chart(output_type_bar_chart(data, 2025))

# ---------- Sunburst ----------
st.subheader("Breakdown by output")
st.plotly_chart(sunburst_chart(data, formatted_months, 2025))

# ---------- 3.3 Documents citing EIGE ----------
st.subheader("Documents citing EIGE")
selected_columns = ['name_of_the_document_citing_eige','name_of_the_journal_citing_eige','name_of_the_institution_citing_eige']
st.dataframe(unique_articles[selected_columns].drop_duplicates(), use_container_width=True)

# ---------- Map ----------
geo_data = load_geospatial_data(geo_url)
st.subheader("Location of institutions citing EIGE")
st.map(data=geo_data)

# ---------- Radar ----------
st.subheader("Impact evaluation of documents citing EIGE")
st.plotly_chart(radar_chart(data, formatted_months, 2025))

# ---------- Impact Ranking ----------
st.subheader("Impact Ranking of Articles")
ranking_columns = [
    'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference',
    'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)',
    'number_of_mentions_in_social_media_using_altmetric',
    'ranking/weight'
]

ranking_rename = {
    'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'Location of the citation',
    'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'Impact factor',
    'number_of_mentions_in_social_media_using_altmetric': 'Altmetric',
    'ranking/weight': 'Weight'
}

if all(col in data.columns for col in ranking_columns):
    st.dataframe(data[ranking_columns].rename(columns=ranking_rename), use_container_width=True)
else:
    missing_cols = [col for col in ranking_columns if col not in data.columns]
    st.warning(f"Missing columns for Impact Ranking table: {missing_cols}")

# ---------- Download ----------
doc_file_path = "data/2025-01-15 2024 report.docx"
excel_file_path = "data/2025_data/2025Q3.xlsx"
with open(doc_file_path, "rb") as file: file_data = file.read()
with open(excel_file_path, "rb") as file: excel_data = file.read()

col1, col2 = st.columns(2)
with col1:
    st.download_button("Download Q3 2025 report", data=file_data, file_name="Q3_2025_report.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
with col2:
    st.download_button("Download monitoring data", data=excel_data, file_name="data_Q3_2025.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")