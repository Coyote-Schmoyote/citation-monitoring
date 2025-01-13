import pandas as pd
from pathlib import Path
import streamlit as st

@st.cache_data
def get_data(file_paths):
    """
    Load and preprocess data from multiple source files.

    Args:
        file_paths (list): List of file paths to CSV files.

    Returns:
        pd.DataFrame: Combined and processed DataFrame.
    """
    def load_data(files):
        """Load data from multiple files into a single DataFrame."""
        dfs = [pd.read_excel(file) for file in files]
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
        # Replace values with 'Other' and create the aggregated column
        df[f"{column}_agg"] = df[column].replace(values_to_replace, "Other")
        return values_to_replace  # Return values_to_replace for further use if needed

    # Load data from all source files
    data = load_data(file_paths)

    # Apply transformations
    if "name of the document citing EIGE" in data.columns:
        data = drop_after_consecutive_nans(data, "name of the document citing EIGE")

    if "URL of the document citing EIGE" in data.columns:
        data.drop("URL of the document citing EIGE", axis=1, inplace=True)

    if "type of EIGE's output cited" in data.columns:
        # Replace values in "type of EIGE's output cited" and create "type of EIGE output_agg"
        values_to_replace = replace_values_with_other(data, "type of EIGE's output cited")

    # Check if the 'Type of EIGE output_agg' column exists after the transformation
    if 'type of EIGE\'s output cited_agg' in data.columns:
        print("Successfully created 'Type of EIGE output_agg' column.")

    if "date of publication" in data.columns:
        data["date of publication"] = pd.to_datetime(
            data["date of publication"], format="%d.%m.%Y", errors="coerce"
        )

    columns_to_fill = ["type of EIGE's output cited_agg", "type of EIGE's output cited"]
    for col in columns_to_fill:
        if col in data.columns:
            data[col] = data[col].fillna("Unknown")

    if "EIGE output referenced" in data.columns:
        data["Short Labels"] = data["EIGE output referenced"].apply(
            lambda x: (x[:16] + '...') if isinstance(x, str) and len(x) > 15 else x
        )

    return data
