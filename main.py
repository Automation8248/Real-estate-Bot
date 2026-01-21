import pandas as pd
import sys
import os
from core.scraper import scrape_leads_tier1
from core.email_manager import send_email
from core.ai_agent import generate_cold_email
from core.telegram_bot import send_msg_alert
from core.payment_listener import check_new_payments
from core.subscription_manager import fulfill_subscriptions

# --- CONFIG ---
DAILY_SCRAPE_TARGET = 500
DAILY_EMAIL_TARGET = 15

def run_daily_marketing():
    """Sirf Marketing aur Scraping ka kaam"""
    print("--- MODE: DAILY MARKETING & SCRAPING ---")
    
    # 1. Scrape New Leads
    print("1. Scraping Leads...")
    try:
        new_leads = scrape_leads_tier1(count=DAILY_SCRAPE_TARGET)
        header = not os.path.exists('data/scraped_leads.csv')
        new_leads.to_csv('data/scraped_leads.csv', mode='a', header=header, index=False)
        send_msg_alert(f"✅ Daily Task: Scraped {len(new_leads)} leads.")
    except Exception as e:
        print(f"Scraping Error: {e}")

    # 2. Cold Outreach (Marketing)
    print("2. Sending Marketing Emails...")
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
            email_body = generate_cold_email(name)
            
            try:
                send_email(email, "Collaboration Opportunity - Estavox", email_body)
                new_record = {'email': email, 'date': pd.Timestamp.now(), 'status': 'sent'}
                history = pd.concat([history, pd.DataFrame([new_record])], ignore_index=True)
            except Exception as e:
                print(f"Failed to send to {email}: {e}")
        
        history.to_csv('data/history.csv', index=False)
        send_msg_alert(f"✅ Marketing Done: Sent {len(fresh_targets)} emails.")
        
    except Exception as e:
        print(f"Marketing Error: {e}")

def run_payment_checks():
    """Sirf Payment Check aur Subscription Delivery"""
    print("--- MODE: PAYMENT CHECK & SUBSCRIPTION ---")

    # 1. Check New Payments (PayPal)
    # Logic: Koi naya banda aaya kya?
    try:
        check_new_payments()
    except Exception as e:
        print(f"Payment Listener Error: {e}")

    # 2. Fulfill Subscriptions (Automatic Weekly Check)
    # Logic: Subscribers.csv mein jo bhi hai, agar uska week pura ho gaya to bhejo.
    try:
        fulfill_subscriptions()
    except Exception as e:
        print(f"Subscription Manager Error: {e}")

if __name__ == "__main__":
    # Command Line Argument Check
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "--payments":
            run_payment_checks()
        elif mode == "--daily":
            run_daily_marketing()
        else:
            print("Invalid mode. Use --payments or --daily")
    else:
        # Default (Agar manual run karein bina flag ke to sab kuch karo)
        run_payment_checks()
        run_daily_marketing()
