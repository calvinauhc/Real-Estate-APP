# This KeyError: 'project_name' means your URA files are missing a column named exactly "project_name".
# Diagnosing Your Exact Header Titles: Create a small temporary script named check_headers.py in your root directory:
import pandas as pd

try:
    df = pd.read_csv("data/ura_raw_master.csv", encoding='latin1', nrows=3)
    print("📁 Your Raw URA Dataset Headers are:")
    print(list(df.columns))
except Exception as e:
    print(f"❌ Could not read master file: {e}")