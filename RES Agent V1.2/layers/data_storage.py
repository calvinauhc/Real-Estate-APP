# layers/data_storage.py

import os

# Define the Base Path for V1.2
BASE_DATA_PATH = "data/raw/crm"

# File paths
AGENTS_FILE = os.path.join(BASE_DATA_PATH, "agents.csv")
USERS_FILE = os.path.join(BASE_DATA_PATH, "users.csv")
CLIENTS_FILE = os.path.join(BASE_DATA_PATH, "clients.csv")

def _ensure_dir():
    if not os.path.exists(BASE_DATA_PATH):
        os.makedirs(BASE_DATA_PATH)