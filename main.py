import pandas as pd
import sys
import os
from datetime import datetime, timedelta
from core.scraper import scrape_leads_tier1
from core.email_manager import send_email
from core.ai_agent import generate_cold_email
from core.telegram_bot import send_msg_alert
from core.payment_listener import check_new_payments
from core.subscription_manager import fulfill_subscriptions

# CONFIG
DAILY_SCRAPE_TARGET = 500
DAILY_EMAIL_TARGET = 15

def run_daily_marketing():
    print("--- MODE: DAILY MARKETING & FOLLOW-UPS ---")
    
    # 1. Scrape
    try:
        new_leads = scrape_leads_tier1(count=DAILY_SCRAPE_TARGET)
        header = not os.path.exists('data/scraped_leads.csv')
        new_leads.to_csv('data/scraped_leads.csv', mode='a', header=header, index=False)
        send_msg_alert(f"✅ Daily Scrape: {len(new_leads)} leads.")
    except Exception as e:
        print(f"Scrape Error: {e}")

    # 2. Marketing Emails
    try:
        targets = pd.read_csv('data/business_targets.csv')
        if os.path.exists('data/history.csv'):
            history = pd.read_csv('data/history.csv')
        else:
            history = pd.DataFrame(columns=['email', 'date', 'status'])
        
        fresh_targets = targets[~targets['email'].isin(history['email'])].head(DAILY_EMAIL_TARGET)

        for index, row in fresh_targets.iterrows():
            email = row['email']
            name = row['name']
            body = generate_cold_email(name)
            
            try:
                send_email(email, "Collaboration Opportunity - Estavox", body)
                new_record = {'email': email, 'date': datetime.now().strftime('%Y-%m-%d'), 'status': 'sent'}
                history = pd.concat([history, pd.DataFrame([new_record])], ignore_index=True)
            except Exception as e:
                print(f"Send Failed: {e}")
        
        history.to_csv('data/history.csv', index=False)
        
    except Exception as e:
        print(f"Marketing Error: {e}")

    # 3. FOLLOW-UP LOGIC (4 DAYS) -- [RE-IMPLEMENTED]
    print("3. Checking Follow-ups...")
    try:
        history = pd.read_csv('data/history.csv')
        try:
            replied = pd.read_csv('data/replied_users.csv', header=None)[0].tolist()
        except:
            replied = []
            
        today = datetime.now()
        
        for index, row in history.iterrows():
            try:
                sent_date = datetime.strptime(row['date'], '%Y-%m-%d')
                days_diff = (today - sent_date).days
                
                # Agar 4 din ho gaye + Reply nahi aaya + Status 'sent' hai
                if days_diff >= 4 and row['email'] not in replied and row['status'] == 'sent':
                    
                    follow_body = """Hi,
                    
Checking if you saw my previous email regarding verified real estate leads?
I'd love to send you 2 free samples to prove the quality.

Let me know if you are interested.

Best,
Lalan Singh
Estavox
"""
                    send_email(row['email'], "Quick Follow-up: Estavox Leads", follow_body)
                    history.at[index, 'status'] = 'followup_sent'
                    print(f"🔄 Follow-up sent to {row['email']}")
            except:
                continue
                
        history.to_csv('data/history.csv', index=False)
    except Exception as e:
        print(f"Follow-up Error: {e}")

def run_payment_checks():
    print("--- MODE: PAYMENT CHECK & SUBSCRIPTION ---")
    try:
        check_new_payments() # Includes Reply Checks
    except Exception as e:
        print(f"Payment Error: {e}")
    
    try:
        fulfill_subscriptions()
    except Exception as e:
        print(f"Subs Error: {e}")

if __name__ == "__main__":
    # Logic for Manual vs Daily vs Payments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "--payments":
            run_payment_checks()
        elif mode == "--daily":
            run_daily_marketing()
        else:
            print("Unknown mode")
    else:
        # Default Run (Runs everything if no flag)
        run_payment_checks()
        run_daily_marketing()
