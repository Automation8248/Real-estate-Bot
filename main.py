import pandas as pd
from datetime import datetime, timedelta
from core.scraper import scrape_leads_tier1
from core.ai_agent import generate_cold_email
from core.email_manager import send_email
from core.telegram_bot import send_msg_alert

def daily_workflow():
    # --- PART 1: DAILY LEAD SCRAPING ---
    print("Scraping Leads...")
    # (Scraping logic same as before)
    
    # --- PART 2: SEND NEW EMAILS (15/Day) ---
    targets = pd.read_csv('data/business_targets.csv')
    
    # Load history properly with dates
    try:
        history = pd.read_csv('data/history.csv')
        history['date'] = pd.to_datetime(history['date'])
    except:
        history = pd.DataFrame(columns=['email', 'date', 'status'])

    # Send 15 new emails
    # ... (Same logic as before for sending new emails) ...
    
    # --- PART 3: FOLLOW-UP LOGIC (New Addition) ---
    print("Checking for follow-ups...")
    
    # Load replied users list
    try:
        replied_users = pd.read_csv('data/replied_users.csv', header=None)[0].tolist()
    except:
        replied_users = []

    today = datetime.now()
    four_days_ago = today - timedelta(days=4)

    # Filter: Sent 4+ days ago AND Status is 'sent' (not 'followup_sent')
    # Note: Logic assumes history has columns: email, date, status
    
    for index, row in history.iterrows():
        sent_date = row['date']
        email = row['email']
        status = row['status'] # 'sent' or 'followup_sent'
        
        # Check condition: 4 din ho gaye + Reply nahi aaya + Follow-up nahi bheja
        if sent_date.date() == four_days_ago.date() and \
           email not in replied_users and \
           status != 'followup_sent':
            
            # Send Follow-up Email
            subject = "Quick question regarding real estate leads"
            body = f"""Hi,
            
I'm writing to follow up on my previous email. I wanted to ensure you didn't miss the opportunity to test 2 free verified leads from Estavox.

Are you open to seeing the quality?

Best,
Lalan Singh
Estavox
"""
            try:
                send_email(email, subject, body)
                # Update status in history (In real DB use SQL, here we just alert)
                send_msg_alert(f"🔄 Follow-up sent to {email}")
                # Mark as done in CSV (Simplistic approach)
                history.at[index, 'status'] = 'followup_sent'
            except Exception as e:
                print(f"Failed follow-up: {e}")

    # Save updated history
    history.to_csv('data/history.csv', index=False)

if __name__ == "__main__":
    daily_workflow()
