# ReadmitIQ — Hospital Readmission Analytics Platform

An end-to-end data warehousing and business intelligence platform for analyzing U.S. hospital readmission performance. Built using real CMS public health data integrated with U.S. Census population data, the system transforms raw healthcare records into actionable insights through a structured data warehouse and an interactive Streamlit dashboard.

---

## Overview

Hospital readmissions are a critical quality metric for U.S. healthcare systems. Under CMS programs, hospitals with excessive readmission rates face financial penalties — making timely, data-driven analysis essential for administrators and policymakers.

ReadmitIQ answers four key questions:
- Which hospitals and states carry the highest readmission risk?
- Which clinical conditions drive the most readmissions?
- How does healthcare capacity compare across populations?
- Where should resources and interventions be prioritized?

---

## Dashboard Features

| Tab | Description |
|-----|-------------|
| **Executive Summary** | National KPIs — 11,720 records, 2,774 hospitals, 51 states, avg excess ratio 1.0018 |
| **State Intelligence** | State benchmark rankings by excess readmission ratio |
| **Country Intelligence** | Choropleth map of readmission risk across the U.S. |
| **Clinical Measures** | Readmission ratio comparison across 6 clinical conditions |
| **Hospital Explorer** | Drill-down into individual hospital performance + volume vs. ratio scatter |
| **Savings Simulator** | Projects financial savings from reducing readmission rates (e.g. 5% reduction → ~$693M saved) |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data Warehouse | Oracle Database, SQL Developer |
| Data Modeling | Kimball Star Schema (FACT_READMISSION + 4 dimensions) |
| ETL & EDA | Python, Pandas |
| Analytics | Advanced SQL — window functions, Z-score normalization, NTILE bucketing |
| Dashboard | Streamlit, Plotly |

---

## Data Sources

- **CMS Hospital Readmissions Reduction Program (HRRP)** — hospital-level readmission metrics across the U.S. ([CMS Provider Data Portal](https://data.cms.gov))
- **U.S. Census Bureau** — state-level population estimates for per-capita normalization

---

## Data Warehouse Design

The warehouse follows Kimball dimensional modeling principles with a central fact table and four surrounding dimensions:

```
FACT_READMISSION
├── DIM_HOSPITAL     (facility, state, type, ownership)
├── DIM_MEASURE      (clinical condition, category)
├── DIM_STATE        (state, region, census division)
└── DIM_POPULATION   (population 2025, density, hospitals per million)
```

**Fact table grain:** one record per hospital, per clinical measure, per reporting period.

---

## Key Analytical Findings

- **Heart Failure (HF)** accounts for ~43% of total readmissions; Pneumonia (PN) accounts for ~33%
- **Florida, California, and Texas** report the highest raw readmission volumes
- **Massachusetts, New Jersey, and Florida** rank highest by excess readmission ratio
- **A small subset of hospitals** drives disproportionate readmission rates — the problem is concentrated, not evenly distributed
- **Smaller hospitals** show greater ratio variability than high-volume institutions
- A **5% reduction** in readmission rates projects to ~$693M in annual savings

---

## Running the Dashboard Locally

**Prerequisites:** Python 3.8+

```bash
# Clone the repo
git clone https://github.com/ananyagullapally/medicore.git
cd medicore

# Install dependencies
pip install streamlit plotly pandas

# Run the dashboard
streamlit run viz.py
```

---

## Project Structure

```
medicore/
├── viz.py                          # Streamlit dashboard (all tabs)
├── eda-cleaning.ipynb              # EDA and data cleaning notebook
├── FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv
├── OLTP-model.png                  # Transactional source model diagram
├── star-schema-model.png           # Dimensional warehouse model diagram
└── output-img/                     # Dashboard screenshots
```

---

## Course Context

Built as the final project for ISM 6208 – Data Warehousing at the University of South Florida (Spring 2026).

---

## References

- Kimball, R. & Ross, M. — *The Data Warehouse Toolkit*
- Inmon, W. H. — *Building the Data Warehouse*
- CMS Readmissions Reduction Program documentation
