import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
# from core.ai_agent import analyze_reply (Ye line shayad aapke code mein ho/na ho, dhyan rakhein)
from core.telegram_bot import send_msg_alert

# ... (Credentials wagarah same rahenge) ...
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
PAYPAL_ID = os.getenv("PAYPAL_EMAIL")

def send_email(to_email, subject, body):
    # ... (Ye function same rahega) ...
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"Lalan Singh <{EMAIL_USER}>"
    msg['To'] = to_email
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    
    send_msg_alert(f"📤 Email Sent to: {to_email}")

def process_incoming_reply(client_email, reply_text):
    # Step 1: Record that this user replied
    with open('data/replied_users.csv', 'a') as f:
        f.write(f"{client_email}\n")

    # Step 2: Leads nikalna
    try:
        leads = pd.read_csv('data/scraped_leads.csv').head(2)
        leads_text = leads.to_string(index=False)
    except:
        leads_text = "Check attachment for sample leads."

    # Step 3: Updated Body Text (Hindi requirement ke hisaab se English instruction)
    body = f"""Hello,

Thanks for your interest. As promised, here are 2 real verified leads for you to test immediately:

--------------------------------------------------
{leads_text}
--------------------------------------------------

To receive leads like this EVERY WEEK, please choose a plan:

WEEKLY SUBSCRIPTION PLANS:
1. Starter: $199 / week (5 Leads)
2. Growth:  $399 / week (10 Leads)
3. Pro:     $599 / week (20 Leads)
4. Elite:   $999 / week (40 Leads)

To start, pay via PayPal here: {PAYPAL_ID}

⚠️ IMPORTANT INSTRUCTION: 
In the PayPal 'Add a Note' section, please write the BUSINESS EMAIL for which you are purchasing this subscription. 
(This helps us send leads to the correct email address).

Best regards,
Lalan Singh
Founder, Estavox
"""
    
    # Send the email
    send_email(client_email, "Your 2 Free Leads + Weekly Plans", body)
    send_msg_alert(f"✅ Sent 2 Leads & Plans to {client_email}")
