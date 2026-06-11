import pandas as pd
import os

def process_raw_data():
    raw_path = "data/raw"
    
    # 1. Process HDB
    hdb_df = pd.read_csv(os.path.join(raw_path, "resale_prices.csv"))
    hdb_df['price_psf'] = hdb_df['resale_price'] / (hdb_df['floor_area_sqm'] * 10.7639)
    # Ensure HDB has a postal sector (if missing, you'd map town here)
    hdb_df['postal_sector'] = hdb_df['postal_sector'].astype(str)
    hdb_df['comparison_key'] = "HDB-Flat-99-year Leasehold"
    
    # 2. Process URA
    ura_df = pd.read_csv(os.path.join(raw_path, "URA_apartment_condo.csv"))
    ura_df['price_psf'] = pd.to_numeric(ura_df['Unit Price ($ PSF)'].replace(',', '', regex=True))
    ura_df['postal_sector'] = ura_df['Postal District'].astype(str).str.replace('D', '', regex=False)
    
    # Build a specific key: e.g., "Private-Condominium-Freehold"
    ura_df['comparison_key'] = (
        "Private-" + 
        ura_df['Property Type'].astype(str) + "-" + 
        ura_df['Tenure'].astype(str)
    )

    # 3. Consolidate and Group
    master_df = pd.concat([
        hdb_df[['postal_sector', 'comparison_key', 'price_psf']], 
        ura_df[['postal_sector', 'comparison_key', 'price_psf']]
    ])
    
    summary = master_df.groupby(['postal_sector', 'comparison_key'])['price_psf'].median().reset_index()
    summary.to_csv("data/avg_valuation_ref.csv", index=False)
    print("Valuation engine updated with multi-tier classification.")

if __name__ == "__main__":
    process_raw_data()