import sys
import os
from core.email_manager import send_email
from core.ai_agent import generate_cold_email

def manual_run(target_email):
    print(f"🚀 Starting Manual Workflow for {target_email}...")
    
    # Hum 'Valued Partner' bhejenge, lekin AI usse ignore karke "Hello," hi use karega
    # kyunki humne AI prompt mein strict rule laga diya hai.
    dummy_name = "Valued Partner"

    print("Generating Respectful Email (No Names)...")
    email_body = generate_cold_email(dummy_name)
    
    print("Sending Email...")
    try:
        send_email(target_email, "Exclusive Partnership Opportunity - Estavox", email_body)
        print("✅ Done! Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email_arg = sys.argv[1]
        manual_run(email_arg)
    else:
        # Agar koi bina email ke run kare (Testing ke liye)
        email_input = input("Enter target email: ")
        if email_input:
            manual_run(email_input)
        else:
            print("❌ Error: No email provided.")
