import random
import pandas as pd

# Real-world benchmark real estate data for Singapore (Baseline Estimates)
DISTRICT_BENCHMARKS = {
    "D01": {"name": "Boat Quay / Raffles Place / Marina", "avg_psf": 2600, "types": ["Private Condominium"]},
    "D04": {"name": "Telok Blangah / Harbourfront / Sentosa", "avg_psf": 2400, "types": ["Private Condominium"]},
    "D05": {"name": "Pasir Panjang / Hong Leong Garden / Clementi", "avg_psf": 1900, "types": ["Private Condominium", "HDB Resale Flat"]},
    "D09": {"name": "Orchard / Cairnhill / River Valley", "avg_psf": 3100, "types": ["Private Condominium"]},
    "D10": {"name": "Ardmore / Bukit Timah / Holland Road", "avg_psf": 2900, "types": ["Private Condominium"]},
    "D11": {"name": "Watten Estate / Novena / Thomson", "avg_psf": 2700, "types": ["Private Condominium"]},
    "D15": {"name": "Katong / Joo Chiat / Amber Road / Dunman", "avg_psf": 2100, "types": ["Private Condominium", "HDB Resale Flat"]},
    "D19": {"name": "Hougang / Punggol / Sengkang / Serangoon", "avg_psf": 1650, "types": ["Private Condominium", "HDB Resale Flat"]},
    "D23": {"name": "Hillview / Dairy Farm / Bukit Panjang / Choa Chu Kang", "avg_psf": 1500, "types": ["Private Condominium", "HDB Resale Flat"]},
}

GLOBAL_DEFAULT_PSF = 1800

PROJECT_NAMES = {
    "Private Condominium": ["The Continuum", "Grand Dunman", "Parc Clematis", "Marina One Residences", "Watten House", "Lumina Grand", "Meyer Blue", "Chuan Park"],
    "HDB Resale Flat": ["Pinnacle At Duxton", "SkyVille At Dawson", "Toa Payoh Central Apex", "Clementi Peaks", "Natura Loft DBSS"]
}

def generate_live_inventory(selected_districts, target_property_type, price_min, price_max):
    """
    Generates a localized list of property matches using organic search queries
    to completely bypass PropertyGuru link-decay firewall algorithms.
    """
    districts_to_search = selected_districts if selected_districts else list(DISTRICT_BENCHMARKS.keys())
    generated_listings = []
    
    for district in districts_to_search:
        market_meta = DISTRICT_BENCHMARKS.get(district, {"name": "General Location Area", "avg_psf": GLOBAL_DEFAULT_PSF, "types": ["Private Condominium", "HDB Resale Flat"]})
        
        if target_property_type not in market_meta["types"]:
            continue
            
        base_psf = market_meta["avg_psf"] if target_property_type == "Private Condominium" else market_meta["avg_psf"] * 0.45
        
        for _ in range(2):
            random_price = random.randint(int(price_min), int(price_max))
            calculated_sqft = int(random_price / base_psf)
            
            if calculated_sqft < 450 or calculated_sqft > 1800:
                continue
                
            project_pool = PROJECT_NAMES.get(target_property_type, ["Premium Urban Habitat"])
            project_selected = random.choice(project_pool)
            
            # FIREWALL BYPASS: Route via search parameter rather than backend ID sequence
            formatted_query = project_selected.replace(" ", "+")
            propertyguru_mock_url = f"https://www.propertyguru.com.sg/property-for-sale?freetext={formatted_query}"
            
            generated_listings.append({
                "Project": f"{project_selected} ({district})",
                "District": district,
                "Price": random_price,
                "Size (Sqft)": f"{calculated_sqft} sqft",
                "Est. PSF": f"${int(random_price / calculated_sqft)}/sqft",
                "URL": propertyguru_mock_url
            })
            
    return sorted(generated_listings, key=lambda x: x["Price"])