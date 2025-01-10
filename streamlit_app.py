import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Set the page configuration
st.set_page_config(
    page_title="Analytical Report",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Define color palette
colors = px.colors.qualitative.Pastel

# Data loader function
@st.cache_data
def get_data():
    DATA_FILENAME = Path(__file__).parent / 'data/test_eige.csv'
    raw_df = pd.read_csv(DATA_FILENAME)

    if "URL of document that references EIGE" in raw_df.columns:
        raw_df.drop("URL of document that references EIGE", axis=1, inplace=True)

    if "Type of EIGE output" in raw_df.columns:
        value_counts = raw_df["Type of EIGE output"].value_counts()
        values_to_replace = value_counts[
            (value_counts <= 1) | (value_counts.index == "Unclear")
        ].index
        raw_df["Type of EIGE output_agg"] = raw_df["Type of EIGE output"].replace(values_to_replace, "Other")

    date_column = "Date of publication of output referencing EIGE"
    if date_column in raw_df.columns:
        raw_df[date_column] = pd.to_datetime(raw_df[date_column], errors="coerce", format="mixed")

    columns_to_fill = ["Type of EIGE output_agg", "Type of EIGE output", "EIGE output referenced"]
    for col in columns_to_fill:
        if col in raw_df.columns:
            raw_df[col] = raw_df[col].fillna("Unknown")

    if "EIGE output referenced" in raw_df.columns:
        raw_df["Short Labels"] = raw_df["EIGE output referenced"].apply(
            lambda x: (x[:16] + '...') if len(x) > 15 else x
        )

    return raw_df

# Load data
data = get_data()
#---------PAGE---------------
# Sidebar menu
st.sidebar.title("EIGE Citation Monitoring")
if st.sidebar.button("Introduction and Methodology"):
    st.session_state.page = "Intro"
if st.sidebar.button("Q4 2024"):
    st.session_state.page = "Q4 2024"
if st.sidebar.button("Q1 2025"):
    st.session_state.page = "Q1 2025"

if "page" not in st.session_state:
    st.session_state.page = "Q4 2024"

    st.title("Analytical report: Measuring EIGE’s impact in academia")

if st.session_state.page == "Q4 2024":
    st.header("Overview of EIGE Outputs Q4 2024")

    st.subheader("1.1 Type of Institution")
    st.markdown('''The common trend of EU institutions making more references to EIGE than social partners was confirmed during the period in analysis. EU institutions accounted for 80% of mentions, in line with the previous quarter. 

The number of documents mentioning EIGE has dropped from 118 in Apr - Jun 2023 to 70 in July-September 2023. This reflects a common trend over the summer holiday months.  

The number of mentions has dropped more drastically, from 227 to 115. This indicates a decline in the number of EIGE outputs referenced per document compared to the previous quarter (from 1.9 to 1.64 mentions per document on average). 

September was the most active month, with 34 documents making 67 references to EIGE as opposed to only eight documents and ten mentions in August, and 28 documents and 38 mentions in July. Confirming a long-term trend, August remains the month with the lowest number of mentions.''')
    # Bar Chart: Types of EIGE Output
    topic_counts = data["Type of EIGE output_agg"].value_counts()

    bar_fig = go.Figure(data=[go.Bar(
        x=topic_counts.index,
        y=topic_counts.values,
        marker=dict(color=topic_counts.values, colorscale=colors),
        hovertemplate="Nr. of citations: %{y} <br>Type of output: %{x}"
    )])

    bar_fig.update_layout(
        title="Types of EIGE Output",
        xaxis=dict(title="Type of Output"),
        yaxis=dict(title="Number of Citations"),
        plot_bgcolor="white"
    )

    st.plotly_chart(bar_fig)

    st.subheader("1.2 Type of output referenced ")
    st.markdown('''
    Three types of output referenced stood out for a similarly significant number of mentions: Reports and their draft (19 mentions), general references (17 mentions), and the Index (16 mentions). They are closely followed by the statistical database (15 mentions) and references to EIGE’s staff (14). 

Reports were the most widely used EIGE output, accounting for 19 of the 115 individual mentions. This restored previous long-term trends which had temporarily changed during the previous quarter. 

As in the previous quarter, general references to the Institute’s work and institutional collaboration remained prominent (17 mentions), even though they were not the most frequent reference anymore.  

References to EIGE’s staff and human resources featured more prominently than in the previous quarter, with 14 mentions. This confirms a year-long trend (such references were the seventh most-frequent category in Q1, the fifth in Q2, and the third in Q3). This growth is explained by more visibility of EIGE’s staffers’ participating as speakers in events, or references to HR changes within EIGE.   

The Statistics Database and EIGE’s toolkits and online tools were mentioned 15 and 11 times, respectively. The Gender Equality Index,2 which used to feature among the main outputs referenced, came third with 16 mentions, but it is important to note that the large number of mentions is skewed by a single document from UN Women, making various references to the methodology of several version of the Index.  
    ''')
    # Sunburst Chart
    def create_sunburst_chart(data, color_palette=px.colors.qualitative.Pastel, height=600):
        fig = px.sunburst(
            data_frame=data,
            path=["Type of EIGE output_agg", "Short Labels"],
            values=[1] * len(data),
            color_discrete_sequence=color_palette
        )

        ids = fig.data[0].ids
        parents = fig.data[0].parents
        customdata = []

        for id, parent in zip(ids, parents):
            is_leaf = id not in parents
            parts = id.split("/")

            if is_leaf:
                if len(parts) == 2:
                    parent, child = parts
                    match = data.loc[
                        (data["Type of EIGE output_agg"] == parent.strip()) &
                        (data["Short Labels"] == child.strip())
                    ]
                elif len(parts) == 1:
                    parent = parts[0]
                    match = data.loc[data["Type of EIGE output_agg"] == parent.strip()]
                else:
                    match = pd.DataFrame()

                if not match.empty:
                    full_label = match["EIGE output referenced"].iloc[0]
                    customdata.append([id, full_label])
                else:
                    customdata.append([id, "No Label Found"])
            else:
                customdata.append([id, ""])

        fig.data[0].customdata = np.array(customdata)
        fig.update_traces(hovertemplate="<b>%{customdata[1]}</b><extra></extra>")
        fig.update_layout(height=height)

        return fig

    sunburst_fig = create_sunburst_chart(data)
    st.plotly_chart(sunburst_fig)

    st.subheader("1.3 Type of document mentioning EIGE’s outputs")
    st.markdown('''
    Following Q2, when an uncommonly large number of working papers was issued, Q3 saw the return to a usual trend: decision-making documents, reports, opinions, and their respective preparatory documents dominated as the main venue for use of EIGE’s outputs. 

13 Resolutions, regulation, directives and decisions (and their proposals), 13 reports (and their drafts), and 12 Opinions (and their drafts and amendments) made use of EIGE’s outputs this quarter.  

An interesting trend was observed with regards to opinions and their drafts: 
* These documents had long registered a declining trend in their likelihood to use EIGE’s outputs (16 occurrences in Q4 2022, nine in Q1 2023, five in Q2 2023). This trend saw a stark reversal this quarter, when 12 opinions and their drafts used EIGE’s outputs.  
* This is especially significant in relative terms, as opinions accounted for approximately 17.1% of all documents using EIGE’s outputs, whereas they had  only accounted for approximately 10% in Q1, and slightly over 4% in Q2.''')
    # Line Chart: Trends in Topics Referencing EIGE Over Time
    agg_df = data.groupby(["Date of publication of output referencing EIGE", "Topic"]).size().reset_index(name="Count")

    line_fig = px.line(
        agg_df,
        x="Date of publication of output referencing EIGE",
        y="Count",
        color="Topic",
        title="Trends in Topics Referencing EIGE Over Time",
        labels={
            'Date of publication of output referencing EIGE': "Date",
            'Count': 'Number of Citations',
            'Topic': 'Category'
        },
        markers=True,
        color_discrete_sequence=colors
    )

    line_fig.update_traces(line=dict(width=4), marker=dict(size=10))

    line_fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {"label": "All Topics", "method": "update", "args": [{"visible": [True]}, {"title": "Trends in Topics Referencing EIGE Over Time"}]},
                ],
                "direction": "down",
                "x": 0.99, "y": 0.5
            }
        ],
        plot_bgcolor="whitesmoke",
        legend=dict(x=0.99, y=0.89),
        width=1000,
        height=550
    )

    st.plotly_chart(line_fig)

