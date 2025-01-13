import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def output_type_bar_chart(data):
    # Count occurrences of each type of EIGE output
    topic_counts = data["Type of EIGE output_agg"].value_counts()
    colors = px.colors.qualitative.Pastel

    # Create the bar chart figure
    fig = go.Figure(data=[go.Bar(
        x=topic_counts.index,
        y=topic_counts.values
    )])

    # Update traces with specific styling and hover template
    fig.update_traces(
        name="November 2023",
        width=0.95,
        marker=dict(
            color=topic_counts.values,
            colorscale=colors
        ),
        hovertemplate="Nr. of citations: %{y} <br>Type of output: %{x}"
    )

    # Update layout with custom settings
    fig.update_layout(
        width=800,
        title="Types of EIGE Output",
        title_font=dict(
            family="Verdana",
            size=20,
            color=colors[0]  # Title font color set to the first color of the colorscale
        ),
        font_size=12,
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=False,
        )
    )
    return fig

def sunburst_chart(data, color_palette=px.colors.qualitative.Pastel, height=600):
    # Drop rows with NaN values in the required columns
    filtered_data = data.dropna(subset=['Type of EIGE output_agg', 'Short Labels_output'])
    
    # Create the sunburst chart with two levels (parent/child hierarchy)
    fig = px.sunburst(
        data_frame=filtered_data,
        path=["Type of EIGE output_agg", "Short Labels_output"],  # Parent and child levels
        values=[1] * len(filtered_data),  # Set all values to 1 for hierarchy alignment
        color_discrete_sequence=color_palette
    )

    # Extract IDs and parents from the chart
    ids = fig.data[0].ids
    parents = fig.data[0].parents
    customdata = []

    # Determine which nodes are leaves (child nodes) or non-leaves (parent nodes)
    for id, parent in zip(ids, parents):
        is_leaf = id not in parents  # If `id` is not a parent, it's a leaf
        parts = id.split("/")

        if is_leaf and len(parts) == 2:  # Child node
            parent, child = parts
            match = filtered_data.loc[
                (filtered_data["Type of EIGE output_agg"] == parent.strip()) &
                (filtered_data["Short Labels_output"] == child.strip())
            ]
            # Append full label for leaves
            if not match.empty:
                full_label = match["EIGE's output cited"].iloc[0]
                customdata.append([id, full_label])
            else:
                customdata.append([id, "No Label Found"])
        elif len(parts) == 1:  # Parent node
            parent = parts[0]
            match = filtered_data.loc[filtered_data["Type of EIGE output_agg"] == parent.strip()]
            # Append placeholder or summary for parent nodes
            if not match.empty:
                customdata.append([id, f"Parent: {parent}"])
            else:
                customdata.append([id, ""])

    # Assign the customdata to the trace
    fig.data[0].customdata = np.array(customdata)

    # Update the hovertemplate to show appropriate labels
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[1]}</b>"  # Display the full label for children and summary for parents
            "<extra></extra>"
        )
    )
    # Update layout with specified height
    fig.update_layout(height=height)
    return fig


def trend_line_chart(data):
    # Aggregate data by date and type of EIGE's output cited
    agg_df = data.groupby(["date of publication", "type of EIGE's output cited"]).size().reset_index(name="Count")

    colors = px.colors.qualitative.Pastel

    # Create the line plot
    fig = px.line(
        agg_df,
        x="date of publication",
        y="Count",
        color="type of EIGE's output cited",
        title="Trends in EIGE's Output Cited Over Time",
        labels={
            'date of publication': "Date",
            'Count': 'Number of Citations',
            'type of EIGE\'s output cited': 'Category'
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
    fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": "All Topics",
                        "method": "update",
                        "args": [{"visible": [True] * len(agg_df["type of EIGE's output cited"].unique())}, {"title": "Trends in EIGE's Output Cited Over Time"}]
                    },
                    {
                        "label": "Gender Equality",
                        "method": "update",
                        "args": [{"visible": [True if topic == "Gender Equality" else False for topic in agg_df["type of EIGE's output cited"]]}, {"title": "Gender Equality Trend"}]
                    },
                    {
                        "label": "Labour",
                        "method": "update",
                        "args": [{"visible": [True if topic == "Labour" else False for topic in agg_df["type of EIGE's output cited"]]}, {"title": "Labour Trend"}]
                    },
                    {
                        "label": "Health",
                        "method": "update",
                        "args": [{"visible": [True if topic == "Health" else False for topic in agg_df["type of EIGE's output cited"]]}, {"title": "Health Trend"}]
                    },
                    {
                        "label": "Education",
                        "method": "update",
                        "args": [{"visible": [True if topic == "Education" else False for topic in agg_df["type of EIGE's output cited"]]}, {"title": "Education Trend"}]
                    }
                ],
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
        # Adjust the position of the legend to make space for the dropdown
        legend=dict(
            x=0.99,
            y=0.89,
            traceorder="normal",
            font=dict(size=12),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="lightgray",
            borderwidth=1
        ),
        # Customize the size of the chart
        width=1000,  # Adjust width
        height=550,  # Adjust height
        margin=dict(l=50, r=50, t=70, b=50),  # Add margin for better spacing
        # Customize the axis labels
        xaxis=dict(
            title="Date of Publication",
            title_font=dict(size=16),
            tickfont=dict(size=12),
            tickangle=45  # Rotate x-axis labels for better readability
        ),
        yaxis=dict(
            title="Number of Citations",
            title_font=dict(size=16),
            tickfont=dict(size=12)
        )
    )

    return fig

