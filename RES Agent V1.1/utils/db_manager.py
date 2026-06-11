import sqlite3
import os

# 🛠️ ADD THIS LINE RIGHT HERE AT THE TOP:
DB_PATH = "agency_app.db"

def init_db():
    """Initializes the SQLite database, builds core operational tables, and seeds a balanced mix of profiles."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create the Client Profiles Table (Fully Verified SQLite Syntax)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_profiles (
        client_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        citizenship TEXT,
        current_properties_count INTEGER,
        cash_savings REAL,
        cpf_ordinary_account REAL,
        cpf_accrued_interest REAL,
        loan_eligibility REAL,
        ownership_structure TEXT
    )
    """)
    
    # 2. Create the Client Targets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_targets (
        client_id TEXT PRIMARY KEY,
        property_type TEXT,
        target_price REAL,
        estimated_selling_price REAL,
        outstanding_loan_old REAL,
        FOREIGN KEY(client_id) REFERENCES client_profiles(client_id)
    )
    """)
    
    # 3. Seed Fresh, Balanced Market Records (HDB, Condo, and Landed)
    # Using INSERT OR REPLACE so it cleanly rewrites or updates existing test data arrays
    
    # --- Profile 1: The HDB Upgrader ---
    cursor.execute("""
    INSERT OR REPLACE INTO client_profiles VALUES (
        'C001', 'Ali Bin Osman', 'SC', 1, 80000.0, 120000.0, 25000.0, 550000.0, 'Single'
    )""")
    cursor.execute("""
    INSERT OR REPLACE INTO client_targets VALUES (
        'C001', 'HDB', 650000.0, 450000.0, 180000.0
    )""")
    
    # --- Profile 2: The Private Condo Buyer ---
    cursor.execute("""
    INSERT OR REPLACE INTO client_profiles VALUES (
        'C002', 'Marcus & Evelyn', 'SC', 0, 150000.0, 220000.0, 0.0, 1400000.0, 'Joint Tenancy|Evelyn|SC|1|0.0|No|None'
    )""")
    cursor.execute("""
    INSERT OR REPLACE INTO client_targets VALUES (
        'C002', 'Condo', 1600000.0, 0.0, 0.0
    )""")
    
    # --- Profile 3: The High Net Worth Landed Buyer ---
    cursor.execute("""
    INSERT OR REPLACE INTO client_profiles VALUES (
        'C003', 'Dr. Eric Tan', 'SC', 1, 600000.0, 350000.0, 0.0, 2400000.0, 'Single'
    )""")
    cursor.execute("""
    INSERT OR REPLACE INTO client_targets VALUES (
        'C003', 'Landed', 4200000.0, 0.0, 0.0
    )""")
    
    conn.commit()
    conn.close()