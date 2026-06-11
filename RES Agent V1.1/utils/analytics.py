# The Architecture
import numpy as np
import pandas as pd

def calculate_haversine_distance_vectorized(target_lat, target_lon, lat_series, lon_series):
    """
    Computes distance in meters using vectorized numpy operations for optimal performance.
    """
    R = 6371000  # Radius of Earth in meters
    
    # Convert degrees to radians
    phi1 = np.radians(target_lat)
    phi2 = np.radians(lat_series)
    delta_phi = np.radians(lat_series - target_lat)
    delta_lambda = np.radians(lon_series - target_lon)
    
    # Haversine matrix formula
    a = np.sin(delta_phi / 2.0)**2 + \
        np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    
    return R * c

def extract_cma_insights(target_lat, target_lon, target_sqft, target_type, historical_df, size_tolerance=0.15):
    """
    Finds historical transaction matches within 500m over the past 5 years 
    matching exactly the property type and roughly the same square footage footprints.
    """
    if historical_df is None or historical_df.empty:
        return None, 0.0, 0
        
    df_filtered = historical_df.copy()
    
    # 1. ENFORCE STRICT SEPARATION: HDB vs HDB / Condo vs Condo
    # Checks if your data column is named 'property_type' or if we map flat types
    if 'property_type' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['property_type'].astype(str).str.upper() == target_type.upper()]
    
    # 2. TIME HORIZON FILTER: Limit strictly to past 5 years relative to the maximum dataset year
    if 'year' in df_filtered.columns:
        max_dataset_year = df_filtered['year'].max()
        df_filtered = df_filtered[df_filtered['year'] >= (max_dataset_year - 5)]
        
    # 3. SIZE Footprint Tolerance Filter (e.g., +/- 15% sqft window match)
    # Assumes your historical data is standard mapped to a 'floor_area_sqm' or 'sqft' column
    size_col = 'floor_area_sqm' if 'floor_area_sqm' in df_filtered.columns else 'sqft'
    
    min_size = target_sqft * (1 - size_tolerance)
    max_size = target_sqft * (1 + size_tolerance)
    df_filtered = df_filtered[(df_filtered[size_col] >= min_size) & (df_filtered[size_col] <= max_size)]
    
    if df_filtered.empty:
        return df_filtered, 0.0, 0

    # 4. FAST VECTORIZED RADIUS CALCULATION
    df_filtered['distance_meters'] = calculate_haversine_distance_vectorized(
        target_lat, target_lon, df_filtered['lat'], df_filtered['lon']
    )
    
    # Filter only listings within the 500m threshold fence
    df_cma_final = df_filtered[df_filtered['distance_meters'] <= 500.0].copy()
    
    if df_cma_final.empty:
        return df_cma_final, 0.0, 0
        
    # 5. COMPUTE MEDIAN METRIC
    median_price = float(df_cma_final['resale_price'].median())
    total_matches = len(df_cma_final)
    
    return df_cma_final, median_price, total_matches
