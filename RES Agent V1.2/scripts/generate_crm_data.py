# scripts/generate_crm_data.py
import pandas as pd
import numpy as np
import csv

def generate_mock_clients(n=100):
    data = {
        'client_id': range(1, n + 1),
        'client_name': [f"Client_{i}" for i in range(1, n + 1)],
        'monthly_income': np.random.uniform(5000, 20000, n),
        'citizenship': np.random.choice(['Singaporean', 'SPR'], n)
    }
    df = pd.DataFrame(data)
    # Essential: Use quoting=csv.QUOTE_ALL as per architectural standards
    df.to_csv('data/raw/crm/clients.csv', index=False, quoting=csv.QUOTE_ALL)
    print("Vault updated: clients.csv generated successfully.")

if __name__ == "__main__":
    generate_mock_clients()