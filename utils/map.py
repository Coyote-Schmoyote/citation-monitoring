import streamlit as st
import pandas as pd 
from geopy.geocoders import Nominatim
from utils.data_loader import get_data

#load data
# File URLs (GitHub raw URLs)
file_urls = ["https://github.com/Coyote-Schmoyote/citation-monitoring/raw/refs/heads/main/data/Q12024_13012025.xlsx"]

# Fetch data using the modified get_data function
data = get_data(file_urls)
# Define a function to get latitude and longitude based on university name
def get_lat_lon(university_name):
    try:
        # Use geopy to get the location based on university name
        location = geolocator.geocode(university_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None  # If no location found
    except Exception as e:
        print(f"Error: {e}")
        return None, None  # Return None in case of error

# Add latitude and longitude columns
data[['latitude', 'longitude']] = data['name_of_the_institution_citing_EIGE'].apply(lambda x: pd.Series(get_lat_lon(x)))

# Display the updated DataFrame
st.write("University Data with Coordinates:")
st.dataframe(data)

# Filter out rows with missing coordinates (latitude or longitude)
data_with_coordinates = data.dropna(subset=['latitude', 'longitude'])

return data_with_coordinates

