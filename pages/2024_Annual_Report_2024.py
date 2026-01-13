import streamlit as st
import pandas as pd
from utils.data_loader import get_data, load_geospatial_data
from utils.charts import total_citations_trend, annual_bar, output_type_bar_chart, sunburst_chart, trend_line_chart, radar_chart

# -----------------------------
# Sidebar / Branding
# -----------------------------
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

# -----------------------------
# Load Data
# -----------------------------
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/ALLQ2024_upd.xlsx"]
geo_url = [
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q1_map.xlsx",
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q2_map.xlsx",
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q3map.xlsx",
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2024Q4map.xlsx"
]

data = get_data(file_urls)

# -----------------------------
# Extract months & quarters dynamically
# -----------------------------
data["date_of_publication"] = pd.to_datetime(data["date_of_publication"], errors="coerce")
data["month"] = data["date_of_publication"].dt.strftime('%B')
data["quarter"] = data["date_of_publication"].dt.quarter.apply(lambda x: f"Q{x}")

unique_months = sorted(
    data["month"].dropna().unique(),
    key=lambda x: pd.to_datetime(x, format='%B').month
)
formatted_months = " - ".join(unique_months)

# -----------------------------
# Intro
# -----------------------------
st.header("2024 Annual Report: Analysis")
st.markdown("""
This report summarizes the findings for 2024.  

**Sections:**
- Number of mentions to EIGE
- EIGE’s output cited
- Documents citing EIGE
- Impact evaluation and ranking
""")

# -----------------------------
# 1. Total Mentions and Publications
# -----------------------------
st.subheader("1. Total Mentions and Publications")
quarter_summary = (
    data.groupby("quarter")
        .agg({
            "name_of_the_document_citing_eige": "nunique",
            "type_of_eige's_output_cited": "count"
        })
        .rename(columns={
            "name_of_the_document_citing_eige": "Number of publications",
            "type_of_eige's_output_cited": "Number of mentions"
        })
)

# Ensure Q1–Q4 order
quarters_order = ["Q1","Q2","Q3","Q4"]
quarter_summary = quarter_summary.reindex(quarters_order, fill_value=0)

# Add total row
total_row = pd.DataFrame({
    "Number of publications": [quarter_summary["Number of publications"].sum()],
    "Number of mentions": [quarter_summary["Number of mentions"].sum()]
}, index=["Total 2024"])

summary_df = pd.concat([quarter_summary, total_row])
st.dataframe(summary_df, use_container_width=True)

# -----------------------------
# 2. EIGE's Output Cited
# -----------------------------
st.subheader("2. EIGE's Output Cited")
st.markdown("""
The academic articles refer to different EIGE outputs: reports, factsheets, research notes, thesaurus, web sections (BPfA, GM, GBV), gender statistics database, and general reference to EIGE.  
Figures below show outputs mentioned in 2024, trends per quarter, and trends per month.
""")

st.plotly_chart(annual_bar(data, 2024))

most_frequent_type = data["type_of_eige's_output_cited"].value_counts().idxmax()
count = data["type_of_eige's_output_cited"].value_counts().max()
st.write(f"Most frequent output type: **{most_frequent_type}**, appearing {count} times.")

#----- TREND LINE-------
# -----------------------------
# Trend Line Chart (Annual)
# -----------------------------
# automatically get all months present in the data
months_names = data['date_of_publication'].dt.strftime('%B').dropna().unique()
months_names_sorted = sorted(months_names, key=lambda x: pd.to_datetime(x, format='%B'))
months_str = " - ".join(months_names_sorted)

# plot trend line
months_names = data['date_of_publication'].dt.strftime('%B').dropna().unique()
months_names_sorted = sorted(months_names, key=lambda x: pd.to_datetime(x, format='%B'))
months_str = " - ".join(months_names_sorted)

# call the updated trend_line_chart
st.plotly_chart(
    trend_line_chart(
        data,          # first positional argument is your DataFrame
        months_str,    # string used for x-axis ordering
        2024,          # year
        *range(1, 13)  # numeric months filter
    )
)


#-----------------------
st.plotly_chart(sunburst_chart(data, formatted_months, 2024))

# -----------------------------
# 3. Documents Citing EIGE
# -----------------------------
st.subheader("3. Documents Citing EIGE")
st.markdown("""
Most documents are research articles. Authors belong to multiple universities globally, mostly EU-based.
""")

geo_data = load_geospatial_data(geo_url)
st.map(data=geo_data, size=100)

# Repeat authors & universities
authors = data["name_of_the_author/organisation_citing_eige"].str.split(",", expand=True).stack().str.strip()
authors = authors[authors.str.len() > 2].value_counts()
repeating_authors = authors[authors > 1]

universities = data["name_of_the_institution"].str.split(",", expand=True).stack()
repeating_universities = universities.value_counts()[lambda x: x > 1]

col1, col2 = st.columns(2)
with col1:
    st.write("Repeating Universities:")
    st.write(repeating_universities)
with col2:
    st.write("Repeating Authors:")
    st.write(repeating_authors)

# -----------------------------
# 4. Impact Evaluation
# -----------------------------
st.subheader("4. Impact Evaluation")
st.markdown("""
Impact evaluation uses four metrics: number of citations, impact factor, sentiment, and location of the citation.  
""")
st.plotly_chart(radar_chart(data, formatted_months, 2024))

# -----------------------------
# 5. Impact Ranking
# -----------------------------
st.subheader("Top-5 of Most Impactful Articles")

top5_df = (
    data[["name_of_the_document_citing_eige", "ranking/weight"]]
    .rename(columns={
        "name_of_the_document_citing_eige": "Document citing EIGE",
        "ranking/weight": "Weight"
    })
    .sort_values(by="Weight", ascending=False)  # top weights first
    .head(5)  # take only top 5
    .reset_index(drop=True)  # reset index to 0-based first
)

# create 1-based numbering
top5_df.index = top5_df.index + 1
top5_df.index.name = "Rank"

st.dataframe(top5_df, use_container_width=True)


# -----------------------------
# Download Section
# -----------------------------
st.subheader("Download Report / Data")
doc_file_path = "data/2024_report.docx"
excel_file_path = "data/ALLQ2024_upd.xlsx"

with open(doc_file_path, "rb") as f:
    doc_bytes = f.read()
with open(excel_file_path, "rb") as f:
    excel_bytes = f.read()

col1, col2 = st.columns(2)
with col1:
    st.download_button("Download 2024 Report", doc_bytes, "2024_report.docx",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
with col2:
    st.download_button("Download Monitoring Data", excel_bytes, "2024_data.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
