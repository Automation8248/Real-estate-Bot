import smtplib
import pandas as pd
from email.mime.text import MIMEText
from core.ai_agent import analyze_reply
from core.telegram_bot import send_msg_alert

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
PAYPAL_ID = os.getenv("PAYPAL_EMAIL")

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    
    send_msg_alert(f"📤 Email Sent to: {to_email}")

def process_incoming_reply(client_email, reply_text):
    # AI se pucho kya karna hai
    intent = analyze_reply(reply_text)
    send_msg_alert(f"📩 Reply from {client_email}: {intent}")

    if intent == 'INTERESTED':
        # Send 2 Free Leads
        leads = pd.read_csv('data/scraped_leads.csv').head(2) # Top 2 leads
        leads_text = leads.to_string(index=False)
        
        body = f"""Here are 2 verified leads as promised:\n\n{leads_text}\n\n
        We have a premium subscription with weekly leads. Would you like to know the plans?"""
        send_email(client_email, "Your 2 Free Leads", body)

    elif intent == 'BUY':
        # Send Subscription & PayPal Details
        body = f"""Great! Our plan includes weekly verified leads from Tier 1 countries.
        
        To start your 30-day subscription, please pay via PayPal here:
        {PAYPAL_ID}
        
        Once payment is verified, you will receive the full list immediately."""
        send_email(client_email, "Subscription Details", body)
