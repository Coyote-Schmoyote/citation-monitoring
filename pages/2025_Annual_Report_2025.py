import streamlit as st
import pandas as pd
import re
from utils.data_loader import get_data, load_geospatial_data
from utils.charts import  total_citations_trend, annual_bar, output_type_bar_chart, sunburst_chart, trend_line_chart, radar_chart

# -----------------------------
# Sidebar / Branding
# -----------------------------
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

# -----------------------------
# Load Data
# -----------------------------
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_data/2025_all.xlsx"]
geo_url = [
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q1_map.xlsx",
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q2_map.xlsx",
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q3_map.xlsx",
    "https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/2025_maps/2025Q4_map.xlsx"
]

data = get_data(file_urls)

# -----------------------------
# Extract months & quarters dynamically
# -----------------------------
# First, ensure date column is datetime
data['date_of_publication'] = pd.to_datetime(data['date_of_publication'], errors='coerce')

# Map months to quarters
month_to_quarter = {
    1: 'Q1', 2: 'Q1', 3: 'Q1',
    4: 'Q2', 5: 'Q2', 6: 'Q2',
    7: 'Q3', 8: 'Q3', 9: 'Q3',
    10:'Q4', 11:'Q4', 12:'Q4'
}
data['quarter'] = data['date_of_publication'].dt.month.map(month_to_quarter)

# Aggregate number of publications and mentions per quarter
quarter_summary = (
    data.groupby('quarter')
        .agg({
            'name_of_the_document_citing_eige': 'nunique',  # publications
            "type_of_eige's_output_cited": 'count'          # mentions
        })
        .rename(columns={
            'name_of_the_document_citing_eige': 'Number of publications',
            "type_of_eige's_output_cited": 'Number of mentions'
        })
)

# Ensure Q1–Q4 order
quarters_order = ["Q1","Q2","Q3","Q4"]
quarter_summary = quarter_summary.reindex(quarters_order, fill_value=0)

# Add total row
total_row = pd.DataFrame({
    "Number of publications": [quarter_summary["Number of publications"].sum()],
    "Number of mentions": [quarter_summary["Number of mentions"].sum()]
}, index=["Total 2025"])

# Combine
summary_df = pd.concat([quarter_summary, total_row])

#Format months
# -----------------------------
# Extract months & quarters dynamically
# -----------------------------
data["date_of_publication"] = pd.to_datetime(data["date_of_publication"], errors="coerce")
data["month"] = data["date_of_publication"].dt.strftime('%B')

unique_months = sorted(
    data["month"].dropna().unique(),
    key=lambda x: pd.to_datetime(x, format='%B').month
)
formatted_months = " - ".join(unique_months)

