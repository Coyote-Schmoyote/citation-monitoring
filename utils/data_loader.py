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
            dfs.append(pd.read_excel(file_data, engine="openpyxl"))
        return pd.concat(dfs, ignore_index=True)

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

    if "date_of_publication" in data.columns:
    # Identify rows where there are three consecutive NaNs in the 'date_of_publication' column
        consecutive_nan = data["date_of_publication"].isna() & data["date_of_publication"].shift().isna()
    # Get the index of the first occurrence of three consecutive NaNs
        nan_start_index = consecutive_nan.idxmax() if consecutive_nan.any() else None
    # If there are three consecutive NaNs, drop rows after the first occurrence
    if nan_start_index is not None:
        data = data.iloc[:nan_start_index] 
    if nan_start_index is not None:
        data = data.iloc[:nan_start_index]

    if "url_of_the_document_citing_eige" in data.columns:
        data.drop("url_of_the_document_citing_eige", axis=1, inplace=True)

    if "type_of_eige's_output_cited" in data.columns:
        replace_values_with_other(data, "type_of_eige's_output_cited")

    if "date_of_publication" in data.columns:
        data["date_of_publication"] = pd.to_datetime(
            data["date_of_publication"], format="mixed", errors="raise", dayfirst=True
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

def load_geospatial_data(file_urls):
    """
    Load and preprocess geospatial data from an Excel file.

    Args:
        file_urls (list): List of URLs to raw Excel files.

    Returns:
        pd.DataFrame: Processed DataFrame with valid latitude and longitude columns.
    """
    print("Fetching data from:", file_urls)  # For debugging
    dfs = []
    
    for url in file_urls:  # Iterate over the list of URLs
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print(f"Error fetching data from {url}. Status code: {response.status_code}")
            continue  # Skip to the next URL if there's an error

        try:
            # Load the Excel file into a DataFrame using the openpyxl engine for .xlsx files
            file_data = BytesIO(response.content)
            data = pd.read_excel(file_data)

            # Rename columns to 'latitude' and 'longitude'
            if 'latitude' not in data.columns or 'longitude' not in data.columns:
                # Assuming columns have different names, replace with your actual column names
                data.rename(columns={'latitude_column_name': 'latitude', 'longitude_column_name': 'longitude'}, inplace=True)
            
            # Ensure that the 'latitude' and 'longitude' columns are valid
            data = data.dropna(subset=['latitude', 'longitude'])
            
            # Append this data to the list of dataframes
            dfs.append(data)

        except Exception as e:
            print(f"Error processing the Excel file from {url}: {e}")
            continue  # Skip this file and move to the next one

    # Concatenate all DataFrames into a single DataFrame
    if dfs:
        combined_data = pd.concat(dfs, ignore_index=True)
        print("Data loaded and processed successfully.")
        return combined_data
    else:
        print("No data loaded. Returning None.")
        return None
