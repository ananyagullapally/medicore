import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="ReadmitIQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# GLOBAL COLORS
# =====================================================
PRIMARY_SCALE = "Blues"

RISK_COLORS = {
    "High Risk": "#dc2626",
    "Moderate Risk": "#f59e0b",
    "Low Risk": "#16a34a"
}

# =====================================================
# FILE PATHS
# =====================================================
CMS_PATH = "/Users/ananyagullapally/Documents/hospital-readmissions/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"

POP_PATH = "/Users/ananyagullapally/Downloads/state_population_2025_clean.csv"

# =====================================================
# STATE NAME TO CODE
# =====================================================
state_map = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR",
    "California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE",
    "District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI",
    "Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
    "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
    "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
    "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI",
    "South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX",
    "Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
    "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():

    df = pd.read_csv(CMS_PATH)
    df.columns = df.columns.str.strip()

    numeric_cols = [
        "Excess Readmission Ratio",
        "Predicted Readmission Rate",
        "Expected Readmission Rate",
        "Number of Discharges",
        "Number of Readmissions"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Excess Readmission Ratio"]).copy()

    # Population data
    pop = pd.read_csv(POP_PATH)
    pop["State"] = pop["State"].map(state_map)

    df = df.merge(pop, on="State", how="left")

    return df

df = load_data()

# =====================================================
# COLUMN REFERENCES
# =====================================================
metric = "Excess Readmission Ratio"
state_col = "State"
hospital_col = "Facility Name"
measure_col = "Measure Name"
discharge_col = "Number of Discharges"
pop_col = "Population_2025"

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("Dashboard Parameters")

selected_measure = st.sidebar.selectbox(
    "Measure",
    ["All"] + sorted(df[measure_col].dropna().unique())
)

selected_states = st.sidebar.multiselect(
    "States",
    sorted(df[state_col].dropna().unique()),
    default=[]
)

top_n = st.sidebar.slider("Top N", 5, 25, 10)

analysis_mode = st.sidebar.radio(
    "Analysis Mode",
    ["Raw Performance", "Population Adjusted"]
)

# =====================================================
# FILTER DATA
# =====================================================
filtered_df = df.copy()

if selected_measure != "All":
    filtered_df = filtered_df[
        filtered_df[measure_col] == selected_measure
    ]

if selected_states:
    filtered_df = filtered_df[
        filtered_df[state_col].isin(selected_states)
    ]

# =====================================================
# KPI VALUES
# =====================================================
rows = len(filtered_df)
hospitals = filtered_df[hospital_col].nunique()
states_n = filtered_df[state_col].nunique()
measures_n = filtered_df[measure_col].nunique()
avg_metric = round(filtered_df[metric].mean(), 4)

# =====================================================
# STATE SUMMARY
# =====================================================
state_summary = (
    filtered_df.groupby(state_col)
    .agg({
        metric: "mean",
        hospital_col: "nunique",
        pop_col: "first"
    })
    .reset_index()
)

state_summary.columns = [
    state_col,
    metric,
    "Hospitals",
    pop_col
]

state_summary["Hospitals_per_Million"] = (
    state_summary["Hospitals"] /
    (state_summary[pop_col] / 1000000)
)

state_summary["Risk_Burden_Index"] = (
    state_summary[metric] *
    state_summary[pop_col]
)

def classify_risk(x):
    if x > 1.02:
        return "High Risk"
    elif x >= 0.99:
        return "Moderate Risk"
    return "Low Risk"

state_summary["Risk Level"] = state_summary[metric].apply(classify_risk)

# =====================================================
# HEADER
# =====================================================
st.title("ReadmitIQ | Intelligent Hospital Readmission Analytics")
st.caption("Integrated CMS + Census population intelligence platform")

# =====================================================
# KPI ROW
# =====================================================
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Rows", f"{rows:,}")
c2.metric("Hospitals", f"{hospitals:,}")
c3.metric("States", states_n)
c4.metric("Measures", measures_n)
c5.metric("Avg Ratio", avg_metric)

st.markdown("---")

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Summary",
    "State Intelligence",
    "Country Intelligence",
    "Clinical Measures",
    "Hospital Explorer",
    "Savings Simulator"
])

