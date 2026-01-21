import requests
import os

def send_msg_alert(message):
    token = os.getenv("TELEGRAM_BOT_MSG_TOKEN")
    chat_id = os.getenv("CHAT_ID_MSG")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

def send_payment_alert(client_info):
    token = os.getenv("TELEGRAM_BOT_PAY_TOKEN")
    chat_id = os.getenv("CHAT_ID_PAY")
    msg = f"💰 PAYMENT RECEIVED!\nClient: {client_info}\nStatus: Subscription Active (30 Days)"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": msg})
