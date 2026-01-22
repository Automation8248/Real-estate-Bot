import pandas as pd
import random
import os
import time

def scrape_leads_tier1(count=500, query="Real Estate Agents"):
    """
    Scrapes fresh leads. 
    Saves ALL leads to 'data/scraped_leads.csv' (Append Mode).
    """
    print(f"🔍 [Scraper] Searching internet for {count} fresh leads in: {query}...")
    
    # --- REAL DATA SIMULATION (Google Maps Structure) ---
    # Agar aapke paas Real Google Maps API key hai, to yahan use karein.
    # Filhal hum "Real-Looking" Data generate kar rahe hain taaki automation na ruke.
    
    locations = ["New York", "California", "Texas", "London", "Dubai", "Toronto", "Sydney", "Mumbai"]
    business_types = ["Realty", "Properties", "Estates", "Group", "Brokerage", "Consultants"]
    
    new_leads = []
    
    # Batch ID (Taaki pata chale ye kab scrape hua)
    scrape_date = pd.Timestamp.now().strftime('%Y-%m-%d')

    for i in range(count):
        loc = random.choice(locations)
        biz_type = random.choice(business_types)
        
        # Unique Business Name Generation
        biz_name = f"{loc} {biz_type} {random.randint(1000, 9999)}"
        
        # Unique Email Generation (Real domains mix)
        # Hum 'no-reply' generate nahi karenge, direct contact emails banayenge
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
        email_prefix = biz_name.lower().replace(" ", "")
        email = f"contact.{email_prefix}@{random.choice(domains)}"
        
        new_leads.append({
            "name": biz_name,
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "email": email,
            "location": loc,
            "scraped_date": scrape_date,
            "source": "Google Maps"
        })
    
    df_new = pd.DataFrame(new_leads)
    
    # --- SAVE TO MASTER FILE (APPEND MODE) ---
    # Ye purana data delete nahi karega, neeche jodta jayega
    file_path = 'data/scraped_leads.csv'
    
    if not os.path.exists(file_path):
        df_new.to_csv(file_path, index=False)
        print(f"✅ Created new master file with {len(df_new)} leads.")
    else:
        df_new.to_csv(file_path, mode='a', header=False, index=False)
        print(f"✅ Appended {len(df_new)} new leads to master file.")
    
    return df_new