# =====================================================
# TAB 1
# =====================================================
with tab1:

    total_pop = state_summary[pop_col].sum()

    k1, k2, k3 = st.columns(3)

    k1.metric("Population Covered", f"{total_pop/1000000:.1f}M")
    k2.metric("Hospitals / Million", f"{hospitals/(total_pop/1000000):.1f}")
    k3.metric("Avg Risk Ratio", avg_metric)

    st.markdown("### National Risk Distribution")

    risk_counts = (
        state_summary["Risk Level"]
        .value_counts()
        .reset_index()
    )

    risk_counts.columns = ["Risk Level", "Count"]

    fig_risk = px.bar(
        risk_counts,
        x="Risk Level",
        y="Count",
        color="Risk Level",
        color_discrete_map=RISK_COLORS
    )

    fig_risk.update_layout(showlegend=False, height=420)

    st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("### State Risk Summary")

    st.dataframe(
        state_summary[
            [state_col, metric, "Risk Level", "Hospitals_per_Million"]
        ].sort_values(metric, ascending=False),
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# TAB 2
# =====================================================
with tab2:

    st.subheader("State Benchmark Rankings")

    if analysis_mode == "Raw Performance":
        ranked = state_summary.sort_values(metric, ascending=False).head(top_n)
        x_col = metric
        title = f"Top {top_n} States by Readmission Ratio"

    else:
        ranked = state_summary.sort_values(
            "Risk_Burden_Index",
            ascending=False
        ).head(top_n)
        x_col = "Risk_Burden_Index"
        title = f"Top {top_n} States by Risk Burden"

    fig_rank = px.bar(
        ranked,
        x=x_col,
        y=state_col,
        orientation="h",
        color=x_col,
        color_continuous_scale=PRIMARY_SCALE,
        title=title
    )

    fig_rank.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        height=550
    )

    st.plotly_chart(fig_rank, use_container_width=True)

# =====================================================
# TAB 3
# =====================================================
with tab3:

    st.subheader("National Geographic Intelligence")

    map_metric = st.selectbox(
        "Map Metric",
        [
            metric,
            "Hospitals_per_Million",
            "Risk_Burden_Index"
        ]
    )

    fig_map = px.choropleth(
        state_summary,
        locations=state_col,
        locationmode="USA-states",
        color=map_metric,
        scope="usa",
        hover_name=state_col,
        color_continuous_scale=PRIMARY_SCALE
    )

    fig_map.update_layout(height=620)

    st.plotly_chart(fig_map, use_container_width=True)

# =====================================================
# TAB 4
# =====================================================
with tab4:

    st.subheader("Clinical Measure Performance")

    measure_summary = (
        filtered_df.groupby(measure_col)[metric]
        .mean()
        .reset_index()
        .sort_values(metric, ascending=False)
    )

    fig_measure = px.bar(
        measure_summary,
        x=metric,
        y=measure_col,
        orientation="h",
        color=metric,
        color_continuous_scale=PRIMARY_SCALE
    )

    fig_measure.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        height=560
    )

    st.plotly_chart(fig_measure, use_container_width=True)

# =====================================================
# TAB 5
# =====================================================
with tab5:

    st.subheader("Hospital Explorer")

    search = st.text_input("Search Hospital")

    hospital_df = filtered_df.copy()

    if search:
        hospital_df = hospital_df[
            hospital_df[hospital_col].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        hospital_df[
            [
                hospital_col,
                state_col,
                measure_col,
                metric,
                discharge_col
            ]
        ].sort_values(metric, ascending=False).head(50),
        use_container_width=True
    )

    st.markdown("### Hospital Volume vs Readmission Ratio")

    scatter_df = hospital_df.dropna(
        subset=[discharge_col, metric]
    )

    fig_scatter = px.scatter(
        scatter_df,
        x=discharge_col,
        y=metric,
        color=state_col,
        hover_name=hospital_col
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

# =====================================================
# TAB 6
# =====================================================
with tab6:

    st.subheader("Projected Savings Simulator")

    reduction = st.slider(
        "Reduce Readmission Ratio By %",
        1,
        20,
        5
    )

    estimated_savings = (
        hospitals *
        reduction *
        50000
    )

    s1, s2 = st.columns(2)

    s1.metric("Reduction Target", f"{reduction}%")
    s2.metric("Projected Savings", f"${estimated_savings:,.0f}")

    months = pd.DataFrame({
        "Month": [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ],
        "Savings": np.cumsum(
            np.random.randint(
                estimated_savings//20,
                estimated_savings//8,
                12
            )
        )
    })

    fig_line = px.line(
        months,
        x="Month",
        y="Savings",
        markers=True
    )

    fig_line.update_traces(line=dict(color="#2563eb"))

    st.plotly_chart(fig_line, use_container_width=True)

# =====================================================
# DOWNLOAD
# =====================================================
st.markdown("---")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Current Dataset",
    csv,
    "readmitiq_export.csv",
    "text/csv"
)