from __future__ import annotations
import os
from typing import Optional

import streamlit as st
import pandas as pd
import numpy as np

from utils import (
    load_or_download_dataset,
    clean_data,
    infer_columns,
    compute_affordability,
    summarize_affordability,
    recommend_actions,
    estimate_struggling,
)

# Optional plotting libraries
import plotly.express as px

try:
    import folium
    from streamlit_folium import st_folium
except Exception:
    folium = None
    st_folium = None  # type: ignore

# Guard optional statsmodels for trendline
try:
    import statsmodels.api as sm  # noqa: F401
    _HAS_SM = True
except Exception:
    _HAS_SM = False

APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Affordable Housing Needs Mapper", layout="wide")

st.title("Affordable Housing Needs Mapper")
st.write(
    "Explore affordability across areas using rents and incomes. Now using the Mumbai dataset you provided."
)

with st.sidebar:
    st.header("Filters")
    income_group_select = st.selectbox("Income Group", ["All", "low-income", "median-income", "high-income"], index=0)
    st.caption("Filtered by income terciles computed from the dataset.")

def _data_fingerprint() -> str:
    data_dir = os.path.join(APP_DIR, "data")
    parts = []
    try:
        for name in sorted(os.listdir(data_dir)):
            if name.lower().endswith(".csv"):
                p = os.path.join(data_dir, name)
                try:
                    stat = os.stat(p)
                    parts.append(f"{name}:{int(stat.st_mtime)}:{stat.st_size}")
                except Exception:
                    parts.append(f"{name}:0:0")
    except Exception:
        pass
    return "|".join(parts)

@st.cache_data(show_spinner=True)
def get_data(_fingerprint: str) -> pd.DataFrame:
    df, _path = load_or_download_dataset(APP_DIR)
    df = clean_data(df)
    area_col, rent_col, income_col, _geom = infer_columns(df)
    df = compute_affordability(df, area_col, rent_col, income_col)
    df["__area_col"] = area_col
    df["__rent_col"] = rent_col if rent_col else ""
    df["__income_col"] = income_col if income_col else ""
    return df

try:
    df = get_data(_data_fingerprint())
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

area_col = df["__area_col"].iloc[0]
rent_col = df["__rent_col"].iloc[0] or None
income_col = df["__income_col"].iloc[0] or None

# If Mumbai CSV columns are present, align them to our expectations
# Neighborhood -> area, Latitude/Longitude -> map, Avg_Rent_Monthly_INR, Median_Annual_Household_Income_INR
if "Neighborhood" in df.columns:
    area_col = "Neighborhood"
    df["__area_col"] = area_col
if "Avg_Rent_Monthly_INR" in df.columns:
    rent_col = "Avg_Rent_Monthly_INR"
    df["__rent_col"] = rent_col
if "Median_Annual_Household_Income_INR" in df.columns:
    income_col = "Median_Annual_Household_Income_INR"
    df["__income_col"] = income_col

if "Latitude" in df.columns and "Longitude" in df.columns:
    lat_col_hint = "Latitude"
    lon_col_hint = "Longitude"
else:
    lat_col_hint = None
    lon_col_hint = None

# Income group segmentation (heuristic based on income distribution)
if income_col is not None and income_col in df.columns:
    income_values = pd.to_numeric(df[income_col], errors="coerce")
    q1, q2, q3 = income_values.quantile([0.33, 0.66, 1.0])
    def label_income(v: float) -> str:
        if np.isnan(v):
            return "unknown"
        if v <= q1:
            return "low-income"
        if v <= q2:
            return "median-income"
        return "high-income"
    df["income_group"] = income_values.apply(label_income)
else:
    df["income_group"] = "unknown"

