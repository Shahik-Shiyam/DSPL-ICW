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

df = load_data()

# Dashboard setup
st.set_page_config(page_title="Interest Rates Risk Analysis", layout="wide")
st.title("Interest Rates with Risk Level Classification")

# Sidebar controls
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

year_range = st.sidebar.slider(
    "Select year range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(1990, 2008)
)

# Filter data
filtered_df = df[(
    df['Description'].isin(selected_rates)) & 
    (df['Risk Level'].isin(risk_levels)) & 
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1])
]

# Main visualizations
st.subheader("Comparative Analysis")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Scatter Plot", "Pie Chart", "Area Chart", "Histogram", "Heatmap"])

with tab1:
    st.subheader("Interest Rates by Risk Level")
    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="Year",
            y="Value",
            color="Risk Level",
            color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
            hover_data=["Description"],
            title="Rates Colored by Risk Level",
            labels={"Value": "Interest Rate (%)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data matches your filters")

with tab2:
    st.subheader("Risk Level Distribution")
    if not filtered_df.empty:
        risk_counts = filtered_df['Risk Level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        
        fig = px.pie(
            risk_counts,
            names="Risk Level",
            values="Count",
            color="Risk Level",
            color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data matches your filters")

with tab3:
    st.subheader("Risk Level Trends Over Time")
    if not filtered_df.empty:
        yearly_risk = filtered_df.groupby(['Year', 'Risk Level']).size().unstack().fillna(0)
        
        fig = px.area(
            yearly_risk,
            color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
            title="Count of Rates by Risk Level Each Year"
        )
        fig.update_layout(yaxis_title="Count of Rates")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data matches your filters")

with tab4:
    st.subheader("Interest Rate Distribution Histogram")
    if not filtered_df.empty:
        selected_rate = st.selectbox(
            "Select rate type for histogram",
            filtered_df['Description'].unique()
        )
        bins = st.slider(
            "Number of bins",
            min_value=5,
            max_value=50,
            value=15
        )
        
        hist_data = filtered_df[filtered_df['Description'] == selected_rate]
        
        if not hist_data.empty:
            fig = px.histogram(
                hist_data,
                x="Value",
                nbins=bins,
                color="Risk Level",
                color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
                title=f"Distribution of {selected_rate}",
                labels={"Value": "Interest Rate (%)"},
                marginal="rug",
                hover_data=["Year"]
            )
            
            # Add vertical line for mean
            mean_val = hist_data['Value'].mean()
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color="black",
                annotation_text=f"Mean: {mean_val:.2f}%",
                annotation_position="top"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display statistics
            st.write(f"""
            **Statistics for {selected_rate}**:
            - Mean: {hist_data['Value'].mean():.2f}%
            - Median: {hist_data['Value'].median():.2f}%
            - Standard Deviation: {hist_data['Value'].std():.2f}%
            - Minimum: {hist_data['Value'].min():.2f}%
            - Maximum: {hist_data['Value'].max():.2f}%
            """)
        else:
            st.warning(f"No data available for {selected_rate} with current filters")
    else:
        st.warning("No data matches your filters")

with tab5:
    st.subheader("Heatmap of Interest Rates by Year and Risk Level")
    if not filtered_df.empty:
        # Pivot table to structure the data for heatmap
        heatmap_data = filtered_df.pivot_table(
            index='Year', columns='Risk Level', values='Value', aggfunc=np.mean
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn',
            colorbar=dict(title="Interest Rate (%)")
        ))
        fig.update_layout(
            title="Heatmap of Average Interest Rates by Risk Level",
            xaxis_title="Risk Level",
            yaxis_title="Year"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data matches your filters")

# Show data table with risk levels
st.subheader("Detailed Data with Risk Levels")
st.dataframe(
    filtered_df.sort_values(['Year', 'Risk Level']),
    column_order=['Year', 'Description', 'Value', 'Risk Level'],
    hide_index=True,
    height=300
)
