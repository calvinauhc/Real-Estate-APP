import os
import requests
from dotenv import load_dotenv

load_dotenv()

COORDINATE_CACHE = {}
ACCESS_TOKEN = None

def get_valid_token():
    global ACCESS_TOKEN
    email = os.getenv("ONEMAP_EMAIL")
    password = os.getenv("ONEMAP_PASSWORD")
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    response = requests.post(url, json={"email": email, "password": password})
    if response.status_code == 200:
        ACCESS_TOKEN = response.json().get("access_token")
        return ACCESS_TOKEN
    raise Exception("Auth failed. Check .env credentials.")

def get_coordinates(search_value):
    global ACCESS_TOKEN
    
    # Clean up the address format for OneMap
    search_value = str(search_value).upper().strip()
    search_value = search_value.replace("STREET", "ST").replace("AVENUE", "AVE").replace("ROAD", "RD")
    
    # Check cache first to avoid repeating API calls for identical addresses
    if search_value in COORDINATE_CACHE:
        return COORDINATE_CACHE[search_value]
    
    if not ACCESS_TOKEN:
        get_valid_token()
        
    url = "https://www.onemap.gov.sg/api/common/elastic/search"
    params = {"searchVal": search_value, "returnGeom": "Y", "getAddrDetails": "Y"}
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if data.get("error") and "expired" in str(data["error"]).lower():
        print("Token expired. Refreshing...")
        get_valid_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
    if data.get("found", 0) > 0:
        result = data["results"][0]
        coords = (float(result["LATITUDE"]), float(result["LONGITUDE"]))
        # Save to cache
        COORDINATE_CACHE[search_value] = coords
        return coords
        
    return None

# =====================================================================
# HDB MASTER RUNNER BLOCK
# =====================================================================
if __name__ == "__main__":
    import pandas as pd
    import sys
    import time

    # 1. Define your data paths (Adjust folder/filename if your HDB csv matches a different name)
    csv_path = "data/resale_prices.csv" 
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: Could not find your HDB CSV data file at: '{csv_path}'")
        print("Please check if your file is in the 'data' folder and named correctly.")
        sys.exit(1)
        
    print(f"📖 Loading HDB dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # 2. Ensure latitude and longitude tracking columns exist in the CSV
    if "latitude" not in df.columns:
        df["latitude"] = None
    if "longitude" not in df.columns:
        df["longitude"] = None

    # 3. Identify completed vs remaining rows
    # Rows are skipped if BOTH latitude and longitude are already filled
    completed_mask = df["latitude"].notna() & df["longitude"].notna()
    skipped_count = len(df[completed_mask])
    
    # Rows to process are those where latitude or longitude is missing/null
    to_process_df = df[~completed_mask]
    remaining_count = len(to_process_df)
    
    print(f"✅ Skipped {skipped_count:,} already completed rows.")
    print(f"🚀 Found {remaining_count:,} remaining rows requiring OneMap geolocation.")
    
    if remaining_count == 0:
        print("🎉 All rows are fully geocoded! Nothing left to do.")
        sys.exit(0)

    print("⚡ Starting geocoding run. Press Ctrl+C at any time to pause safely.\n")
    
    processed_counter = 0
    checkpoint_every = 100  # Automatically saves progress to disk every 100 rows
    
    try:
        # Group by block and street address to avoid redundant API hits for units in the same block
        for index, row in to_process_df.iterrows():
            # Construct standard HDB search string: e.g., "123 ANG MO KIO AVE 4"
            block = str(row.get("block", "")).strip()
            street = str(row.get("street_name", "")).strip()
            address_query = f"{block} {street}"
            
            if not block or not street:
                continue
                
            # Call our utility function
            coords = get_coordinates(address_query)
            
            if coords:
                df.at[index, "latitude"] = coords[0]
                df.at[index, "longitude"] = coords[1]
                print(f"📌 [{processed_counter + 1}/{remaining_count}] Resolved: {address_query} -> {coords}")
            else:
                print(f"⚠️ [{processed_counter + 1}/{remaining_count}] Not Found on OneMap: {address_query}")
                
            processed_counter += 1
            
            # Tiny sleep interval to stay clear of OneMap API rate limiting limits
            time.sleep(0.1)
            
            # Periodic incremental file save protection block
            if processed_counter % checkpoint_every == 0:
                df.to_csv(csv_path, index=False)
                print(f"💾 Autosave Checkpoint: Committed last {checkpoint_every} rows safely to disk.")
                
    except KeyboardInterrupt:
        print("\n🛑 Pause signal received! Wrapping up current row and saving progress safely...")
    finally:
        # Final save guard when loop ends or gets interrupted
        df.to_csv(csv_path, index=False)
        print(f"💾 File updated successfully. Added {processed_counter:,} new rows to your database.")