import requests
import pandas as pd

def fetch_latest_data_from_gov(resource_id: str):
    """
    Fetches raw data from data.gov.sg API.
    Resource IDs can be found on the data.gov.sg dataset page.
    """
    base_url = "https://data.gov.sg/api/action/datastore_search"
    params = {'resource_id': resource_id, 'limit': 10000} # Adjust limit as needed
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        records = response.json()['result']['records']
        return pd.DataFrame(records)
    else:
        return pd.DataFrame() # Handle error accordingly

# Usage: 
# ura_data = fetch_latest_data_from_gov("YOUR_URA_RESOURCE_ID")