import pandas as pd
import requests
import os
import time
from datetime import datetime

RAW_FILE = "data/ura_raw_master.csv"
OUTPUT_FILE = "data/ura_processed_data.csv"

# Helper function to convert URA date formats (like "Mar-21" or "03/21") to standard YYYY-MM
def parse_ura_date(date_str):
    try:
        date_str = str(date_str).strip()
        # Try format: "Mar-21" or "Mar-2021"
        for fmt in ('%b-%y', '%b-%Y', '%m/%y', '%m/%Y'):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m'), dt.year
            except ValueError:
                continue
        return "N/A", "N/A"
    except Exception:
        return "N/A", "N/A"

# 1. Initialize or Load Progress
if os.path.exists(OUTPUT_FILE):
    print("🔄 Found existing processed URA data. Resuming progress...")
    processed_df = pd.read_csv(OUTPUT_FILE)
    processed_df['lookup_key'] = processed_df['project_name'].fillna('') + "_" + processed_df['street_name'].fillna('')
    geo_cache = processed_df.set_index('lookup_key')[['lat', 'lon']].dropna().to_dict('index')
else:
    print("🆕 Starting fresh URA geocoding pipeline...")
    processed_df = pd.DataFrame()
    geo_cache = {}

if not os.path.exists(RAW_FILE):
    print(f"❌ Error: {RAW_FILE} not found.")
    exit()

# Read the raw file with your exact casing headers
raw_df = pd.read_csv(RAW_FILE, encoding='latin1')

# Form unique location mapping keys using exact raw headers
raw_df['lookup_key'] = raw_df['Project Name'].fillna('') + "_" + raw_df['Street Name'].fillna('')

if not processed_df.empty:
    done_keys = processed_df[processed_df['lat'].notna() & (processed_df['lat'] != 'N/A')]['lookup_key'].unique()
    rows_to_process = raw_df[~raw_df['lookup_key'].isin(done_keys)].copy()
    print(f"⏩ Skipped {len(raw_df) - len(rows_to_process):,} already processed rows.")
else:
    rows_to_process = raw_df.copy()

print(f"🚀 Total remaining URA rows to process: {len(rows_to_process):,}")

# 2. Geocoding Loop
updated_rows = []
counter = 0

for idx, row in rows_to_process.iterrows():
    key = row['lookup_key']
    proj = str(row['Project Name']) if pd.notna(row['Project Name']) else ""
    street = str(row['Street Name']) if pd.notna(row['Street Name']) else ""
    
    # Parse date formats safely on the fly
    month_val, year_val = parse_ura_date(row['Sale Date'])

    # Build standardized output dictionary row structured for dashboard compatibility
    out_row = {
        'project_name': proj,
        'street_name': street,
        'block': '', # Left blank safely as URA embeds details into street/project locations
        'resale_price': float(str(row['Transacted Price ($)']).replace(',', '')),
        'month': month_val,
        'year': year_val,
        'storey_range': str(row['Floor Level']) if pd.notna(row['Floor Level']) else 'N/A',
        'flat_type': str(row['Property Type']) if pd.notna(row['Property Type']) else 'Private',
        'flat_model': str(row['property_group']) if pd.notna(row['property_group']) else 'Private',
        'lookup_key': key,
        'town': str(row['Postal District']) if pd.notna(row['Postal District']) else 'N/A'
    }

    # Extract coordinates or make OneMap API calls
    if key in geo_cache:
        out_row['lat'] = geo_cache[key]['lat']
        out_row['lon'] = geo_cache[key]['lon']
    else:
        search_query = f"{proj} {street} Singapore" if proj else f"{street} Singapore"
        try:
            url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={search_query}&returnGeom=Y&getAddrDetails=N&pageNum=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['found'] > 0:
                result = data['results'][0]
                lat, lon = result['LATITUDE'], result['LONGITUDE']
            else:
                lat, lon = "N/A", "N/A"
        except Exception:
            lat, lon = "N/A", "N/A"
            
        geo_cache[key] = {'lat': lat, 'lon': lon}
        out_row['lat'] = lat
        out_row['lon'] = lon
        time.sleep(0.1) # Safe API breathing delay

    updated_rows.append(out_row)
    counter += 1
    
    # Save checkpoint batches to disk every 500 rows
    if counter % 500 == 0:
        batch_df = pd.DataFrame(updated_rows)
        if os.path.exists(OUTPUT_FILE):
            master_df = pd.read_csv(OUTPUT_FILE)
            master_df = pd.concat([master_df, batch_df], ignore_index=True).drop_duplicates(subset=['lookup_key', 'month', 'resale_price'])
            master_df.to_csv(OUTPUT_FILE, index=False)
        else:
            batch_df.to_csv(OUTPUT_FILE, index=False)
            
        print(f"💾 Checkpoint saved: Processed {counter}/{len(rows_to_process)} records...")
        updated_rows = []

# Final structural save
if updated_rows:
    batch_df = pd.DataFrame(updated_rows)
    if os.path.exists(OUTPUT_FILE):
        master_df = pd.read_csv(OUTPUT_FILE)
        master_df = pd.concat([master_df, batch_df], ignore_index=True).drop_duplicates(subset=['lookup_key', 'month', 'resale_price'])
        master_df.to_csv(OUTPUT_FILE, index=False)
    else:
        batch_df.to_csv(OUTPUT_FILE, index=False)

print("🎉 URA Geocoding pipeline complete! data/ura_processed_data.csv is fully ready.")