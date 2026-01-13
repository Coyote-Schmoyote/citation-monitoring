import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

colors = px.colors.qualitative.Pastel

# -----------------------------
# 2. bar chart of total citations
# -----------------------------
def total_citations_trend(
    data,
    months=None,
    year=None,
    *args,
    mode="documents"  # "documents" | "avg_citations"
):
    """
    Trend line per month.
    mode="documents"      → number of documents citing EIGE
    mode="avg_citations"  → average Google Scholar citations per article
    """

    data = data.copy()
    date_col = 'date_of_publication'
    doc_col = 'name_of_the_document_citing_eige'
    citation_col = 'number_of_citations_(using_google_scholar)'

    # Required columns
    required = [date_col, doc_col]
    if mode == "avg_citations":
        required.append(citation_col)

    if not all(col in data.columns for col in required):
        return px.line(title="Required columns missing")

    # Types
    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
    data = data.dropna(subset=[date_col, doc_col])

    if mode == "avg_citations":
        data[citation_col] = pd.to_numeric(data[citation_col], errors='coerce')
        data = data.dropna(subset=[citation_col])

    # Filter months
    if args:
        data = data[data[date_col].dt.month.isin(args)]

    data['month_str'] = data[date_col].dt.strftime('%B')

    # Aggregate
    if mode == "documents":
        agg = (
            data.groupby('month_str')[doc_col]
            .nunique()
            .reset_index(name='value')
        )
        y_title = "Number of documents"
        title = f"Number of Documents Citing EIGE ({year})"

    else:  # avg_citations
        agg = (
            data.groupby(['month_str', doc_col])[citation_col]
            .mean()
            .reset_index()
            .groupby('month_str')[citation_col]
            .mean()
            .reset_index(name='value')
        )
        y_title = "Average citations per article"
        title = f"Average Google Scholar Citations per Article ({year})"

    # Month ordering
    if months and isinstance(months, str):
        month_names = [m.strip() for m in months.split(' - ')]
    else:
        month_names = sorted(
            agg['month_str'].unique(),
            key=lambda m: pd.to_datetime(m, format='%B').month
        )

    agg['month_order'] = agg['month_str'].map(
        {m: i for i, m in enumerate(month_names)}
    )
    agg = agg.sort_values('month_order')

    # Plot
    fig = px.line(
        agg,
        x='month_str',
        y='value',
        markers=True,
        title=title
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title=y_title,
        yaxis=dict(tickformat=",d")  # integers only
    )

    # No labels on points
    fig.update_traces(text=None)

    return fig
