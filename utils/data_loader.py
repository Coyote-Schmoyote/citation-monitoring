import pandas as pd
import streamlit as st
from io import BytesIO
import requests


@st.cache_data
def get_data(file_urls):
    # accept single URL or list
    if isinstance(file_urls, str):
        file_urls = [file_urls]

    if not isinstance(file_urls, list) or len(file_urls) == 0:
        raise ValueError("file_urls must be a non-empty list or a single URL.")

    dfs = []

    for url in file_urls:
        response = requests.get(url)
        response.raise_for_status()  # fails loudly if GitHub returns HTML / 404

        file_bytes = BytesIO(response.content)

        df = pd.read_excel(file_bytes, engine="openpyxl")
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)

    # normalize columns
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
            data = data.iloc[:nan_mask.idxmax()]

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
