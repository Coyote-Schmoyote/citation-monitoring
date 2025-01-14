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
    # Rename columns for clarity
    data = data.rename(columns={
        'impact factor of the journal: 1 respectable; 2 strong; 3 very strong (using free version of scopus)': 'impact factor of the journal',
        'number of citations (using google scholar)': 'number of citations',
        'location of the citation: 3 body of the article; 2 introduction; 1 bibliography/reference': 'location of the citation',
        'category of mention: 1 positive; 0 neutral; -1 negative': 'sentiment of mention'
    })

    # Save the original values in new columns
    data['original_sentiment_of_mention'] = data['sentiment of mention']

    # Ensure numeric conversion and clean data
    columns_to_convert = ['impact factor of the journal', 'number of citations', 'location of the citation', 'sentiment of mention']

    for col in columns_to_convert:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # Fill NaN values with 0 in key columns
    data[columns_to_convert] = data[columns_to_convert].fillna(0)

    # Map sentiment values (for normalized values)
    sentiment_mapping = {-1: 0, 0: 1.5, 1: 3}
    data['sentiment of mention'] = data['sentiment of mention'].map(sentiment_mapping)

    # Define categories
    categories = ['impact factor of the journal', 'number of citations',
                  'location of the citation', 'sentiment of mention']

    # Group by document titles and calculate averages
    data_grouped = data.groupby('name of the document citing EIGE')[categories].mean().reset_index()

    # Truncate long titles
    data_grouped['name_of_the_document_citing_EIGE_truncated'] = data_grouped['name of the document citing EIGE'].apply(lambda x: x[:45])

    # Create radar chart
    fig = go.Figure()
    for _, article in data_grouped.iterrows():
        # Create a hover template showing original (non-normalized) values
        hovertemplate = f"Article: {article['name of the document citing EIGE']}<br>"

        # Add the original values to the hovertemplate
        hovertemplate += f"Original Sentiment of Mention: {article['sentiment of mention']}<br>"
        hovertemplate += f"Original Impact Factor: {article['impact factor of the journal']}<br>"
        hovertemplate += f"Original Number of Citations: {article['number of citations']}<br>"
        hovertemplate += f"Original Location of Citation: {article['location of the citation']}<br>"

        hovertemplate += "<extra></extra>"  # Prevent extra data from appearing on hover

        # Add radar chart trace for the article
        fig.add_trace(go.Scatterpolar(
            r=article[categories],
            theta=categories,
            fill='toself',
            name=article['name_of_the_document_citing_EIGE_truncated'],
            hovertemplate=hovertemplate  # Add the customized hovertemplate
        ))

    fig.update_layout(
            polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 3],  # Set range to match "Low", "Medium", "High"
                tickvals=[1, 2, 3],  # Tick positions
                ticktext=["Low", "Medium", "High"]  # Custom tick labels
            )
        ),
        title="Radar Chart: Article Comparison by Categories",
        showlegend=True
    )
    return fig


