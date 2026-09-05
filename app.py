import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME
# ==============================================================================
st.set_page_config(
    page_title="Live Space Missions Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI cards
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA LOADING & CACHING
# ==============================================================================
@st.cache_data
def load_data(filepath_or_buffer):
    """Loads and cleans the space mission dataset."""
    df = pd.read_csv(filepath_or_buffer)
    
    # Drop redundant index columns
    cols_to_drop = [c for c in ['Unnamed: 0.1', 'Unnamed: 0'] if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    
    # Process Datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True)
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%b')
    
    # Extract Country from Location
    df['Country'] = df['Location'].apply(lambda x: x.split(',')[-1].strip() if pd.notnull(x) else 'Unknown')
    
    # Clean Price Column ($ Millions)
    df['Price_M'] = df['Price'].astype(str).str.replace(',', '', regex=False)
    df['Price_M'] = pd.to_numeric(df['Price_M'], errors='coerce')
    
    # Clean Rocket Status
    df['Rocket_Status'] = df['Rocket_Status'].astype(str).str.replace('Status', '', regex=False)
    
    return df

# Load initial dataset
try:
    df_raw = load_data("space_mission_data.csv")
except Exception:
    st.error("⚠️ `space_mission_data.csv` not found in the directory. Please upload a file below.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df_raw = load_data(uploaded_file)
    else:
        st.stop()

# ==============================================================================
# 3. SIDEBAR - LIVE INTERACTIVE FILTERS
# ==============================================================================
st.sidebar.title("🎛️ Live Dashboard Controls")

# Live Keyword Search
search_query = st.sidebar.text_input("🔍 Search Mission Details / Payload", placeholder="e.g. Starlink, Apollo, Falcon")

# Year Range Slider
min_year, max_year = int(df_raw['Year'].min()), int(df_raw['Year'].max())
selected_years = st.sidebar.slider(
    "📅 Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Multi-select Organization Filter
all_orgs = sorted(df_raw['Organisation'].unique().tolist())
selected_orgs = st.sidebar.multiselect("🏢 Organization", options=all_orgs)

# Multi-select Country Filter
all_countries = sorted(df_raw['Country'].unique().tolist())
selected_countries = st.sidebar.multiselect("🌍 Country", options=all_countries)

# Multi-select Mission Status Filter
all_statuses = sorted(df_raw['Mission_Status'].unique().tolist())
selected_statuses = st.sidebar.multiselect("🎯 Mission Status", options=all_statuses, default=all_statuses)

# --- APPLY FILTERS DYNAMICALLY ---
filtered_df = df_raw[
    (df_raw['Year'] >= selected_years[0]) & 
    (df_raw['Year'] <= selected_years[1]) &
    (df_raw['Mission_Status'].isin(selected_statuses))
]

if selected_orgs:
    filtered_df = filtered_df[filtered_df['Organisation'].isin(selected_orgs)]
if selected_countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
if search_query:
    filtered_df = filtered_df[filtered_df['Detail'].str.contains(search_query, case=False, na=False)]

# ==============================================================================
# 4. DASHBOARD HEADER & LIVE KPIS
# ==============================================================================
st.markdown('<div class="main-title">🌌 Space Missions Live Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive exploration of space launches, costs, and success rates from 1957 to 2020</div>', unsafe_allow_html=True)

# Live Metric Calculations
total_launches = len(filtered_df)
success_count = (filtered_df['Mission_Status'] == 'Success').sum()
success_rate = (success_count / total_launches * 100) if total_launches > 0 else 0
active_rockets = (filtered_df['Rocket_Status'] == 'Active').sum()
total_cost = filtered_df['Price_M'].sum()
avg_cost = filtered_df['Price_M'].mean()

# Display KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Missions", f"{total_launches:,}")
kpi2.metric("Success Rate", f"{success_rate:.1f}%")
kpi3.metric("Active Rockets", f"{active_rockets:,}")
kpi4.metric("Avg Cost / Launch", f"${avg_cost:.1f}M" if not np.isnan(avg_cost) else "N/A")
kpi5.metric("Total Tracked Spend", f"${total_cost:,.0f}M" if total_cost > 0 else "N/A")

st.markdown("---")

# ==============================================================================
# 5. DYNAMIC INTERACTIVE CHARTS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Timeline Analytics", 
    "🏆 Top Players & Locations", 
    "💵 Financial Distribution", 
    "📄 Interactive Data Table"
])

# ------------------------------------------------------------------------------
# TAB 1: LAUNCH TIMELINE & OUTCOMES
# ------------------------------------------------------------------------------
with tab1:
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        # Yearly Stacked Bar Chart
        yearly_data = filtered_df.groupby(['Year', 'Mission_Status']).size().reset_index(name='Launches')
        fig_timeline = px.bar(
            yearly_data,
            x='Year',
            y='Launches',
            color='Mission_Status',
            title="Annual Launch Volume by Outcome",
            color_discrete_map={
                'Success': '#10B981',
                'Failure': '#EF4444',
                'Partial Failure': '#F59E0B',
                'Prelaunch Failure': '#6366F1'
            },
            template="plotly_white"
        )
        fig_timeline.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_timeline, use_container_width=True)
        
    with col_b:
        # Donut Chart for Outcome Percentages
        outcome_counts = filtered_df['Mission_Status'].value_counts().reset_index()
        outcome_counts.columns = ['Status', 'Count']
        fig_pie = px.pie(
            outcome_counts,
            names='Status',
            values='Count',
            title="Mission Success Share",
            hole=0.45,
            color='Status',
            color_discrete_map={
                'Success': '#10B981',
                'Failure': '#EF4444',
                'Partial Failure': '#F59E0B',
                'Prelaunch Failure': '#6366F1'
            },
            template="plotly_white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: ORGANIZATIONS & COUNTRIES
# ------------------------------------------------------------------------------
with tab2:
    col_c, col_d = st.columns(2)
    
    with col_c:
        top_orgs = filtered_df['Organisation'].value_counts().head(12).reset_index()
        top_orgs.columns = ['Organisation', 'Missions']
        fig_orgs = px.bar(
            top_orgs,
            x='Missions',
            y='Organisation',
            orientation='h',
            title="Top 12 Launch Organizations",
            color='Missions',
            color_continuous_scale='Blues',
            template="plotly_white"
        )
        fig_orgs.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_orgs, use_container_width=True)
        
    with col_d:
        top_countries = filtered_df['Country'].value_counts().head(10).reset_index()
        top_countries.columns = ['Country', 'Missions']
        fig_country = px.bar(
            top_countries,
            x='Country',
            y='Missions',
            title="Top 10 Launch Locations by Country",
            color='Missions',
            color_continuous_scale='Purples',
            template="plotly_white"
        )
        st.plotly_chart(fig_country, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: COST ANALYSIS
# ------------------------------------------------------------------------------
with tab3:
    cost_df = filtered_df.dropna(subset=['Price_M'])
    
    if not cost_df.empty:
        col_e, col_f = st.columns(2)
        
        with col_e:
            fig_cost_hist = px.histogram(
                cost_df,
                x='Price_M',
                nbins=25,
                title="Launch Cost Distribution ($ Millions)",
                color_discrete_sequence=['#0EA5E9'],
                template="plotly_white"
            )
            fig_cost_hist.update_layout(xaxis_title="Cost ($ Millions)", yaxis_title="Number of Launches")
            st.plotly_chart(fig_cost_hist, use_container_width=True)
            
        with col_f:
            avg_spend = cost_df.groupby('Organisation')['Price_M'].agg(['mean', 'count']).reset_index()
            avg_spend = avg_spend[avg_spend['count'] >= 3].sort_values(by='mean', ascending=False).head(10)
            
            fig_avg_cost = px.bar(
                avg_spend,
                x='mean',
                y='Organisation',
                orientation='h',
                title="Avg Mission Cost by Org (Min. 3 Reported Launches)",
                labels={'mean': 'Avg Cost ($M)'},
                color='mean',
                color_continuous_scale='Tealgrn',
                template="plotly_white"
            )
            fig_avg_cost.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_avg_cost, use_container_width=True)
    else:
        st.info("ℹ️ No cost data available for the currently selected combination of filters.")

# ------------------------------------------------------------------------------
# TAB 4: RAW DATA EXPLORER & DOWNLOAD
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Filtered Launch Logs")
    
    # Dynamic Column Selector
    selected_cols = st.multiselect(
        "Select Columns to Display",
        options=filtered_df.columns.tolist(),
        default=['Organisation', 'Location', 'Date', 'Detail', 'Price_M', 'Mission_Status']
    )
    
    st.dataframe(filtered_df[selected_cols], use_container_width=True)
    
    # CSV Download Button
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Dataset to CSV",
        data=csv_bytes,
        file_name="space_missions_filtered.csv",
        mime="text/csv"
    )