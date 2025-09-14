from __future__ import annotations
import os
import json
from typing import Tuple, Optional, Tuple as TypingTuple

import pandas as pd
import numpy as np

# Optional imports guarded at runtime for environments without geopandas/folium
try:
    import geopandas as gpd  # noqa: F401
except Exception:
    gpd = None  # type: ignore


def ensure_data_dir(base_dir: str) -> str:
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def download_kaggle_dataset(target_dir: str) -> Optional[str]:
    """
    Download the Kaggle dataset using kagglehub and copy CSVs into target_dir.
    Returns the local directory path containing downloaded files, or None on failure.
    """
    try:
        import kagglehub  # type: ignore
    except Exception as e:
        print(f"kagglehub not available: {e}")
        return None

    try:
        path = kagglehub.dataset_download("huyngohoang/housingcsv")
        print("Path to dataset files:", path)
        # Copy CSV files if any to target_dir
        for root, _dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith((".csv", ".geojson", ".json")):
                    src = os.path.join(root, f)
                    dst = os.path.join(target_dir, f)
                    try:
                        if os.path.abspath(src) != os.path.abspath(dst):
                            with open(src, "rb") as r, open(dst, "wb") as w:
                                w.write(r.read())
                    except Exception as copy_err:
                        print(f"Failed to copy {src} -> {dst}: {copy_err}")
        return path
    except Exception as e:
        print(f"Failed to download dataset: {e}")
        return None


def _derive_city_from_address_series(address: pd.Series) -> pd.Series:
    """Derive city name from an Address series of strings.
    Tries to split by newline then by comma, returning the token before the comma on the last line.
    """
    def parse(addr: object) -> Optional[str]:
        if not isinstance(addr, str) or not addr.strip():
            return None
        # Normalize whitespace
        text = "\n".join([part.strip() for part in str(addr).splitlines() if part.strip()])
        last_line = text.split("\n")[-1]
        # Now split by comma to get City, ST zip
        if "," in last_line:
            city = last_line.split(",")[0].strip()
            return city or None
        # Fallback: use last tokenized word group
        return last_line.strip() or None

    series = address.apply(parse)
    # Fill any missing with 'Unknown'
    return series.fillna("Unknown")


