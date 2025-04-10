import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd 

colors = px.colors.qualitative.Pastel

def output_type_bar_chart(data, year):
    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Drop rows where 'date_of_publication' is NaT or NaN
    data = data.dropna(subset=['date_of_publication'])

    # Extract month and year from the date_of_publication column
    data['month_year'] = data['date_of_publication'].dt.strftime('%B %Y')

    # Create a dropdown menu for selecting the month, adding an "All" option
    month_options = ['All'] + data['month_year'].unique().tolist()
    selected_month = st.selectbox("Select a month", month_options)

    # Filter data based on the selected month
    if selected_month == 'All':
        filtered_data = data
    else:
        filtered_data = data[data['month_year'] == selected_month]

    # Use the correct column name
    required_column = "type_of_eige's_output_cited_agg"
    detail_column = "type_of_eige's_output_cited"

    if required_column not in filtered_data.columns or detail_column not in filtered_data.columns:
        raise KeyError(
            f"Required columns not found in the dataset. "
            f"Available columns: {list(filtered_data.columns)}"
        )

    # Drop rows where output type is 'unknown' (case-insensitive)
    filtered_data = filtered_data[~filtered_data[required_column].str.lower().eq('unknown')]

    # Replace 'other' aggregated type with more specific values from the detailed column
    other_mask = filtered_data[required_column].str.lower() == 'other'
    filtered_data.loc[other_mask, required_column] = filtered_data.loc[other_mask, detail_column]

    # Count occurrences of each type of EIGE output
    topic_counts = filtered_data[required_column].value_counts()

    # Create a fixed color map
    unique_outputs = topic_counts.index.tolist()

    if len(unique_outputs) > len(colors):
        raise ValueError(f"Not enough colors in the palette. Found {len(unique_outputs)} unique outputs but only {len(colors)} colors.")

    output_color_map = {output: colors[i] for i, output in enumerate(unique_outputs)}

    # Create the bar chart
    fig = go.Figure()

    for output in unique_outputs:
        output_data = filtered_data[filtered_data[required_column] == output]
        fig.add_trace(go.Bar(
            x=[output] * len(output_data),
            y=[1] * len(output_data),
            name=output,
            marker=dict(color=output_color_map.get(output, 'gray')),
            hovertemplate=(
                "<b>Type of EIGE's Output:</b> %{customdata[0]}<br>" +
                "<b>EIGE's Output Cited:</b> %{customdata[1]}<br>" +
                "%{text}"
            ),
            customdata=output_data[[detail_column, "eige's_output_cited"]].values,
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        barmode='stack',
        title=f"Count of EIGE Outputs by Type {selected_month}, {year}",
        title_font=dict(family="Verdana", size=14),
        font_size=12,
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=False,
            tickmode='linear',
            tick0=1,
            dtick=1
        ),
        template="plotly_white",
        showlegend=False
    )

    return fig

def sunburst_chart(data, months, year, color_palette=px.colors.qualitative.Pastel, height=600):
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
    title=f"Breakdown of EIGE's output cited, {months}, {year}",
    title_font=dict(family="Verdana", size=14),
    font_size=12,)

    return fig

