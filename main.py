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

# --- CONFIGURATION ---
DAILY_SCRAPE_TARGET = 500  # Roz 500 naye leads jodege
DAILY_EMAIL_TARGET = 15    # Roz sirf 15 ko email (Safety ke liye)

def load_history():
    """History load karo taaki duplicates check kar sakein"""
    if os.path.exists('data/history.csv'):
        return pd.read_csv('data/history.csv')
    else:
        return pd.DataFrame(columns=['email', 'date', 'status'])

def run_daily_marketing():
    print("--- 🚀 MODE: DAILY MARKETING OPERATION ---")
    
    # --- STEP 1: COLLECT LEADS (Real Data) ---
    print("1️⃣ Collecting Data from Google Maps Source...")
    scrape_leads_tier1(count=DAILY_SCRAPE_TARGET)

    # --- STEP 2: LOAD & FILTER (Anti-Spam) ---
    print("2️⃣ Filtering Data (Removing Duplicates & No-Reply)...")
    
    try:
        all_leads = pd.read_csv('data/scraped_leads.csv')
        history = load_history()
        
        # Fast Filtering Set
        sent_emails_set = set(history['email'].astype(str).str.lower().tolist())
        
        # Load Replied Users (Inko pareshan nahi karna)
        try:
            replied_users = set(pd.read_csv('data/replied_users.csv', header=None)[0].astype(str).str.lower().tolist())
        except:
            replied_users = set()

    except Exception as e:
        print(f"❌ Data Load Error: {e}")
        return

    targets_to_send = []
    # Block List (Fake Emails)
    block_keywords = ['no-reply', 'noreply', 'donotreply', 'newsletter', 'admin', 'support', 'help', 'info']

    # Reverse loop (Latest leads pehle uthao)
    for index, row in all_leads.iloc[::-1].iterrows():
        email = str(row['email']).lower().strip()
        name = row['name']
        
        # FILTER 1: History Check (Sent before?)
        if email in sent_emails_set:
            continue
            
        # FILTER 2: Reply Check (Replied before?)
        if email in replied_users:
            continue
            
        # FILTER 3: Junk Email Check
        if any(keyword in email for keyword in block_keywords):
            continue
            
        # Valid Target Found
        targets_to_send.append({'email': email, 'name': name})
        
        if len(targets_to_send) >= DAILY_EMAIL_TARGET:
            break
    
    print(f"✅ Found {len(targets_to_send)} fresh, unique targets for today.")

    # --- STEP 3: SEND EMAILS ---
    if targets_to_send:
        for target in targets_to_send:
            email = target['email']
            name = target['name']
            
            # AI writes safe greeting email (No Names)
            body = generate_cold_email(name)
            
            try:
                send_email(email, "Partnership Opportunity", body)
                
                # Update History Immediately
                new_record = {
                    'email': email, 
                    'date': datetime.now().strftime('%Y-%m-%d'), 
                    'status': 'sent'
                }
                history = pd.concat([history, pd.DataFrame([new_record])], ignore_index=True)
                sent_emails_set.add(email) # Add to current set to avoid repeat in same run
                
            except Exception as e:
                print(f"❌ Failed to send to {email}: {e}")

        # Save History File
        history.to_csv('data/history.csv', index=False)
        send_msg_alert(f"✅ Daily Task Done: {len(targets_to_send)} Emails Sent.")
    else:
        print("⚠️ No new targets found. Check Scraper.")

    # --- STEP 4: FOLLOW-UP LOGIC (4 Days) ---
    print("3️⃣ Checking for Follow-ups (4-Day Rule)...")
    check_followups(history, replied_users)

def check_followups(history, replied_users_set):
    today = datetime.now()
    updated = False
    
    for index, row in history.iterrows():
        try:
            sent_date = datetime.strptime(row['date'], '%Y-%m-%d')
            days_diff = (today - sent_date).days
            email = str(row['email']).lower()
            
            # Condition: 4 din ho gaye + Reply nahi aaya + Status 'sent' hai
            if days_diff >= 4 and email not in replied_users_set and row['status'] == 'sent':
                
                print(f"🔄 Sending Follow-up to {email}...")
                follow_body = """Hello,

I'm writing to follow up on my previous email. I wanted to ensure you didn't miss the opportunity to test 2 free verified leads.

Are you open to seeing the quality?

Best,
Lalan Singh
Founder, Estavox
"""
                try:
                    send_email(email, "Quick Follow-up", follow_body)
                    history.at[index, 'status'] = 'followup_sent'
                    updated = True
                except Exception as e:
                    print(f"Follow-up failed: {e}")
        except:
            continue
    
    if updated:
        history.to_csv('data/history.csv', index=False)
        print("✅ Follow-ups updated.")

def run_payment_checks():
    print("--- 💰 MODE: PAYMENT & SUBSCRIPTION CHECK ---")
    try:
        # Check PayPal & Replies
        check_new_payments() 
    except Exception as e:
        print(f"Payment Listener Error: {e}")
    
    try:
        # Send Weekly Leads
        fulfill_subscriptions()
    except Exception as e:
        print(f"Subscription Error: {e}")

if __name__ == "__main__":
    # Command Line Logic
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "--payments":
            run_payment_checks()
            
        elif mode == "--daily":
            run_daily_marketing()
            
        else:
            # Agar koi galat command de
            print("Unknown mode. Running Full Check.")
            run_payment_checks()
            run_daily_marketing()
    else:
        # Default: Agar bina command ke run karein
        run_payment_checks()
        run_daily_marketing()