if st.session_state.page == "Intro":
    st.header("Overview of Methodology")

    st.markdown('''
    The consultants have provided two types of deliverables: 
    * Monthly impact monitoring reports
        The monthly impact monitoring reports present all references to EIGE and EIGE’s products in EU policy making documents.
    * Analytical reports 
        The analytical report includes the main findings and trends for the monitoring period July-September 2023.  ''')
    
    st.header("Methodology")
    st.markdown('''
    For the monthly reports, we have monitored a list of ten keywords, in the databases and websites of the institutions and organisations mentioned in the section above. The keywords searched were: 
    * EIGE; 
    * Institute for Gender Equality; 
    * Institute of Gender Equality; 
    * Gender Equality Index; 
    * Gender Index; 
    * Women and Men in Decision-Making; 
    * Gender Statistics Database; 
    * Agency for Gender Equality; 
    * Carlien Scheele. 

For the analytical report, we have produced graphics and trends based on the data collected for the monthly and previous quarterly and annual reports. 
    ''')
    st.subheader("2.3 Report structure ")
    st.markdown('''
    The report is organised in two main sections and three annexes, namely: 

* this Introduction (section 2), including detail on the objectives, methodology and report structure. 

* the Analysis (section 3), presenting the analysis and of the monthly reports. 

* Annex 1 presents the monthly reports (April-June 2023). 

* Annex 2 presents the comparison charts with the previous quarter. 

* Annex 3 presents the comparisons with the same quarter of the previous year
    ''')