# Apply sidebar filters
if income_group_select and income_group_select != "All":
    df = df[df["income_group"] == income_group_select]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Affordability Map")
    if folium and st_folium:
        # Prefer explicit Latitude/Longitude for Mumbai CSV
        lat_col = lat_col_hint
        lon_col = lon_col_hint
        if not lat_col or not lon_col:
            for name in df.columns:
                low = name.lower()
                if low in {"lat", "latitude"}:
                    lat_col = name
                if low in {"lon", "longitude", "lng"}:
                    lon_col = name
        if lat_col and lon_col and lat_col in df.columns and lon_col in df.columns:
            fmap = folium.Map(location=[pd.to_numeric(df[lat_col], errors="coerce").median(), pd.to_numeric(df[lon_col], errors="coerce").median()], zoom_start=11, tiles="cartodbpositron")
            for _, row in df.iterrows():
                color = {
                    "Affordable": "green",
                    "Moderate": "orange",
                    "Expensive": "red",
                }.get(row.get("affordability_class", "Unknown"), "gray")
                try:
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                except Exception:
                    continue
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"{area_col}: {row.get(area_col, 'N/A')}\nIndex: {row.get('affordability_index', np.nan):.1f}",
                ).add_to(fmap)
            st_folium(fmap, width=None, height=520)
        else:
            st.info("No latitude/longitude columns found for map rendering in this dataset.")
    else:
        st.warning("folium/streamlit-folium not available. Install dependencies to see the map.")

with col2:
    st.subheader("Key Stats")
    stats_all = df["affordability_index"].describe()
    overall = stats_all[["count", "mean", "50%", "min", "max"]].rename({"50%": "median"})
    st.metric("Median Affordability Index", f"{overall['median']:.1f}")
    st.metric("Mean Affordability Index", f"{overall['mean']:.1f}")
    st.metric("Max Affordability Index", f"{overall['max']:.1f}")
    # Struggling estimate
    overall_cnt, overall_pct, per_area = estimate_struggling(df, area_col, threshold=50.0)
    st.metric("Households Struggling (>50)", f"{overall_cnt}", help="Count of rows exceeding affordability index 50")
    st.metric("Share Struggling", f"{overall_pct*100:.1f}%")

st.subheader("Income vs Rent")
if rent_col and income_col and rent_col in df.columns and income_col in df.columns:
    trendline_value = "ols" if _HAS_SM else None
    fig = px.scatter(
        df,
        x=income_col,
        y=rent_col,
        color="affordability_class",
        hover_data=[area_col],
        trendline=trendline_value,
        labels={income_col: "Annual Income", rent_col: "Monthly Rent" if "month" in rent_col.lower() else rent_col},
        title="Income vs Rent/Price with Affordability Classification",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Income or rent columns not identified; showing affordability distribution instead.")
    fig = px.histogram(df, x="affordability_index", nbins=30, color="affordability_class")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Affordability by Area (Median Index)")
summary = summarize_affordability(df, area_col)
bar = px.bar(
    summary,
    x=area_col,
    y="median_affordability_index",
    color="affordability_class",
    title="Median Affordability Index by Area",
)
st.plotly_chart(bar, use_container_width=True)

# Top-N areas by struggling percent
st.subheader("Top Areas by Housing Stress (Struggling %)")
try:
    _, _, per_area = estimate_struggling(df, area_col, threshold=50.0)
    per_area_sorted = per_area.sort_values("struggling_pct", ascending=False)
    bar2 = px.bar(
        per_area_sorted,
        x=area_col,
        y=(per_area_sorted["struggling_pct"] * 100.0),
        labels={"y": "Struggling %"},
        title="Struggling Households Share by Area",
    )
    bar2.update_yaxes(title="Struggling %")
    st.plotly_chart(bar2, use_container_width=True)
except Exception as e:
    st.info("Unable to compute per-area stress metrics.")

st.subheader("Recommendations")
for rec in recommend_actions(df, area_col, top_k=5):
    st.write("- ", rec)

st.caption(
    "Affordability index = (annualized rent / annual income) * 100. Thresholds: <30 Affordable, 30–50 Moderate, >50 Expensive."
)
