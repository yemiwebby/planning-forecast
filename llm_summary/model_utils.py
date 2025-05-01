import pandas as pd

def extract_forecast_data(df, year: str, region: str) -> dict:
    year = str(year)
    filtered = df[df["LAD23NM"].str.lower() == region.lower()]
    if filtered.empty:
        raise ValueError("Region not found.")

    row = filtered.iloc[0]
    return {
        "housing_price": row.get(f"{year}_housing_price"),
        "housing_price_ci_lower": row.get(f"{year}_housing_price_ci_lower"),
        "housing_price_ci_upper": row.get(f"{year}_housing_price_ci_upper"),
        "affordability": row.get(f"{year}_housing_affordability"),
        "affordability_ci_lower": row.get(f"{year}_housing_affordability_ci_lower"),
        "affordability_ci_upper": row.get(f"{year}_housing_affordability_ci_upper"),
        "dwellings": row.get(f"{year}_net_additional_dwellings"),
        "dwellings_ci_lower": row.get(f"{year}_net_additional_dwellings_ci_lower"),
        "dwellings_ci_upper": row.get(f"{year}_net_additional_dwellings_ci_upper"),
    }