import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Interest_Rates.csv')
    return df

df = load_data()

# Set up the dashboard
st.set_page_config(page_title="Interest Rates Dashboard", layout="wide")
st.title("Historical Interest Rates Analysis (1950-2008)")

# Sidebar controls
st.sidebar.header("Dashboard Controls")
rate_types = df['Description'].unique()
selected_rates = st.sidebar.multiselect(
    "Select rate types to display", 
    rate_types, 
    default=["TREASURY BILL RATE", "ADVANCE RATE (END OF PERIOD)"]
)

year_range = st.sidebar.slider(
    "Select year range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(1990, 2008)
)

# Filter data based on selections
filtered_df = df[
    (df['Description'].isin(selected_rates)) & 
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1])
]

# Main dashboard layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Interest Rate Trends")
    
    if not selected_rates:
        st.warning("Please select at least one rate type from the sidebar")
    else:
        # Line chart
        fig = px.line(
            filtered_df, 
            x="Year", 
            y="Value", 
            color="Description",
            title=f"Interest Rates ({year_range[0]}-{year_range[1]})",
            labels={"Value": "Interest Rate (%)", "Year": "Year"},
            height=500
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Key Statistics")
    
    if not selected_rates:
        st.write("Select rates to see statistics")
    else:
        for rate in selected_rates:
            rate_data = filtered_df[filtered_df['Description'] == rate]
            if not rate_data.empty:
                st.metric(
                    label=f"{rate} (Avg)",
                    value=f"{rate_data['Value'].mean():.2f}%",
                    delta=f"Range: {rate_data['Value'].min():.2f}% - {rate_data['Value'].max():.2f}%"
                )

# Additional visualizations
st.subheader("Comparative Analysis")

tab1, tab2, tab3 = st.tabs(["All Rates Heatmap", "Yearly Comparison", "Rate Distribution"])

with tab1:
    # Prepare data for heatmap
    heatmap_data = df.pivot_table(index='Year', columns='Description', values='Value')
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Rate Type", y="Year", color="Interest Rate"),
        title="Interest Rates Heatmap",
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    selected_year = st.selectbox("Select year to compare rates", sorted(df['Year'].unique(), reverse=True))
    year_data = df[df['Year'] == selected_year]
    
    if not year_data.empty:
        fig = px.bar(
            year_data,
            x="Description",
            y="Value",
            title=f"Rate Comparison for {selected_year}",
            labels={"Value": "Interest Rate (%)", "Description": "Rate Type"},
            color="Description"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write(f"No data available for {selected_year}")

with tab3:
    if not selected_rates:
        st.write("Select rates to see distributions")
    else:
        fig = px.box(
            filtered_df,
            x="Description",
            y="Value",
            title="Rate Distributions",
            labels={"Value": "Interest Rate (%)", "Description": "Rate Type"},
            color="Description"
        )
        st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("Raw Data")
st.dataframe(filtered_df.sort_values(['Year', 'Description']), height=300)


# Add this to your existing Streamlit dashboard code (under the tabs section)

# Add a new tab for the histogram
tab1, tab2, tab3, tab4 = st.tabs(["All Rates Heatmap", "Yearly Comparison", "Rate Distribution", "Histogram"])

# ... keep your existing tab1, tab2, tab3 code ...

with tab4:
    st.subheader("Interest Rate Distribution Histogram")
    
    # User controls for histogram
    col1, col2 = st.columns(2)
    with col1:
        hist_rate = st.selectbox(
            "Select rate type for histogram",
            rate_types,
            index=0
        )
    with col2:
        bins = st.slider(
            "Number of bins",
            min_value=5,
            max_value=50,
            value=15
        )
    
    # Filter data for selected rate
    hist_data = df[df['Description'] == hist_rate]
    
    if not hist_data.empty:
        fig = px.histogram(
            hist_data,
            x="Value",
            nbins=bins,
            title=f"Distribution of {hist_rate}",
            labels={"Value": "Interest Rate (%)"},
            color_discrete_sequence=['#636EFA'],
            marginal="box"  # Adds a box plot on top
        )
        
        # Add vertical line for mean
        mean_val = hist_data['Value'].mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_val:.2f}%",
            annotation_position="top"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.write(f"""
        **Statistics for {hist_rate}**:
        - Mean: {hist_data['Value'].mean():.2f}%
        - Median: {hist_data['Value'].median():.2f}%
        - Standard Deviation: {hist_data['Value'].std():.2f}%
        - Minimum: {hist_data['Value'].min():.2f}%
        - Maximum: {hist_data['Value'].max():.2f}%
        """)
    else:
        st.warning(f"No data available for {hist_rate}")



        import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Interest_Rates.csv')
    return df

df = load_data()

# Set up the dashboard
st.set_page_config(page_title="Interest Rates Dashboard", layout="wide")
st.title("Historical Interest Rates Analysis (1950-2008)")

# Sidebar controls
st.sidebar.header("Dashboard Controls")

# Get all unique rate types
rate_types = df['Description'].unique()

# Add "Select All" checkbox
select_all = st.sidebar.checkbox("Select All Rate Types", value=True)

if select_all:
    selected_rates = rate_types
else:
    selected_rates = st.sidebar.multiselect(
        "Select rate types to display", 
        rate_types,
        default=["TREASURY BILL RATE", "ADVANCE RATE (END OF PERIOD)"]
    )

year_range = st.sidebar.slider(
    "Select year range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(1990, 2008)
)

# Filter data based on selections
filtered_df = df[
    (df['Description'].isin(selected_rates)) & 
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1])
]

# Main visualization
st.subheader("Interest Rate Trends")

if not selected_rates:
    st.warning("Please select at least one rate type from the sidebar")
else:
    fig = px.line(
        filtered_df, 
        x="Year", 
        y="Value", 
        color="Description",
        title=f"Interest Rates ({year_range[0]}-{year_range[1]})",
        labels={"Value": "Interest Rate (%)", "Year": "Year"},
        height=500
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# Rest of your dashboard code...