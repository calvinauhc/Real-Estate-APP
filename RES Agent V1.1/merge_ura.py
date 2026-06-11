import pandas as pd
import os

# 1. Define the files dictionary (This is what was missing!)
files = {
    "Condo/Apartment": "data/URA_apartment_condo.csv",
    "Executive Condominium": "data/URA_EC.csv",
    "Landed": "data/URA_landed.csv",
    "Strata Landed": "data/URA_strata.csv"
}

combined_list = []

# 2. Loop through and merge with fallback encoding protection
for group_name, file_path in files.items():
    if os.path.exists(file_path):
        print(f"Processing {group_name}...")
        try:
            # Try reading with standard encoding first
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # Fallback to Latin1/CP1252 if it hits special characters
            print(f"⚠️  UTF-8 decoding failed for {group_name}. Retrying with Latin1 encoding...")
            df = pd.read_csv(file_path, encoding='latin1')
        
        # Add a tag so your dashboard knows what type of private property it is
        df['property_group'] = group_name
        combined_list.append(df)
    else:
        print(f"⚠️ Warning: {file_path} not found, skipping.")

# 3. Save the master file
if combined_list:
    ura_master = pd.concat(combined_list, ignore_index=True)
    ura_master.to_csv("data/ura_raw_master.csv", index=False)
    print(f"\n🎉 Success! Combined {len(ura_master):,} records into data/ura_raw_master.csv")
else:
    print("\n❌ Error: No URA files were found. Check your file path names inside data/!")