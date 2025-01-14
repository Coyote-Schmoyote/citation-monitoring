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
    # Print the columns to debug the issue
    print(f"Columns in data: {data.columns}")

    # Rename the columns for clarity
    data = data.rename(columns={
        'impact factor of the journal: 1 respectable; 2 strong; 3 very strong (using free version of scopus)': 'impact factor of the journal',
        'number of citations (using google scholar)': 'number of citations',
        'location of the citation: 3 body of the article; 2 introduction; 1 bibliography/reference': 'location of the citation',
        'category of mention: 1 positive; 0 neutral; -1 negative': 'sentiment of mention'
    })

    # After renaming, check the columns again
    print(f"Columns after renaming: {data.columns}")

    # Check if the 'sentiment of mention' column exists
    if 'sentiment of mention' not in data.columns:
        st.error("'sentiment of mention' column not found in the data!")
        return

    # Inspect the unique values in 'sentiment of mention' column
    print(f"Unique values in 'sentiment of mention' column: {data['sentiment of mention'].unique()}")

    # Ensure 'sentiment of mention' is numeric, convert errors to NaN
    data['sentiment of mention'] = pd.to_numeric(data['sentiment of mention'], errors='coerce')

    # Check if the conversion was successful
    print(f"Unique values after conversion: {data['sentiment of mention'].unique()}")

    # Adjust the sentiment of mention values:
    sentiment_mapping = {-1: 0, 0: 1.5, 1: 3}
    data['sentiment of mention'] = data['sentiment of mention'].map(sentiment_mapping)

    # Check if the mapping worked correctly
    print(f"Unique values after mapping: {data['sentiment of mention'].unique()}")

    # List of renamed categories (columns) we want to include in the radar chart
    categories = ['impact factor of the journal', 'number of citations', 
                  'location of the citation', 'sentiment of mention']

    # Group by document titles and calculate the average of the numerical columns
    data_grouped = data.groupby('name of the document citing EIGE')[categories].mean().reset_index()

    # Truncate the article titles to a maximum of 25 characters
    data_grouped['name_of_the_document_citing_EIGE_truncated'] = data_grouped['name of the document citing EIGE'].apply(lambda x: x[:25])

    # Initialize the figure
    fig = go.Figure()

    # Add data for each article (now averaged)
    for i, article in data_grouped.iterrows():
        # Create a hover template based on the category
        hovertemplate = f"Article: {article['name of the document citing EIGE']}<br>"

        for category in categories:
            if category == 'impact factor of the journal':
                hovertemplate += f"Impact Factor: {article[category]}<br>"
            elif category == 'number of citations':
                hovertemplate += f"Number of Citations: {article[category]}<br>"
            elif category == 'location of the citation':
                hovertemplate += f"Location of Citation: {article[category]}<br>"
            elif category == 'sentiment of mention':
                hovertemplate += f"Sentiment of Mention: {article[category]}<br>"

        hovertemplate += "<extra></extra>"

        # Create the radar chart trace for the article
        trace = go.Scatterpolar(
            r=article[categories],
            theta=categories,
            fill='toself',
            name=article['name_of_the_document_citing_EIGE_truncated'],  # Truncated title in legend
            hovertemplate=hovertemplate  # Use the constructed hovertemplate
        )
        
        fig.add_trace(trace)

    # Update layout to ensure the chart appears properly
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3],  # Adjusting range to show 0, 1, 2, 3
                tickvals=[0, 1, 2, 3],  # Set tick positions at 0, 1, 2, 3
                ticktext=["None", "Low", "Medium", "High"]  # Custom labels for the ticks
            ),
        ),
        title="Radar Chart: Article Comparison by Categories",
        showlegend=True,
        hovermode="closest"
    )

    # Show the chart in Streamlit
    st.plotly_chart(fig)

# Example usage:
# Assuming 'data' is your dataset
# create_radar_chart(data)  # Uncomment and provide 'data' when running in Streamlit
