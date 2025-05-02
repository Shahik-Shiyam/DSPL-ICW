import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load and enhance data with Risk Level
@st.cache_data
def load_data():
    df = pd.read_csv('Interest_Rates.csv')
    
    # Add Risk Level classification
    def classify_risk(value):
        if value < 10: return "Low"
        elif value < 20: return "Medium"
        else: return "High"
    
    df['Risk Level'] = df['Value'].apply(classify_risk)
    return df

# Initialize session state variables
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = st.session_state.df
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

df = st.session_state.df

# Dashboard setup
st.set_page_config(page_title="Interest Rates Risk Analysis", layout="wide")
st.title("Interest Rates with Risk Level Classification")

# Sidebar controls for page selection and filters
st.sidebar.header("Navigation")
if st.sidebar.button("About"):
    st.session_state.page = "About"
if st.sidebar.button("Dashboard"):
    st.session_state.page = "Dashboard"
if st.sidebar.button("Summary Statistics"):
    st.session_state.page = "Summary"

# Sidebar filters (always visible)
st.sidebar.header("Filters")
rate_types = df['Description'].unique()
selected_rates = st.sidebar.multiselect(
    "Select rate types", 
    rate_types, 
    default=["TREASURY BILL RATE", "ADVANCE RATE (END OF PERIOD)"]
)

risk_levels = st.sidebar.multiselect(
    "Select risk levels",
    ["Low", "Medium", "High"],
    default=["Low", "Medium", "High"]
)

year_range = st.sidebar_
