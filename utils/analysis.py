import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

# Step 1: Drop columns and handle missing data
def drop_columns_and_handle_missing(data):
    columns_to_drop = [
        'date_of_publication',
        'name_of_the_author/organisation_citing_eige',
        "year_of_publication_of_eige's_output_cited",
        'source',
        'short_labels',
        'month',
        'name_of_the_document_citing_eige'
    ]
    data = data.drop(columns=columns_to_drop, errors='ignore')
    data = data.dropna()  # Remove rows with missing values
    return data

# Step 2: Encode categorical columns
def encode_categorical_columns(data, categorical_columns):
    # Apply One-Hot Encoding to the specified categorical columns
    data = pd.get_dummies(data, columns=categorical_columns)

    # If there are additional categorical columns to encode, apply Label Encoding
    # (This depends on your dataset, you might want to adjust it based on the columns you want to encode)
    label_columns = [
        "name_of_the_institution", 
        "number_of_mentions_in_social_media_using_altmetric"
    ]
    
    le = LabelEncoder()
    for column in label_columns:
        data[column] = data[column].astype(str)
        data[column] = le.fit_transform(data[column])

    return data

# Step 3: Normalize the data
def normalize_data(data, target_column):
    scaler = MinMaxScaler()
    
    # Normalize the target column
    data[target_column] = scaler.fit_transform(data[[target_column]])
    
    # Normalize other numerical features if necessary
    numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns
    data[numerical_columns] = scaler.fit_transform(data[numerical_columns])
    
    return data

# Step 4: Combine categorical columns and apply PCA for dimensionality reduction
def combine_categorical_and_pca(data, categorical_columns):
    # Apply One-Hot Encoding to the categorical columns
    data_encoded = pd.get_dummies(data, columns=categorical_columns)
    
    # Apply PCA to reduce dimensions to 1 for visualization
    pca = PCA(n_components=1)
    pca_result = pca.fit_transform(data_encoded)
    
    return pca_result

# Step 5: Visualize the scatter plot of Normalized Weights vs Combined Categorical Features
def visualize_combined_scatter(data, target_column, pca_result):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plotting the normalized weights vs PCA result on the x-axis
    scatter = ax.scatter(pca_result, data[target_column], c=data[target_column], cmap='viridis', alpha=0.7)
    
    ax.set_xlabel('Combination of Categorical Features (PCA)')
    ax.set_ylabel(f'Normalized {target_column}')
    ax.set_title(f'Scatterplot of Normalized Weights vs Combined Categorical Features')
    fig.colorbar(scatter, ax=ax, label=f'Normalized {target_column}')
    
    # Display using Streamlit
    st.pyplot(fig)

# Step 6: Final function to run all steps and return results
def normalize_and_analyze(data, target_column, categorical_columns):
    # Drop columns and handle missing data
    data = drop_columns_and_handle_missing(data)
    
    # Check if the target column exists in the dataset
    if target_column not in data.columns:
        raise ValueError(f"Target column '{target_column}' not found in the dataset.")
    
    # Check if the categorical columns exist in the dataset
    for column in categorical_columns:
        if column not in data.columns:
            raise ValueError(f"Categorical column '{column}' not found in the dataset.")
    
    # Encode categorical columns
    data = encode_categorical_columns(data, categorical_columns)
    
    # Normalize data
    data = normalize_data(data, target_column)
    
    # Combine categorical columns and apply PCA for dimensionality reduction
    pca_result = combine_categorical_and_pca(data, categorical_columns)
    
    # Visualize the combined scatter plot
    visualize_combined_scatter(data, target_column, pca_result)
    
    # Return the analysis results with columns that exist in the dataset
    st.write("Columns after processing:", data.columns)
    
    # Adjust return to actual columns after processing
    return data  # Return all columns, or you can select specific ones that make sense

