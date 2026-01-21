import imaplib
import email
import re
import pandas as pd
import os
from datetime import datetime
from core.telegram_bot import send_payment_alert, send_msg_alert
from core.email_manager import process_incoming_reply  # Reply handle karne ke liye

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
    print("Checking Inbox for Payments AND Replies...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
    except Exception as e:
        print(f"IMAP Login Failed: {e}")
        return

    # ---------------------------------------------------------
    # PART 1: CHECK FOR PAYPAL PAYMENTS
    # ---------------------------------------------------------
    try:
        status, messages = mail.search(None, '(FROM "service@paypal.com" UNSEEN SUBJECT "Payment received")')
        
        if status == "OK" and messages[0]:
            for num in messages[0].split():
                try:
                    _, data = mail.fetch(num, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1])
                    subject = msg["Subject"]
                    body = get_email_body(msg)

                    # --- Parsing Logic ---
                    # 1. Payer Email
                    payer_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\s+sent you', body)
                    payer_email = payer_match.group(1) if payer_match else "Unknown"

                    # 2. Amount
                    amount_match = re.search(r'\$(\d+\.\d{2})', subject + body)
                    
                    # 3. Note / Business Email Check
                    all_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', body)
                    business_email = None
                    for em in all_emails:
                        if em != payer_email and em != EMAIL_USER and "paypal.com" not in em:
                            business_email = em
                            break
                    
                    if amount_match and payer_email != "Unknown":
                        amount = amount_match.group(1)
                        if amount in PLANS:
                            plan_info = PLANS[amount]
                            
                            # A. Subscriber Add (Leads go to Payer)
                            add_subscriber(payer_email, plan_info['name'], plan_info['leads'])
                            
                            # B. Stop Marketing (Remove from target list)
                            target_to_remove = business_email if business_email else payer_email
                            stop_marketing_for(target_to_remove)
                            
                            # Alert
                            alert_msg = f"💰 Recvd ${amount} from {payer_email}"
                            if business_email: alert_msg += f"\n(Linked: {business_email})"
                            send_payment_alert(alert_msg)
                            
                            # Mark as Read
                            mail.store(num, '+FLAGS', '\\Seen')
                except Exception as e:
                    print(f"Payment parse error: {e}")
    except Exception as e:
        print(f"Error searching payments: {e}")

    # ---------------------------------------------------------
    # PART 2: CHECK FOR CLIENT REPLIES
    # ---------------------------------------------------------
    try:
        # Search ALL unread emails
        status, messages = mail.search(None, '(UNSEEN)')
        
        if status == "OK" and messages[0]:
            for num in messages[0].split():
                try:
                    _, data = mail.fetch(num, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1])
                    
                    email_from = msg.get("From")
                    subject = msg.get("Subject")
                    
                    # Filter: Ignore PayPal, Myself, and Google Alerts
                    if "paypal.com" in email_from or EMAIL_USER in email_from or "google.com" in email_from:
                        continue

                    # Extract Sender Email Address
                    sender_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', email_from)
                    if not sender_match:
                        continue
                    sender_email = sender_match.group(0)

                    print(f"📩 Reply Detected from: {sender_email}")
                    
                    # Get Body
                    body = get_email_body(msg)

                    # --- ACTION: Send 2 Leads + Plans ---
                    process_incoming_reply(sender_email, body)
                    
                    # Mark as Read (Taaki baar baar reply na kare)
                    mail.store(num, '+FLAGS', '\\Seen')
                    
                except Exception as e:
                    print(f"Reply parse error: {e}")
    except Exception as e:
        print(f"Error searching replies: {e}")

    mail.logout()

# --- HELPER FUNCTIONS ---

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors='ignore')
    else:
        return msg.get_payload(decode=True).decode(errors='ignore')
    return ""

def add_subscriber(email, plan_name, lead_count):
    file_path = 'data/subscribers.csv'
    
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=['email', 'plan', 'leads_per_week', 'start_date', 'last_sent_date', 'status'])
        df.to_csv(file_path, index=False)
    
    df = pd.read_csv(file_path)
    
    # Update or Add
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
    print(f"✅ Subscriber Added: {email}")

def stop_marketing_for(target_email):
    try:
        df = pd.read_csv('data/history.csv')
        if target_email in df['email'].values:
            df.loc[df['email'] == target_email, 'status'] = 'converted'
            df.to_csv('data/history.csv', index=False)
            print(f"🛑 Marketing stopped for: {target_email}")
    except:
        pass
