import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
from core.telegram_bot import send_msg_alert
from core.ai_agent import analyze_and_plan
from core.scraper import scrape_leads_tier1

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
PAYPAL_ID = os.getenv("PAYPAL_EMAIL")

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = f"Lalan Singh <{EMAIL_USER}>"
        msg['To'] = to_email
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        
        send_msg_alert(f"📤 Email Sent to: {to_email}")
    except Exception as e:
        print(f"Email Send Error: {e}")

def process_incoming_reply(client_email, reply_text):
    print(f"Processing reply from {client_email}...")
    
    # 1. Save that user replied (taaki follow-up na jaye)
    try:
        with open('data/replied_users.csv', 'a') as f:
            f.write(f"{client_email}\n")
    except:
        pass

    # 2. AI Plan
    plan = analyze_and_plan(reply_text)
    action = plan.get('action', 'STANDARD')
    
    # Common Subscription Text (Jo aapne manga tha)
    subscription_info = f"""
WEEKLY SUBSCRIPTION PLANS:
1. Starter: $199 / week (5 Leads)
2. Growth:  $399 / week (10 Leads)
3. Pro:     $599 / week (20 Leads)
4. Elite:   $999 / week (40 Leads)

To start, pay via PayPal here: {PAYPAL_ID}

⚠️ IMPORTANT: 
In the PayPal 'Add a Note' section, please write the BUSINESS EMAIL for which you are purchasing this subscription.
"""

    email_body = ""
    subject = ""

    # --- SCENARIO 1: QUESTION ---
    if action == 'QUESTION':
        ai_answer = plan.get('reply_text', "We provide verified leads.")
        subject = "Re: Your Question - Estavox"
        email_body = f"""Hello,

{ai_answer}

If you are ready to see the quality, reply 'Yes' and I'll send 2 free samples.

Best,
Lalan Singh
Estavox
"""

    # --- SCENARIO 2: CUSTOM REQUEST ---
    elif action == 'CUSTOM':
        query = plan.get('query', 'Real Estate Agents')
        leads = scrape_leads_tier1(count=2, query=query)
        leads_text = leads.to_string(index=False)
        
        subject = f"Here are your {query} Leads"
        email_body = f"""Hello,

Here are 2 fresh verified leads specifically for '{query}' as requested:

--------------------------------------------------
{leads_text}
--------------------------------------------------

We can automate this for you weekly.
{subscription_info}

Best,
Lalan Singh
Estavox
"""

    # --- SCENARIO 3: STANDARD (Interest/Price) ---
    else:
        try:
            leads = pd.read_csv('data/scraped_leads.csv').head(2)
            leads_text = leads.to_string(index=False)
        except:
            leads_text = "See attachment."

        subject = "Your 2 Free Leads + Weekly Plans"
        email_body = f"""Hello,

As promised, here are 2 real verified leads for you to test immediately:

--------------------------------------------------
{leads_text}
--------------------------------------------------

To receive leads like this EVERY WEEK, choose a plan below:
{subscription_info}

Best,
Lalan Singh
Estavox
"""

    # Send Final Email
    send_email(client_email, subject, email_body)
