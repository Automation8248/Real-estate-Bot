import imaplib
import email
import re
import pandas as pd
import os
from datetime import datetime
from core.telegram_bot import send_payment_alert

# Configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = "imap.gmail.com"

# Subscription Plans
PLANS = {
    '199.00': {'name': 'Starter', 'leads': 5},
    '399.00': {'name': 'Growth', 'leads': 10},
    '599.00': {'name': 'Pro', 'leads': 20},
    '999.00': {'name': 'Elite', 'leads': 40}
}

def check_new_payments():
    print("Checking for PayPal payments...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
    except Exception as e:
        print(f"IMAP Login Failed: {e}")
        return

    # Search specifically for PayPal "Payment received" emails that are Unread
    status, messages = mail.search(None, '(FROM "service@paypal.com" UNSEEN SUBJECT "Payment received")')
    
    if status != "OK" or not messages[0]:
        print("No new payments found.")
        return

    for num in messages[0].split():
        try:
            status, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            subject = msg["Subject"]
            
            # Extract Body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            # --- SMART PARSING LOGIC ---
            
            # 1. Payer Email (Sender)
            payer_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\s+sent you', body)
            payer_email = payer_match.group(1) if payer_match else "Unknown"

            # 2. Amount Extraction ($199.00)
            amount_match = re.search(r'\$(\d+\.\d{2})', subject + body)
            
            # 3. Check "Note" for Business Email
            # Body mein jitne bhi emails hain unhe nikalo
            all_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', body)
            
            business_email = None
            for em in all_emails:
                # Agar email Payer ka nahi hai, aur Mera nahi hai, aur PayPal ka nahi hai -> To wo Business Email hai
                if em != payer_email and em != EMAIL_USER and "paypal.com" not in em:
                    business_email = em
                    break
            
            if amount_match and payer_email != "Unknown":
                amount = amount_match.group(1)
                
                if amount in PLANS:
                    plan_info = PLANS[amount]
                    
                    # A. Subscriber Add Karo (Leads hamesha Payer Email par jayengi jo Active hai)
                    add_subscriber(payer_email, plan_info['name'], plan_info['leads'])
                    
                    # B. Agar Business Email mila, to use Marketing List se hatao
                    if business_email:
                        stop_marketing_for(business_email)
                    else:
                        stop_marketing_for(payer_email)
                    
                    # C. Mark email as read
                    mail.store(num, '+FLAGS', '\\Seen')
                    
                    # Alert
                    msg_text = f"💰 Payment: ${amount} from {payer_email}"
                    if business_email:
                        msg_text += f"\n(Linked Business: {business_email})"
                    send_payment_alert(msg_text)
                    
        except Exception as e:
            print(f"Error processing email {num}: {e}")

    mail.logout()

def add_subscriber(email, plan_name, lead_count):
    file_path = 'data/subscribers.csv'
    
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=['email', 'plan', 'leads_per_week', 'start_date', 'last_sent_date', 'status'])
        df.to_csv(file_path, index=False)
    
    df = pd.read_csv(file_path)
    
    # Update existing or Add new
    if email in df['email'].values:
        df.loc[df['email'] == email, 'plan'] = plan_name
        df.loc[df['email'] == email, 'leads_per_week'] = lead_count
        df.loc[df['email'] == email, 'status'] = 'Active'
        df.loc[df['email'] == email, 'last_sent_date'] = 'New' # Trigger Immediate Send
    else:
        new_row = {
            'email': email, 
            'plan': plan_name,
            'leads_per_week': lead_count, 
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'last_sent_date': 'New', # Trigger Immediate Send
            'status': 'Active'
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(file_path, index=False)
    print(f"✅ Subscriber Added/Updated: {email}")

def stop_marketing_for(target_email):
    try:
        df = pd.read_csv('data/history.csv')
        if target_email in df['email'].values:
            df.loc[df['email'] == target_email, 'status'] = 'converted'
            df.to_csv('data/history.csv', index=False)
            print(f"🛑 Marketing stopped for converted client: {target_email}")
    except:
        pass
