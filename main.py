import pandas as pd
import sys
import os
from core.scraper import scrape_leads_tier1
from core.email_manager import send_email
from core.ai_agent import generate_cold_email
from core.telegram_bot import send_msg_alert
# New Modules Import
from core.payment_listener import check_new_payments
from core.subscription_manager import fulfill_subscriptions

# --- CONFIG ---
DAILY_SCRAPE_TARGET = 500
DAILY_EMAIL_TARGET = 15

def daily_workflow():
    print("--- STARTING AUTOMATION ---")
    
    # STEP 1: Scrape New Leads
    # (Yeh daily stock banayega jo subscribers aur free samples mein use hoga)
    print("1. Scraping Leads...")
    try:
        new_leads = scrape_leads_tier1(count=DAILY_SCRAPE_TARGET)
        # Append to master file
        header = not os.path.exists('data/scraped_leads.csv')
        new_leads.to_csv('data/scraped_leads.csv', mode='a', header=header, index=False)
        send_msg_alert(f"✅ Scraped {len(new_leads)} new leads.")
    except Exception as e:
        print(f"Scraping Error: {e}")

    # STEP 2: Check Payments (Priority)
    # (Agar kisi ne abhi pay kiya hai, usse list mein add karo)
    print("2. Checking Payments...")
    try:
        check_new_payments()
    except Exception as e:
        print(f"Payment Listener Error: {e}")

    # STEP 3: Fulfill Subscriptions
    # (Jo naye add huye ya jinka week pura hua, unhe leads bhejo)
    print("3. Fulfilling Subscriptions...")
    try:
        fulfill_subscriptions()
    except Exception as e:
        print(f"Subscription Manager Error: {e}")

    # STEP 4: Cold Outreach (Marketing)
    # (Naye logo ko pitch karo)
    print("4. Sending Marketing Emails...")
    try:
        targets = pd.read_csv('data/business_targets.csv')
        
        # Load History
        if os.path.exists('data/history.csv'):
            history = pd.read_csv('data/history.csv')
        else:
            history = pd.DataFrame(columns=['email', 'date', 'status'])
        
        # Filter fresh targets (Not in history)
        fresh_targets = targets[~targets['email'].isin(history['email'])].head(DAILY_EMAIL_TARGET)

        for index, row in fresh_targets.iterrows():
            email = row['email']
            name = row['name']
            
            # Generate AI Email
            email_body = generate_cold_email(name)
            
            # Send
            try:
                send_email(email, "Collaboration Opportunity - Estavox", email_body)
                
                # Update History
                new_record = {'email': email, 'date': pd.Timestamp.now(), 'status': 'sent'}
                history = pd.concat([history, pd.DataFrame([new_record])], ignore_index=True)
                
            except Exception as e:
                print(f"Failed to send to {email}: {e}")
        
        # Save History
        history.to_csv('data/history.csv', index=False)
        
    except Exception as e:
        print(f"Marketing Error: {e}")

    print("--- WORKFLOW COMPLETE ---")

if __name__ == "__main__":
    daily_workflow()
