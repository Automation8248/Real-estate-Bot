import pandas as pd
from datetime import datetime
from core.email_manager import send_email
from core.telegram_bot import send_msg_alert

def fulfill_subscriptions():
    print("Running Subscription Manager...")
    subs_file = 'data/subscribers.csv'
    leads_file = 'data/scraped_leads.csv'
    
    try:
        subs = pd.read_csv(subs_file)
        leads = pd.read_csv(leads_file)
    except Exception as e:
        print(f"Files missing for subscription: {e}")
        return

    today = datetime.now()

    for index, row in subs.iterrows():
        if row['status'] != 'Active':
            continue

        should_send = False
        
        # CONDITION 1: Brand New Subscriber (Send Immediately)
        if row['last_sent_date'] == 'New':
            should_send = True
            print(f"🚀 New Payment Detected! Sending leads to {row['email']}")
        
        # CONDITION 2: Weekly Cycle (7 Days Passed)
        else:
            try:
                last_date = datetime.strptime(row['last_sent_date'], '%Y-%m-%d')
                days_diff = (today - last_date).days
                if days_diff >= 7:
                    should_send = True
                    print(f"📅 Weekly cycle due for {row['email']}")
            except:
                continue

        if should_send:
            count = int(row['leads_per_week'])
            
            # Logic: Get random samples or top rows
            sample_leads = leads.sample(n=count) if len(leads) >= count else leads
            leads_text = sample_leads.to_string(index=False)
            
            subject = f"Weekly Real Estate Leads - {row['plan']} Plan"
            body = f"""Hello,

Here is your scheduled delivery of verified real estate leads from Estavox.

--------------------------------------------------
{leads_text}
--------------------------------------------------

Plan: {row['plan']} ({count} Leads/Week)
Next Delivery: In 7 Days

Thank you for your business.

Best,
Lalan Singh
Founder, Estavox
"""

            try:
                send_email(row['email'], subject, body)
                send_msg_alert(f"📦 Sent {count} leads to subscriber: {row['email']}")
                
                # Update Date to Today
                subs.at[index, 'last_sent_date'] = today.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"Failed to send to {row['email']}: {e}")

    subs.to_csv(subs_file, index=False)