def trend_line_chart(data, months, year, *args):
    """
    Generates a trend line chart based on the given months.

    Args:
        data (pd.DataFrame): The dataset containing citation data.
        *args (int): List of months (e.g., 1 for January, 2 for February, ..., 12 for December).

    Returns:
        plotly.graph_objects.Figure: The trend line chart figure.
    """
    # Ensure no more than 12 months are passed
    if len(args) > 12:
        print("Warning: Only the first 12 months will be used.")
        args = args[:12]

    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Convert "date_of_publication" to datetime format for easier manipulation
    data['date_of_publication'] = pd.to_datetime(data['date_of_publication'])

    # Filter data to include only the months passed as arguments (dynamic number of months)
    data = data[data['date_of_publication'].dt.month.isin(args)]

    # Aggregate data by month and type of EIGE's output cited
    data['month'] = data['date_of_publication'].dt.to_period('M').dt.to_timestamp()
    agg_df = data.groupby(["month", "type_of_eige's_output_cited"]).size().reset_index(name="Count")

    colors = px.colors.qualitative.Pastel

    # Create the line plot
    fig = px.line(
        agg_df,
        x="month",
        y="Count",
        color="type_of_eige's_output_cited",
        title=f"Trends in EIGE's Output Cited {months}, {year}",
        labels={
            "month": "Month",
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

    # Adjust x-axis ticks to show only unique months
    unique_months = agg_df['month'].dt.strftime('%B').unique()
    fig.update_layout(
        xaxis=dict(
            title="Month of Publication",
            title_font=dict(size=16),
            tickfont=dict(size=12),
            tickvals=agg_df['month'].drop_duplicates().sort_values(),
            ticktext=unique_months
        ),
        yaxis=dict(
            title="Number of Citations",
            tickfont=dict(size=12),
            tickmode="linear", 
            dtick=1
        ),
        legend=dict(
            x=0.99,
            y=0.89,
            traceorder="normal",
            font=dict(size=12),
            bordercolor="lightgray",
            borderwidth=1
        ),
        width=1000,
        height=550,
        margin=dict(l=50, r=50, t=70, b=50)
    )

    return fig

def radar_chart(data, months, year):
    # Rename columns for clarity
    data = data.rename(columns={
        'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'impact factor of the journal',
        'number_of_citations_(using_google_scholar)': 'number of citations',
        'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'location of the citation',
        'category_of_mention:_1_positive;_0_neutral;_-1_negative': 'sentiment of mention'
    })

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
    data_grouped = data.groupby('name_of_the_document_citing_eige')[categories].mean().reset_index()

    # Truncate long titles
    data_grouped['name_of_the_document_citing_EIGE_truncated'] = data_grouped['name_of_the_document_citing_eige'].apply(lambda x: x[:45])

    # Create radar chart
    fig = go.Figure()
    for _, article in data_grouped.iterrows():
        # Create a hover template showing original (non-normalized) values
        hovertemplate = f"Article: {article['name_of_the_document_citing_eige']}<br>"

        # Add the original values to the hovertemplate
        hovertemplate += f"Original Sentiment of Mention: {article['sentiment of mention'] / 3:.2f}<br>"  # Display normalized sentiment
        hovertemplate += f"Original Impact Factor of the Journal: {article['impact factor of the journal']}<br>"
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
        title=f"Impact evaluation of articles citing EIGE, {months}, {year}",
        title_font=dict(family="Verdana", size=14),
        font_size=12,
        showlegend=True
    )
    return fig

def citation_stack(data, months, year):
    """
    Generates a stacked bar chart where each bar represents a document citing EIGE.
    Each stack represents a citation count (how many times a document appears in the dataset).

    Parameters:
    data (pandas.DataFrame): DataFrame containing citation information.

    Returns:
    plotly.graph_objects.Figure: The stacked bar chart figure.
    """
    
    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Count how many times each document appears
    document_counts = data['name_of_the_document_citing_eige'].value_counts().reset_index()
    document_counts.columns = ['document', 'citation_count']

    # Create a stacked bar chart
    fig = go.Figure()

    # Loop over each unique document and add a trace for the citations
    for i, row in document_counts.iterrows():
        document_str = str(row['document'])
        truncated_document_name = document_str[:15] + "..." if len(document_str) > 15 else document_str

        # Create the hover text with citation count
        hover_text = f"Document: {document_str}<br>Citation Count: {row['citation_count']}"

        fig.add_trace(go.Bar(
            x=[truncated_document_name],
            y=[row['citation_count']],  # Use the count as the stack height
            name=document_str,
            hoverinfo='text',
            text=hover_text,
            marker=dict(color=px.colors.qualitative.Pastel[i % len(px.colors.qualitative.Pastel)]),
            showlegend=False
        ))

      # Update layout
    fig.update_layout(
        barmode='stack',
        title=f"Number of EIGE citations per article, {months} {year}.",
        title_font=dict(family="Verdana", size=14),
        font_size=12,
        xaxis_title="Document Name",
        yaxis_title="Number of Citations",
        xaxis_tickangle=-45,
        yaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1  # Ensure y-axis ticks in intervals of 1
        ),
        template="plotly_white",
        showlegend=False
    )

    return fig

