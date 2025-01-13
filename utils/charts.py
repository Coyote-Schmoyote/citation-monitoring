import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
    colors = px.colors.qualitative.Pastel

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
        title="Types of EIGE Output",
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

    # Customize hover templates
    fig.update_traces(
        hovertemplate="<b>%{id}</b><br>Type: %{parent}<br>Label: %{label}<extra></extra>"
    )

    # Update layout with specified height
    fig.update_layout(height=height)
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
