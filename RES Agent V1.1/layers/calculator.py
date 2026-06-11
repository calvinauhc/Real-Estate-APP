import pandas as pd
import os

# 1. Load data once globally
DATA_PATH = "/Users/chuafamily/RES app dev/Real-Estate-APP/RES Agent V1.1/data/resale_prices.csv"

def get_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV file not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    # 2. Convert to numeric to ensure math works
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    df['floor_area_sqm'] = pd.to_numeric(df['floor_area_sqm'], errors='coerce')
    return df

# Initialize data
df = get_data()

def get_avg_price_by_town(town_name):
    """Calculates average resale price for a specific town."""
    town_data = df[df['town'] == town_name.upper()]
    if town_data.empty:
        return None
    return town_data['resale_price'].mean()

def get_avg_psm_by_town(town_name):
    """Calculates average price per square meter for a town."""
    town_data = df[df['town'] == town_name.upper()]
    if town_data.empty:
        return None
    
    # Calculate PSF/PSM for each row, then average
    town_data = town_data.copy()
    town_data['psm'] = town_data['resale_price'] / town_data['floor_area_sqm']
    return town_data['psm'].mean()

# Simple CLI test
if __name__ == "__main__":
    town = input("Enter town name: ")
    price = get_avg_price_by_town(town)
    psm = get_avg_psm_by_town(town)
    
    if price:
        print(f"\n--- Results for {town.upper()} ---")
        print(f"Average Price: ${price:,.2f}")
        print(f"Average Price per SQM: ${psm:,.2f}")
    else:
        print("Town not found. Please check your spelling.")