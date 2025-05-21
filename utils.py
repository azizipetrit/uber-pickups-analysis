import pandas as pd
import streamlit as st

# Constants
DATE_COLUMN = "date/time"
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
          'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    """
    Load and preprocess Uber pickup data
    
    Parameters:
    nrows (int): Number of rows to load
    
    Returns:
    pandas.DataFrame: Processed DataFrame
    """
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    
    # Add day of week and hour columns for analysis
    data['day_of_week'] = data[DATE_COLUMN].dt.day_name()
    data['hour'] = data[DATE_COLUMN].dt.hour
    
    return data

def get_day_order():
    """Return days of week in correct order"""
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
