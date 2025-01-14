import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from io import BytesIO
import requests

@st.cache_data
def get_data(file_urls):
    """
    Load and preprocess data from multiple source files hosted on GitHub.

    Args:
        file_urls (list): List of URLs to raw GitHub files.

    Returns:
        pd.DataFrame: Combined and processed DataFrame.
    """
    def load_data(urls):
        """Load data from multiple URLs into a single DataFrame."""
        dfs = []
        for url in urls:
            response = requests.get(url)
            file_data = BytesIO(response.content)
            dfs.append(pd.read_excel(file_data))
        return pd.concat(dfs, ignore_index=True)

    def drop_after_consecutive_nans(df, column):
        """Drop rows after two consecutive NaNs in a specific column."""
        consecutive_nan = df[column].isna() & df[column].shift().isna()
        nan_start_index = consecutive_nan.idxmax() if consecutive_nan.any() else None
        return df.iloc[:nan_start_index] if nan_start_index is not None else df

    def replace_values_with_other(df, column):
        """Replace values occurring once or marked as 'Unclear' with 'Other'."""
        value_counts = df[column].value_counts()
        values_to_replace = value_counts[
            (value_counts <= 1) | (value_counts.index == "Unclear")
        ].index
        df[f"{column}_agg"] = df[column].replace(values_to_replace, "Other")
        return values_to_replace

    # Load data from all source files
    data = load_data(file_urls)

    # Normalize column names for consistency
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Apply transformations
    if "name_of_the_document_citing_eige" in data.columns:
        data = drop_after_consecutive_nans(data, "name_of_the_document_citing_eige")

    if "url_of_the_document_citing_eige" in data.columns:
        data.drop("url_of_the_document_citing_eige", axis=1, inplace=True)

    if "type_of_eige's_output_cited" in data.columns:
        replace_values_with_other(data, "type_of_eige's_output_cited")

    if "date_of_publication" in data.columns:
        data["date_of_publication"] = pd.to_datetime(
            data["date_of_publication"], format="%d.%m.%Y", errors="coerce"
        )

    columns_to_fill = ["type_of_eige's_output_cited_agg", "type_of_eige's_output_cited"]
    for col in columns_to_fill:
        if col in data.columns:
            data[col] = data[col].fillna("Unknown")

    if "eige's_output_cited" in data.columns:
        data["short_labels"] = data["eige's_output_cited"].apply(
            lambda x: (x[:16] + '...') if isinstance(x, str) and len(x) > 15 else x
        )

    # Debugging step: Print column names to confirm presence of expected columns
    print("Columns in data:", data.columns)
    return data

def load_geospatial_data(file_url):
    """
    Load and preprocess geospatial data from an Excel file.

    Args:
        file_url (str): URL to the raw Excel file.

    Returns:
        pd.DataFrame: Processed DataFrame with valid latitude and longitude columns.
    """

    # Fetch the file from the URL
    print("Fetching data from:", file_url)  # For debugging
    response = requests.get(file_url)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Error fetching data from {file_url}. Status code: {response.status_code}")
        return None

    try:
        # Load the Excel file into a DataFrame using the openpyxl engine for .xlsx files
        file_data = BytesIO(response.content)
        data = pd.read_excel(file_data, engine='openpyxl')  # Specify engine

        # Rename columns to 'latitude' and 'longitude'
        if 'latitude' not in data.columns or 'longitude' not in data.columns:
            # Assuming columns have different names, replace with your actual column names
            data.rename(columns={'latitude_column_name': 'latitude', 'longitude_column_name': 'longitude'}, inplace=True)
        
        # Ensure that the 'latitude' and 'longitude' columns are valid
        data = data.dropna(subset=['latitude', 'longitude'])

        print("Data loaded and processed successfully.")
        return data

    except Exception as e:
        print(f"Error processing the Excel file: {e}")
        return None
