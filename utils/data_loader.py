import pandas as pd
import streamlit as st


@st.cache_data
def get_data(filepath):
    data = pd.read_excel(filepath, engine="openpyxl")

    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    def replace_values_with_other(df, column):
        counts = df[column].value_counts()
        to_replace = counts[(counts <= 1) | (counts.index == "Unclear")].index
        df[f"{column}_agg"] = df[column].replace(to_replace, "Other")

    if "date_of_publication" in data.columns:
        nan_mask = (
            data["date_of_publication"].isna()
            & data["date_of_publication"].shift().isna()
        )
        if nan_mask.any():
            cutoff = nan_mask.idxmax()
            data = data.iloc[:cutoff]

    if "url_of_the_document_citing_eige" in data.columns:
        data.drop(columns=["url_of_the_document_citing_eige"], inplace=True)

    if "type_of_eige's_output_cited" in data.columns:
        replace_values_with_other(data, "type_of_eige's_output_cited")

    if "date_of_publication" in data.columns:
        data["date_of_publication"] = pd.to_datetime(
            data["date_of_publication"],
            format="mixed",
            errors="coerce",
            dayfirst=True
        )

    for col in [
        "type_of_eige's_output_cited",
        "type_of_eige's_output_cited_agg"
    ]:
        if col in data.columns:
            data[col] = data[col].fillna("Unknown")

    if "eige's_output_cited" in data.columns:
        data["short_labels"] = data["eige's_output_cited"].apply(
            lambda x: x[:16] + "..." if isinstance(x, str) and len(x) > 15 else x
        )

    return data


@st.cache_data
def load_geospatial_data(filepath):
    data = pd.read_excel(filepath, engine="openpyxl")

    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    if not {"latitude", "longitude"}.issubset(data.columns):
        raise ValueError("Latitude and longitude columns not found.")

    data = data.dropna(subset=["latitude", "longitude"])

    return data
