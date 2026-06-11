import sqlite3

def init_db():
    conn = sqlite3.connect("real_estate_star.db")
    cursor = conn.cursor()
    
    # 1. Create dim_properties
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_properties (
        property_dim_key TEXT PRIMARY KEY,
        project_name TEXT NOT NULL,
        property_type TEXT,
        built_year INT,
        total_room_count TEXT,
        tenure_type TEXT,
        postal_sector TEXT
    );
    """)
    
    # 2. Create dim_districts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_districts (
        district_dim_key TEXT PRIMARY KEY,
        planning_area_name TEXT,
        region_zone TEXT
    );
    """)
    
    # 3. Create dim_calendar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_calendar (
        calendar_dim_key INT PRIMARY KEY,
        transaction_year INT,
        quarter TEXT,
        month_number INT
    );
    """)
    
    # 4. Create central fact_transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_transactions (
        transaction_id TEXT PRIMARY KEY,
        property_dim_key TEXT,
        district_dim_key TEXT,
        calendar_dim_key INT,
        final_resale_price REAL,
        psf REAL,
        FOREIGN KEY (property_dim_key) REFERENCES dim_properties(property_dim_key),
        FOREIGN KEY (district_dim_key) REFERENCES dim_districts(district_dim_key),
        FOREIGN KEY (calendar_dim_key) REFERENCES dim_calendar(calendar_dim_key)
    );
    """)
    
    # Seed static districts mapping table
    districts_seed = [
        ("D09", "Orchard / River Valley", "CCR"),
        ("D10", "Bukit Timah / Holland", "CCR"),
        ("D15", "Katong / Marine Parade", "RCR"),
        ("D19", "Serangoon / Punggol", "OCR"),
        ("D23", "Bukit Panjang / Choa Chu Kang", "OCR")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dim_districts VALUES (?, ?, ?);", districts_seed)
    
    conn.commit()
    conn.close()
    print("✨ Database initialized with dimension constraints successfully.")

if __name__ == "__main__":
    init_db()
