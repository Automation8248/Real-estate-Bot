import pandas as pd
import random
from core.scraper import scrape_leads_tier1 # Custom scraper function
from core.ai_agent import generate_cold_email
from core.email_manager import send_email
from core.telegram_bot import send_msg_alert

def daily_workflow():
    # 1. Scrape 500+ Leads
    print("Scraping Leads...")
    new_leads = scrape_leads_tier1(count=500) # Returns DataFrame
    new_leads.to_csv('data/scraped_leads.csv', mode='a', header=False, index=False)
    send_msg_alert(f"✅ Daily Task: 500 Leads Scraped & Saved.")

    # 2. Select 15 Businesses to Message
    targets = pd.read_csv('data/business_targets.csv')
    history = pd.read_csv('data/history.csv')
    
    # Filter jo pehle send nahi huye
    fresh_targets = targets[~targets['email'].isin(history['email'])].head(15)

    for index, row in fresh_targets.iterrows():
        email = row['email']
        name = row['name']
        
        # AI generate email
        email_body = generate_cold_email(name)
        
        # Send Email
        try:
            send_email(email, "Real Estate Leads Opportunity", email_body)
            
            # Update History
            with open('data/history.csv', 'a') as f:
                f.write(f"{email},{pd.Timestamp.now()}\n")
                
        except Exception as e:
            print(f"Error sending to {email}: {e}")

if __name__ == "__main__":
    daily_workflow()