# -----------------------------
# Output Type Bar Chart
# -----------------------------
def output_type_bar_chart(data, year):
    data = data.copy()
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")

    if "date_of_publication" not in data.columns:
        return go.Figure().update_layout(
            title="No date column found",
            template="plotly_white"
        )

    # Keep NA dates, label them explicitly
    data["month_year"] = data["date_of_publication"].dt.strftime("%B %Y")
    data["month_year"] = data["month_year"].fillna("NA")

    agg_col = "type_of_eige's_output_cited_agg"
    detail_col = "type_of_eige's_output_cited"

    if agg_col not in data.columns or detail_col not in data.columns:
        return go.Figure().update_layout(
            title="Required columns missing",
            template="plotly_white"
        )

    # Keep NA output types too
    data[agg_col] = data[agg_col].fillna("NA")

    # Drop only explicit 'unknown', not NA
    data = data[~data[agg_col].str.lower().eq("unknown")]

    # Resolve "other" → detailed label where available
    other_mask = data[agg_col].str.lower() == "other"
    data.loc[other_mask, agg_col] = (
        data.loc[other_mask, detail_col]
        .fillna("Other (unspecified)")
    )

    topic_counts = (
        data[agg_col]
        .value_counts()
        .rename_axis("output_type")
        .reset_index(name="count")
    )

    base_palette = px.colors.qualitative.Safe
    extended_palette = (
        base_palette * ((len(topic_counts) // len(base_palette)) + 1)
    )[:len(topic_counts)]

    color_map = dict(zip(topic_counts["output_type"], extended_palette))

    fig = px.bar(
        topic_counts,
        x="output_type",
        y="count",
        color="output_type",
        color_discrete_map=color_map,
        labels={
            "output_type": "EIGE output",
            "count": "Number of mentions"
        },
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title=None,
        yaxis_title="Number of mentions",
        legend_title_text="EIGE output"
    )

    return fig

# -----------------------------
# Sunburst Chart
# -----------------------------
def sunburst_chart(data, months, year, color_palette=px.colors.qualitative.Pastel, height=600):
    data = data.copy()
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
    required_columns = ["type_of_eige's_output_cited_agg", "short_labels"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return go.Figure().update_layout(title=f"Missing columns: {missing_columns}", template="plotly_white")

    filtered_data = data.dropna(subset=required_columns)
    fig = px.sunburst(
        data_frame=filtered_data,
        path=["type_of_eige's_output_cited_agg", "short_labels"],
        values=[1]*len(filtered_data),
        color_discrete_sequence=color_palette
    )
    fig.update_layout(height=height, title=f"EIGE output breakdown {months}, {year}", template="plotly_white")
    return fig

# -----------------------------
# Trend Line Chart
# -----------------------------

def trend_line_chart(data, months=None, year=None, *args):
    """
    Stacked bar chart: total citations per EIGE output type per month.
    Bars are stacked, but no numbers displayed inside.
    """
    if len(args) > 12:
        args = args[:12]

    data = data.copy()
    date_col = 'date_of_publication'
    type_col = "type_of_eige's_output_cited"
    citation_col = 'number_of_citations_(using_google_scholar)'

    for col in [date_col, type_col, citation_col]:
        if col not in data.columns:
            return px.bar(title="Required columns missing")

    # Ensure proper types
    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
    data[citation_col] = pd.to_numeric(data[citation_col], errors='coerce')
    data = data.dropna(subset=[date_col, type_col, citation_col])

    # Filter by numeric months if provided
    if args:
        data = data[data[date_col].dt.month.isin(args)]

    # Month string
    data['month_str'] = data[date_col].dt.strftime('%B')

    # Aggregate citations per month and type
    agg_df = data.groupby(['month_str', type_col])[citation_col].sum().reset_index()
    agg_df.rename(columns={citation_col: 'total_citations'}, inplace=True)

    # Determine month order
    if months and isinstance(months, str):
        month_names = [m.strip() for m in months.split(' - ')]
    else:
        month_names = sorted(agg_df['month_str'].unique(), key=lambda m: pd.to_datetime(m, format='%B'))

    month_mapping = {m: i for i, m in enumerate(month_names, 1)}
    agg_df['month_order'] = agg_df['month_str'].map(lambda m: month_mapping.get(m, 99))
    agg_df = agg_df.sort_values('month_order')

    # Stacked bar chart (without text labels)
    fig = px.bar(
        agg_df,
        x='month_str',
        y='total_citations',
        color=type_col,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        template="plotly_white",
        barmode='stack',  # stacked bars
        title=f"Monthly Citations by EIGE Output Type ({year})",
        xaxis_title="Month",
        yaxis_title="Citations",
        legend_title="Output Type"
    )
    return fig


# -----------------------------
# Radar Chart (ordered by weight)
# -----------------------------
def radar_chart(data, months, year):
    data = data.copy()
    
    # rename columns for readability
    rename_map = {
        'impact_factor_of_the_journal:_1_respectable;_2_strong;_3_very_strong_(using_free_version_of_scopus)': 'impact factor of the journal',
        'number_of_citations_(using_google_scholar)': 'number of citations',
        'location_of_the_citation:_3_body_of_the_article;_2_introduction;_1_bibliography/reference': 'location of the citation',
        'category_of_mention:_1_positive;_0_neutral;_-1_negative': 'sentiment of mention'
    }
    data = data.rename(columns=rename_map)

    # convert columns to numeric
    columns_to_convert = ['impact factor of the journal', 'number of citations', 'location of the citation', 'sentiment of mention']
    for col in columns_to_convert:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    data[columns_to_convert] = data[columns_to_convert].fillna(0)

    # remap sentiment
    if 'sentiment of mention' in data.columns:
        sentiment_mapping = {-1:0, 0:1.5, 1:3}
        data['sentiment of mention'] = data['sentiment of mention'].map(sentiment_mapping)

    categories = [c for c in columns_to_convert if c in data.columns]
    if 'name_of_the_document_citing_eige' not in data.columns or 'ranking/weight' not in data.columns:
        return go.Figure().update_layout(title="Missing columns", template="plotly_white")

    # group by document and compute mean metrics
    data_grouped = data.groupby(['name_of_the_document_citing_eige', 'ranking/weight'])[categories].mean().reset_index()
    
    # sort by weight descending
    data_grouped = data_grouped.sort_values(by='ranking/weight', ascending=False)

    # build figure
    fig = go.Figure()
    for _, article in data_grouped.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=article[categories],
            theta=categories,
            fill='toself',
            name=article['name_of_the_document_citing_eige'][:45]
        ))

    fig.update_layout(
        template="plotly_white",
        polar=dict(radialaxis=dict(visible=True)),
        title=f"Impact Evaluation (Radar) – {year}"
    )
    return fig

# -----------------------------
# Annual Bar Chart
# -----------------------------
def annual_bar(data, year):
    """
    Plot annual bar chart of EIGE outputs cited.
    Expects 'type_of_eige\'s_output_cited' column in data.
    """
    if "type_of_eige's_output_cited" not in data.columns:
        raise KeyError(f"'type_of_eige\'s_output_cited' column missing. Available: {list(data.columns)}")
    
    # Count mentions per type
    counts = data["type_of_eige's_output_cited"].value_counts().reset_index()
    counts.columns = ["type_of_output", "count"]
    
    fig = px.bar(counts, x="type_of_output", y="count",
                 color="type_of_output",
                 labels={"count": f"Mentions in {year}", "type_of_output": "EIGE Output"},
                 title=f"Annual mentions of EIGE outputs in {year}")
    fig.update_layout(showlegend=False)
    return fig

# -----------------------------
# Citation Stacked Bar
# -----------------------------
def citation_stack(data, doc_col='name_of_the_document_citing_eige', months='', year=''):
    if data.empty:
        return go.Figure().update_layout(title="No data available", template="plotly_white")

    data = data.copy()
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
    doc_col = doc_col.lower().replace(' ', '_')
    if doc_col not in data.columns:
        return go.Figure().update_layout(title=f"Column '{doc_col}' not found", template="plotly_white")

    df_counts = data.groupby(doc_col).size().reset_index(name='count')
    fig = go.Figure()
    for i, row in df_counts.iterrows():
        doc_name = str(row[doc_col])
        truncated_name = doc_name[:15] + "..." if len(doc_name) > 15 else doc_name
        hover_text = f"Document: {doc_name}<br>Mentions: {row['count']}"
        fig.add_trace(go.Bar(
            x=[truncated_name],
            y=[row['count']],
            name=doc_name,
            hoverinfo='text',
            text=hover_text,
            marker=dict(color=colors[i % len(colors)])
        ))
    fig.update_layout(barmode='stack', xaxis_title="Article", yaxis_title="Mentions", template="plotly_white", showlegend=False)
    return fig