def infer_columns(df: pd.DataFrame) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    Try to infer column names for area, average rent, and average income.
    Returns (area_col, rent_col, income_col, geometry_col?) where geometry_col is optional id/geometry.
    May add a derived area column based on Address, named 'Derived City'.
    """
    cols = {c.lower(): c for c in df.columns}

    # Prefer an Address-derived city if available
    if "address" in cols:
        derived_col = "Derived City"
        if derived_col not in df.columns:
            df[derived_col] = _derive_city_from_address_series(df[cols["address"]])
        candidate_area = derived_col
    else:
        candidate_area = None
        # Look for clear categorical area-like columns
        for key in [
            "neighborhood",
            "ward",
            "zone",
            "district",
            "city",
            "location",
            "locality",
            "area",  # keep last so that 'Avg. Area ...' is less likely to be picked
        ]:
            for k, orig in cols.items():
                if key in k:
                    # Avoid selecting 'Avg. Area ...' numeric features as area labels
                    if key == "area" and k.startswith("avg. area"):
                        continue
                    candidate_area = orig
                    break
            if candidate_area:
                break

    rent_candidates = [
        "rent", "avg_rent", "average_rent", "rent_price", "monthly_rent", "rent_per_month",
        "houseprice", "house_price", "price", "saleprice"
    ]
    income_candidates = [
        "income", "avg_income", "average_income", "median_income", "household_income"
    ]

    def find_col(cands: list[str]) -> Optional[str]:
        for cand in cands:
            for k, orig in cols.items():
                if cand in k:
                    return orig
        return None

    rent_col = find_col(rent_candidates)
    income_col = find_col(income_candidates)

    # Geometry/lat-lon optional
    geom_col = None
    for key in ["geometry", "wkt", "geojson", "geom"]:
        for k, orig in cols.items():
            if key == k:
                geom_col = orig
                break
        if geom_col:
            break

    # If lat/lon exist, we will use numeric mapping rather than polygons
    return candidate_area or df.columns[0], rent_col, income_col, geom_col


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Standardize column names (strip) but preserve original for labeling
    rename_map = {c: c.strip() for c in df.columns}
    df.rename(columns=rename_map, inplace=True)

    # Handle missing values: numeric -> median, categorical -> mode
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
        else:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mode().iloc[0])

    # Try to coerce potential numeric text columns
    for col in df.columns:
        if df[col].dtype == object:
            try:
                coerced = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
                if coerced.notna().sum() > 0 and coerced.notna().sum() >= int(0.6 * len(df)):
                    df[col] = coerced.fillna(coerced.median())
            except Exception:
                pass

    return df


def compute_affordability(df: pd.DataFrame, area_col: str, rent_col: Optional[str], income_col: Optional[str]) -> pd.DataFrame:
    df = df.copy()

    # If income is missing, estimate from price using heuristic; if rent missing, try price as proxy
    if rent_col is None:
        # Try to find price columns as proxy for rent
        price_cols = [c for c in df.columns if c.lower() in {"price", "saleprice", "houseprice", "house_price"}]
        if price_cols:
            rent_col = price_cols[0]
        else:
            # create dummy rent if not present
            df["estimated_rent"] = np.nan
            rent_col = "estimated_rent"

    # Determine annualized rent
    rent_series = pd.to_numeric(df[rent_col], errors="coerce")
    is_monthly = "month" in rent_col.lower()
    if is_monthly:
        rent_annual = rent_series * 12.0
    else:
        rent_annual = rent_series

    if income_col is None:
        # heuristic: income ~ rent * factor (e.g., 3.5x monthly rent *12)
        # If rent appears to be sale price, scale down aggressively
        series = pd.to_numeric(df[rent_col], errors="coerce")
        if series.max() and series.max() > 1e6 and not is_monthly:
            monthly_rent_est = series / 300.0  # crude conversion from sale price
        else:
            monthly_rent_est = series if is_monthly else series / 12.0
        annual_income_est = (monthly_rent_est * 12.0) * 3.5
        df["estimated_income"] = annual_income_est
        income_col = "estimated_income"

    income_series = pd.to_numeric(df[income_col], errors="coerce")

    # Compute affordability index with annualized rent / annual income
    df["affordability_index"] = (rent_annual / income_series) * 100.0

    # If dataset provides Affordability_Index, prefer it only if ours is missing
    if "Affordability_Index" in df.columns and df["affordability_index"].isna().any():
        fallback = pd.to_numeric(df["Affordability_Index"], errors="coerce")
        df["affordability_index"] = df["affordability_index"].fillna(fallback)

    # Classify
    def classify(idx: float) -> str:
        if pd.isna(idx):
            return "Unknown"
        if idx < 30:
            return "Affordable"
        if idx <= 50:
            return "Moderate"
        return "Expensive"

    df["affordability_class"] = df["affordability_index"].apply(classify)

    # Normalize column names we will use later
    standard_cols = {
        "area": area_col,
        "rent": rent_col,
        "income": income_col,
    }
    # Keep mapping metadata for app use
    df.attrs["column_mapping"] = standard_cols

    return df


def summarize_affordability(df: pd.DataFrame, area_col: str) -> pd.DataFrame:
    grouped = (
        df.groupby([area_col, "affordability_class"], dropna=False)["affordability_index"]
        .median()
        .reset_index()
        .rename(columns={"affordability_index": "median_affordability_index"})
    )
    return grouped


def recommend_actions(df: pd.DataFrame, area_col: str, top_k: int = 3) -> list[str]:
    s = df[[area_col, "affordability_index"]].dropna()
    if s.empty:
        return ["Insufficient data to generate recommendations."]
    worst = s.sort_values("affordability_index", ascending=False).head(top_k)
    recs = []
    for _, row in worst.iterrows():
        area = row[area_col]
        idx = row["affordability_index"]
        recs.append(
            f"{area} shows high housing stress (affordability index={idx:.1f}). Prioritize affordable units near major transit and schools."
        )
    return recs


def load_first_csv_in_dir(data_dir: str) -> Optional[str]:
    # Prefer a Mumbai-specific CSV if present
    candidates = []
    for name in os.listdir(data_dir):
        if name.lower().endswith(".csv"):
            candidates.append(name)
    if not candidates:
        return None
    # Prefer explicit Mumbai file
    for name in candidates:
        if "mumbai_housing_affordability.csv" == name:
            return os.path.join(data_dir, name)
    # Prefer any csv mentioning mumbai
    for name in candidates:
        if "mumbai" in name.lower():
            return os.path.join(data_dir, name)
    # Fallback to a deterministic first
    for name in sorted(candidates):
        return os.path.join(data_dir, name)
    return None


def load_dataset(data_dir: str) -> Tuple[pd.DataFrame, str]:
    csv_path = load_first_csv_in_dir(data_dir)
    if not csv_path:
        raise FileNotFoundError("No CSV found in data directory.")
    df = pd.read_csv(csv_path)
    return df, csv_path


def load_or_download_dataset(base_dir: str) -> Tuple[pd.DataFrame, str]:
    data_dir = ensure_data_dir(base_dir)
    # Try local first
    try:
        df, path = load_dataset(data_dir)
    except Exception:
        # Attempt download
        download_kaggle_dataset(data_dir)
        df, path = load_dataset(data_dir)
    return df, path


def estimate_struggling(df: pd.DataFrame, area_col: str, threshold: float = 50.0) -> TypingTuple[int, float, pd.DataFrame]:
    """Estimate households struggling with affordability overall and per-area.

    Returns: (overall_count, overall_pct, per_area_df) where per_area_df has columns:
    [area_col, 'struggling_count', 'total', 'struggling_pct']
    """
    series = pd.to_numeric(df["affordability_index"], errors="coerce")
    overall_total = int(series.notna().sum())
    overall_count = int((series > threshold).sum())
    overall_pct = (overall_count / overall_total) if overall_total else 0.0
    per_area = (
        df.assign(_struggling=series > threshold)
        .groupby(area_col)
        .agg(struggling_count=("_struggling", "sum"), total=("_struggling", "count"))
        .reset_index()
    )
    per_area["struggling_pct"] = per_area.apply(lambda r: (r["struggling_count"] / r["total"]) if r["total"] else 0.0, axis=1)
    return overall_count, overall_pct, per_area
