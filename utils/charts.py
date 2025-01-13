import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio 
import numpy as np
import pandas as pd 

colors = px.colors.qualitative.Pastel

def output_type_bar_chart(data):
    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Use the correct column name
    required_column = "type_of_eige's_output_cited_agg"
    if required_column not in data.columns:
        raise KeyError(
            f"Column '{required_column}' not found in the dataset. "
            f"Available columns: {list(data.columns)}"
        )

    # Count occurrences of each type of EIGE output
    topic_counts = data[required_column].value_counts()

    # Create the bar chart
    fig = go.Figure(data=[go.Bar(
        x=topic_counts.index,
        y=topic_counts.values
    )])

    # Update styling
    fig.update_traces(
        name="November 2023",
        width=0.95,
        marker=dict(
            color=topic_counts.values,
            colorscale=colors
        ),
        hovertemplate="Nr. of citations: %{y} <br>Type of output: %{x}"
    )
    fig.update_layout(
        width=800,
        title="Count of EIGE Outputs by type",
        title_font=dict(family="Verdana", size=20, color=colors[0]),
        font_size=12,
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    return fig

def sunburst_chart(data, color_palette=px.colors.qualitative.Pastel, height=600):
    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Check for required columns
    required_columns = ["type_of_eige's_output_cited_agg", "short_labels"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        raise KeyError(
            f"Required columns {missing_columns} not found in the dataset. "
            f"Available columns: {list(data.columns)}"
        )

    # Drop rows with NaN values in the required columns
    filtered_data = data.dropna(subset=required_columns)

    # Create the sunburst chart
    fig = px.sunburst(
        data_frame=filtered_data,
        path=["type_of_eige's_output_cited_agg", "short_labels"],
        values=[1] * len(filtered_data),
        color_discrete_sequence=color_palette
    )

    # Extract IDs and parents from the chart
    ids = fig.data[0].ids
    parents = fig.data[0].parents
    customdata = []

    # Loop over each ID and parent to determine whether it is a leaf or parent node
    for id, parent in zip(ids, parents):
        is_leaf = id not in parents  # If `id` is not a parent, it's a leaf
        parts = id.split("/")

        if is_leaf and len(parts) == 2:  # Child node (leaf)
            parent, child = parts
            match = filtered_data.loc[
                (filtered_data["type_of_eige's_output_cited_agg"] == parent.strip()) &
                (filtered_data["short_labels"] == child.strip())
            ]
            # Add full label for child nodes
            if not match.empty:
                full_label = match["eige's_output_cited"].iloc[0]
                customdata.append([id, full_label, parent])  # Add parent info for hover
            else:
                customdata.append([id, "No Label Found", parent])
        elif len(parts) == 1:  # Parent node
            parent = parts[0]
            customdata.append([id, f"Parent: {parent}", ""])

    # Assign the customdata to the trace
    fig.data[0].customdata = np.array(customdata)

    # Update the hovertemplate to show the full label and parent information
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"  # Full label or parent summary
            "Type: %{customdata[2]}<br>"   # Parent context
            "<extra></extra>"
        )
    )

    # Update layout with specified height
    fig.update_layout(
    height=height,
    title="EIGE Output and its types",
    title_font=dict(family="Verdana", size=20, color=colors[0]),
    font_size=12,)

    return fig

def trend_line_chart(data):
    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Aggregate data by date and type of EIGE's output cited
    agg_df = data.groupby(["date_of_publication", "type_of_eige's_output_cited"]).size().reset_index(name="Count")

    colors = px.colors.qualitative.Pastel

    # Create the line plot
    fig = px.line(
        agg_df,
        x="date_of_publication",
        y="Count",
        color="type_of_eige's_output_cited",
        title="Trends in EIGE's Output Cited Over Time",
        labels={
            "date_of_publication": "Date",
            "Count": "Number of Citations",
            "type_of_eige's_output_cited": "Category"
        },
        markers=True,
        color_discrete_sequence=colors
    )

    # Update the line thickness and marker size
    fig.update_traces(
        line=dict(width=4),
        marker=dict(size=10)
    )

    # Add dropdown for selecting topics to display
    unique_topics = agg_df["type_of_eige's_output_cited"].unique()
    dropdown_buttons = [
        {
            "label": "All Topics",
            "method": "update",
            "args": [{"visible": [True] * len(unique_topics)}, {"title": "Trends in EIGE's Output Cited Over Time"}]
        }
    ]
    for topic in unique_topics:
        dropdown_buttons.append({
            "label": topic,
            "method": "update",
            "args": [
                {"visible": [True if t == topic else False for t in unique_topics]},
                {"title": f"Trend for {topic}"}
            ]
        })

    fig.update_layout(
        updatemenus=[
            {
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
                "active": 0,
                "x": 0.99,
                "xanchor": "left",
                "y": 0.5,
                "yanchor": "top"
            }
        ],
        plot_bgcolor="whitesmoke",
        legend=dict(
            x=0.99,
            y=0.89,
            traceorder="normal",
            font=dict(size=12),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="lightgray",
            borderwidth=1
        ),
        width=1000,
        height=550,
        margin=dict(l=50, r=50, t=70, b=50),
        xaxis=dict(
            title="Date of Publication",
            title_font=dict(size=16),
            tickfont=dict(size=12),
            tickangle=45
        ),
        yaxis=dict(
            title="Number of Citations",
            title_font=dict(size=16),
            tickfont=dict(size=12)
        )
    )

    return fig

def radar_chart(data):
    """
    Create a radar chart from the provided dataset.

    Args:
        data (pd.DataFrame): Preprocessed DataFrame.

    Returns:
        go.Figure: The radar chart as a Plotly Figure object.
    """
    # Rename and preprocess columns
    data = data.rename(columns={
        'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'impact factor of the journal',
        'number_of_citations_(using_google_scholar)': 'number of citations',
        'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'location of the citation',
        'category_of_mention:_1_positive;_0_neutral;_-1_negative': 'sentiment of mention'
    })

    # Ensure 'sentiment of mention' is numeric
    data['sentiment of mention'] = pd.to_numeric(data['sentiment of mention'], errors='coerce')

    # Adjust sentiment mapping
    sentiment_mapping = {-1: 0, 0: 1.5, 1: 3}
    data['sentiment of mention'] = data['sentiment of mention'].map(sentiment_mapping)

    # Relevant categories
    categories = ['impact factor of the journal', 'number of citations', 
                  'location of the citation', 'sentiment of mention']

    # Group by document titles
    data_grouped = data.groupby('name_of_the_document_citing_eige')[categories].mean().reset_index()

    # Truncate document titles for display
    data_grouped['name_truncated'] = data_grouped['name_of_the_document_citing_eige'].apply(lambda x: x[:25])

    # Create radar chart
    fig = go.Figure()
    for _, article in data_grouped.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=article[categories],
            theta=categories,
            fill='toself',
            name=article['name_truncated']
        ))

    # Update layout with custom scale
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 3],
                tickvals=[1, 2, 3],
                ticktext=["Low", "Medium", "High"]
            )
        ),
        title="Radar Chart: Article Comparison",
        showlegend=True
    )

    return fig  # Return the figure object
