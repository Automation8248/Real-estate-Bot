import pandas as pd
import random

def scrape_leads_tier1(count=5, query="Real Estate Agents"):
    """
    Simulates scraping real estate leads.
    Args:
        count: Number of leads to generate.
        query: Search query (e.g., 'Real Estate Agents in New York')
    """
    print(f"🔍 Scraping started for: {query}...")
    
    # Logic: Agar query mein location hai to use extract karo, nahi to 'Premium Market'
    location = query.replace("Real Estate Agents in ", "") if "in" in query else "Premium Market"
    
    leads = []
    names = ["Realty", "Estates", "Properties", "Group", "Homes", "Brokerage"]
    
    for i in range(count):
        # Fake Data Generation (Real scraping logic yahan replace hoga)
        biz_name = f"{location} {random.choice(names)} {random.randint(100, 999)}"
        phone = f"+1-555-01{random.randint(10, 99)}"
        email = f"contact@{biz_name.lower().replace(' ', '')}.com"
        
        leads.append({
            "name": biz_name,  # 'name' column match hona chahiye target list se
            "phone": phone,
            "email": email,
            "location": location
        })
    
    print(f"✅ Found {len(leads)} leads.")
    return pd.DataFrame(leads)
