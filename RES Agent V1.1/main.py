import csv
import time
import os
import streamlit as st
from layers.geocoder import get_coordinates

def run_pipeline(input_path, output_path):
    """Processes raw resale data, dynamically appends coordinate layers, and safely exports rows."""
    
    # 🛑 Crucial Check: If processed data already exists, skip processing to avoid freezing the UI on start
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return
        
    processed_data = []
    
    if not os.path.exists(input_path):
        st.error(f"❌ Input raw data file not found at: {input_path}")
        return

    # 1. Read and process incoming raw records
    with open(input_path, mode='r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        # Ensure our target headers list accounts for coordinate tracking
        if 'latitude' not in fieldnames:
            fieldnames.append('latitude')
        if 'longitude' not in fieldnames:
            fieldnames.append('longitude')

        for row in reader:
            # 🌍 RE-INTEGRATED: Geocoding Lookup Layer
            block = row.get('block', '')
            street = row.get('street_name', '')
            
            try:
                # Look up spatial data points
                coords = get_coordinates(block, street)
                if coords:
                    row['latitude'] = coords[0]
                    row['longitude'] = coords[1]
                else:
                    row['latitude'] = ""
                    row['longitude'] = ""
            except Exception:
                row['latitude'] = ""
                row['longitude'] = ""
            
            # API pacing buffer to prevent OneMap network blocks
            time.sleep(0.01)
            processed_data.append(row)
            
    # 2. Write rows out safely while dropping rogue 'None' keys
    with open(output_path, mode='w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for row in processed_data:
            # Drop any phantom keys that aren't strings
            sanitized_row = {k: v for k, v in row.items() if k is not None}
            writer.writerow(sanitized_row)

# --- APPLICATION BOOT EXECUTION FLOW ---
if __name__ == "__main__":
    # Ensure your data folders exist
    os.makedirs('data', exist_ok=True)
    
    # Run data preparation pipeline safely
    run_pipeline('data/resale_prices.csv', 'data/processed_data.csv')