def scatterplot(data):    

    # Ensure the necessary columns are present
    required_columns = [
        'date_of_publication', 'ranking/weight', 
        'name_of_the_document_citing_eige', 
        'name_of_the_author/organisation_citing_eige', 
        'name_of_the_institution_citing_eige', 
        'name_of_the_journal_citing_eige'
    ]
    
    for col in required_columns:
        if col not in data.columns:
            raise KeyError(f"The '{col}' column is missing from the dataset.")

    # Step 1: Convert 'date_of_publication' to datetime if it's not already
    data['date_of_publication'] = pd.to_datetime(data['date_of_publication'], errors='coerce')

    # Step 2: Handle missing or invalid data in the 'ranking/weight' column
    data['ranking/weight'] = pd.to_numeric(data['ranking/weight'], errors='coerce')

    # Step 3: Filter out rows with missing values in critical columns
    data = data.dropna(subset=['date_of_publication', 'ranking/weight'])

    # Step 4: Create scatter plot with hover data
    fig = px.scatter(data,
                     x='date_of_publication', 
                     y='ranking/weight', 
                     title="Citations Scatter Plot by Date and Rating",
                     labels={'date_of_publication': 'Date of Publication', 'ranking/weight': 'Overall Rating'})

    # Step 5: Show the plot
    fig.show()

    return fig

def annual_bar(data, year):
    # Normalize column names for consistent access
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Drop rows where 'date_of_publication' is NaT or NaN
    data = data.dropna(subset=['date_of_publication'])

    # Extract quarter and year
    data['quarter'] = data['date_of_publication'].dt.to_period('Q').astype(str)

    # Define quarter order for sorting
    quarter_order = [f'Q1 {year}', f'Q2 {year}', f'Q3 {year}', f'Q4 {year}']

    # Create a dropdown menu for selecting the quarter, adding an "All" option
    quarter_options = ['All'] + sorted(data['quarter'].unique().tolist(), key=lambda x: quarter_order.index(x) if x in quarter_order else len(quarter_order))
    selected_quarter = st.selectbox("Select a quarter", quarter_options)

    # Filter data based on the selected quarter
    if selected_quarter == 'All':
        filtered_data = data
    else:
        filtered_data = data[data['quarter'] == selected_quarter]

    # Use the correct column name
    required_column = "type_of_eige's_output_cited_agg"
    if required_column not in filtered_data.columns:
        raise KeyError(
            f"Column '{required_column}' not found in the dataset. "
            f"Available columns: {list(filtered_data.columns)}"
        )

    # Count occurrences of each type of EIGE output per quarter
    topic_counts = filtered_data.groupby(['quarter', required_column]).size().unstack(fill_value=0)

    # Create a fixed color map based on the type of output (using a predefined color palette)
    unique_outputs = topic_counts.columns.tolist()

    # Ensure there are enough colors
    if len(unique_outputs) > len(colors):
        raise ValueError(f"Not enough colors in the palette. Found {len(unique_outputs)} unique outputs but only {len(colors)} colors.")

    output_color_map = {output: colors[i] for i, output in enumerate(unique_outputs)}

    # Create the bar chart
    fig = go.Figure()

    for output in unique_outputs:
        fig.add_trace(go.Bar(
            x=topic_counts.index,
            y=topic_counts[output],
            name=output,
            marker=dict(color=output_color_map[output]),
            hovertemplate="<b>Quarter:</b> %{x}<br><b>Type of EIGE's Output:</b> %{customdata[0]}<br><b>Count:</b> %{y}",
            customdata=[[output] * len(topic_counts.index)]
        ))

    # Update layout to show stacked bar chart
    fig.update_layout(
        barmode='stack',
        title=f"Count of EIGE Outputs by Type per Quarter, {year}",
        title_font=dict(family="Verdana", size=14),
        font_size=12,
        xaxis=dict(title="Quarter", showgrid=False),
        yaxis=dict(
            title="Count",
            showgrid=False,
            tickmode='linear',
            tick0=1,
            dtick=1
        ),
        template="plotly_white"
    )

    return fig