# ---------
# -----------------------------
# Intro
# -----------------------------
st.header("2025 Annual Report: Analysis")
st.markdown("""
This report summarizes the findings for 2025.  

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

st.dataframe(summary_df, use_container_width=True)

#--------------SUMMARY OF PUBLICATIONS---------
# Total mentions & publications
total_mentions = quarter_summary["Number of mentions"].sum()
total_publications = quarter_summary["Number of publications"].sum()

# Most active quarter
most_active_quarter = quarter_summary["Number of publications"].idxmax()
most_active_publications = quarter_summary["Number of publications"].max()

# Dynamic text
summary_text = f"""
The monitoring team has identified **{total_mentions} mentions** to EIGE’s outputs in **{total_publications} different publications**.  
The **{most_active_quarter}** has been the most active quarter both in terms of number of publications (**{most_active_publications}**).
"""

st.markdown(summary_text)
#-------------------------------
#1.1 CITATION TREND --------------
# Total citations trend line
st.plotly_chart(total_citations_trend(data, formatted_months, 2025, *range(1,13)))
#------TEXT
# -----------------------------
# Total citations trend for dynamic text
# -----------------------------
# -----------------------------
# Dynamic citation summary
# -----------------------------
# -----------------------------
# Dynamic document summary
# -----------------------------
data_copy = data.copy()
data_copy['date_of_publication'] = pd.to_datetime(data_copy['date_of_publication'], errors='coerce')
data_copy['month'] = data_copy['date_of_publication'].dt.strftime('%B')

# Count unique documents per month
monthly_docs = data_copy.groupby('month')['name_of_the_document_citing_eige'].nunique()
monthly_docs = monthly_docs.reindex(
    sorted(monthly_docs.index, key=lambda m: pd.to_datetime(m, format='%B'))
)

# Helper to format month lists nicely
fmt = lambda lst: lst[0] if len(lst) == 1 else " and ".join(lst) if len(lst) == 2 else ", ".join(lst[:-1]) + ", and " + lst[-1]

most_val = int(monthly_docs.max())
least_val = int(monthly_docs.min())
most_months = fmt(monthly_docs[monthly_docs == monthly_docs.max()].index.tolist())
least_months = fmt(monthly_docs[monthly_docs == monthly_docs.min()].index.tolist())
total_docs = int(monthly_docs.sum())

summary_text = f"""
The **most active month(s)** in terms of documents citing EIGE were **{most_months}** with **{most_val} publications**.  
The **least active month(s)** were **{least_months}** with **{least_val} publications**.  
Overall, **{total_docs} publications** cited EIGE in 2025.
"""

st.markdown(summary_text)
#--------------------------------


# -----------------------------
# 2. EIGE's Output Cited
# -----------------------------
st.subheader("2. EIGE's Output Cited")
st.markdown("""
The academic articles refer to different EIGE outputs: reports, factsheets, research notes, thesaurus, web sections (BPfA, GM, GBV), gender statistics database, and general reference to EIGE.  
Figures below show outputs mentioned in 2025, trends per quarter, and trends per month.
""")

st.plotly_chart(annual_bar(data, 2025))

most_frequent_type = data["type_of_eige's_output_cited"].value_counts().idxmax()
count = data["type_of_eige's_output_cited"].value_counts().max()

# Count occurrences of EIGE outputs
output_counts = data["type_of_eige's_output_cited"].value_counts()

# Top 2 outputs
top_outputs = output_counts.head(2)

# Prepare text dynamically
if len(top_outputs) == 0:
    output_text = "No outputs were identified in the dataset."
elif len(top_outputs) == 1:
    output_text = f"the most frequently used output in 2025 is **{top_outputs.index[0]}** ({top_outputs.values[0]})"
else:
    output_text = (
        f"the most frequently used outputs in 2025 are **{top_outputs.index[0]}** ({top_outputs.values[0]}) "
        f"followed by **{top_outputs.index[1]}** ({top_outputs.values[1]})"
    )

# Full paragraph
dynamic_paragraph = f"""
The academic articles identified refer to different EIGE’s outputs (reports, factsheets, research notes, thesaurus, 
web sections (index, BPfA, GM, and GBV), gender statistics database, and general reference to EIGE). 
Excluding the identified documents citing EIGE that are not publicly available, we have noted that {output_text}.
"""

st.markdown(dynamic_paragraph)

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
        2025,          # year
        *range(1, 13)  # numeric months filter
    )
)


#-----------------------
st.plotly_chart(sunburst_chart(data, formatted_months, 2025))

# -----------------------------
# 3. Documents Citing EIGE
# -----------------------------
st.subheader("3. Documents Citing EIGE")
st.markdown("""
Most documents are research articles. Authors belong to multiple universities globally, mostly EU-based.
""")

geo_data = load_geospatial_data(geo_url)
st.map(data=geo_data, size=100)


# Authors
if 'name_of_the_author/organisation_citing_eige' in data.columns:
    author_series = data['name_of_the_author/organisation_citing_eige']

    # Split by comma, strip whitespace, explode
    author_split = author_series.apply(lambda x: [a.strip() for a in str(x).split(",")]).explode()

    # Filter: remove very short names (<4 chars)
    author_filtered = author_split[author_split.str.len() > 4]

    # Regex for initials-only patterns like: J. C., A.-Q., B.-M.
    # Explanation:
    # ^[A-Z](?:\.|\.-[A-Z]\.)?(?:\s[A-Z](?:\.|\.-[A-Z]\.)?)*$ 
    # - Starts with a capital letter, followed by . or .-X.
    # - Optional repeats separated by spaces
    initials_pattern = re.compile(r'^[A-Z](?:\.|\.-[A-Z]\.)(?:\s[A-Z](?:\.|\.-[A-Z]\.))*$', re.I)

    # Remove any author matching the pattern
    author_filtered = author_filtered[~author_filtered.str.match(initials_pattern)]

    # Count occurrences
    author_counts = author_filtered.value_counts()

    # Only repeating
    repeating_authors = author_counts[author_counts > 1]

    repeating_authors_display = pd.DataFrame({
        'Author': repeating_authors.index,
        'Count': repeating_authors.values
    })
else:
    repeating_authors_display = pd.DataFrame(columns=['Author', 'Count'])


# Stop words (countries, cities, etc.)
stop_words = ['spain', 'zgreb', 'norway', 'bergen', 'canada', 'gdansk']

if 'name_of_the_institution_citing_eige' in data.columns:
    uni_series = data['name_of_the_institution_citing_eige']
    # Split by comma, strip whitespace, explode
    uni_split = uni_series.apply(lambda x: [u.strip() for u in str(x).split(",")]).explode()
    # Lowercase for filtering
    uni_lower = uni_split.str.lower()
    # Remove stopwords and anything very short (<3 chars)
    uni_filtered = uni_split[~uni_lower.isin(stop_words) & (uni_split.str.len() > 2)]
    # Optional: keep only names that contain 'university' or 'college' or 'institute'
    uni_filtered = uni_filtered[uni_filtered.str.lower().str.contains('university|college|institute')]
    # Count occurrences
    counts = uni_filtered.value_counts()
    # Only repeating
    repeating_universities = counts[counts > 1]
    # Display as dataframe
    repeating_universities_display = pd.DataFrame({
        'University': repeating_universities.index,
        'Count': repeating_universities.values
    })
else:
    repeating_universities_display = pd.DataFrame(columns=['University', 'Count'])

col1, col2 = st.columns(2)

with col1:
    st.write("Repeating Universities:")
    if repeating_universities_display.empty:
        st.info("No repeating universities found or column missing.")
    else:
        st.dataframe(repeating_universities_display)

with col2:
    st.write("Repeating Authors:")
    if repeating_authors_display.empty:
        st.info("No repeating authors found or column missing.")
    else:
        st.dataframe(repeating_authors_display)
# -----------------------------
# 4. Impact Evaluation
# -----------------------------
st.subheader("4. Impact Evaluation")
st.markdown("""
Impact evaluation uses four metrics: number of citations, impact factor, sentiment, and location of the citation.  
""")
st.plotly_chart(radar_chart(data, formatted_months, 2025))

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
excel_file_path = "data/2025_data/2025_all.xlsx"

with open(doc_file_path, "rb") as f:
    doc_bytes = f.read()
with open(excel_file_path, "rb") as f:
    excel_bytes = f.read()

col1, col2 = st.columns(2)
with col1:
    st.download_button("Download 2024 Report", doc_bytes, "2024_report.docx",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
with col2:
    st.download_button("Download Monitoring Data", excel_bytes, "2025_data.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
