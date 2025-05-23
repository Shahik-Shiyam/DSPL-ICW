import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set Streamlit config at the top
st.set_page_config(page_title="Interest Rates Risk Analysis", layout="wide")

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

    # Simulate sector type column (if it doesn't exist)
    if 'Sector Type' not in df.columns:
        df['Sector Type'] = np.where(df['Description'].str.contains("TREASURY|BILL", case=False), "Public", "Private")

    return df

# Initialize session state variables
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = st.session_state.df
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

df = st.session_state.df

# Title
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

year_range = st.sidebar.slider(
    "Select year range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(1990, 2008)
)

# Apply filters
filtered_df = df[
    (df['Description'].isin(selected_rates)) & 
    (df['Risk Level'].isin(risk_levels)) & 
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1])
]
st.session_state.filtered_df = filtered_df

# Page routing
if st.session_state.page == "About":
    st.subheader("About this Dashboard")
    st.write("""
        This dashboard visualizes and analyzes interest rates with a focus on risk classification.

        ###  What does this dashboard do?
        - It classifies interest rate data into three risk levels:
            - **Low Risk**: Interest rate below 10%
            - **Medium Risk**: Interest rate between 10% and 20%
            - **High Risk**: Interest rate above 20%
        - Risk level is also determined by the **type of security** and **sector type**.
        - A new column, **Sector Type**, was added to help distinguish between public and private financial instruments.
        - You can filter the dataset by:
            - Interest rate type
            - Risk level
            - Year range

        ###  About the Dataset
        - **Source**: United Nations Data Portal (UNData)
        - **Content**: Historical interest rate values reported by various countries across different types.
        - **Variables include**:
            - `Country`
            - `Year`
            - `Description` (Rate type)
            - `Value` (Interest rate %)
            - `Risk Level`
            - `Sector Type`

        Below is the full dataset used in this dashboard:
    """)
    st.dataframe(df)

elif st.session_state.page == "Dashboard":
    st.subheader("Comparative Analysis")

    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)

        avg_rate = filtered_df['Value'].mean()
        max_rate = filtered_df['Value'].max()
        min_rate = filtered_df['Value'].min()
        std_dev = filtered_df['Value'].std()

        col1.metric("Average Interest Rate", f"{avg_rate:.2f}%")
        col2.metric("Max Interest Rate", f"{max_rate:.2f}%")
        col3.metric("Min Interest Rate", f"{min_rate:.2f}%")
        col4.metric("Standard Deviation", f"{std_dev:.2f}")
    else:
        st.warning("No data matches your filters")

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

                mean_val = hist_data['Value'].mean()
                fig.add_vline(
                    x=mean_val,
                    line_dash="dash",
                    line_color="black",
                    annotation_text=f"Mean: {mean_val:.2f}%",
                    annotation_position="top"
                )

                st.plotly_chart(fig, use_container_width=True)

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
            heatmap_data = filtered_df.pivot_table(
                index='Year',
                columns='Risk Level',
                values='Value',
                aggfunc=np.mean
            )

            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                colorbar=dict(title='Interest Rate (%)'),
            ))
            fig.update_layout(title="Heatmap of Interest Rates by Year and Risk Level")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data matches your filters")

elif st.session_state.page == "Summary":
    st.subheader("Summary Statistics")

    if not filtered_df.empty:
        st.write("### Basic Statistics")
        st.write(filtered_df['Value'].describe().to_frame().T)

        st.write("### Statistics by Risk Level")
        risk_stats = filtered_df.groupby('Risk Level')['Value'].agg(['mean', 'median', 'std', 'min', 'max'])
        st.write(risk_stats)

        st.write("### Statistics by Rate Type")
        rate_stats = filtered_df.groupby('Description')['Value'].agg(['mean', 'median', 'std', 'min', 'max'])
        st.write(rate_stats)

        st.write("### Yearly Statistics")
        yearly_stats = filtered_df.groupby('Year')['Value'].agg(['mean', 'median', 'std', 'min', 'max'])
        st.write(yearly_stats)
    else:
        st.warning("No data matches your filters")
