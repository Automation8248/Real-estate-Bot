import sys
from core.ai_agent import generate_cold_email
from core.email_manager import send_email

def manual_run(target_email):
    print(f"Starting manual workflow for {target_email}...")
    
    body = generate_cold_email("Valued Partner")
    send_email(target_email, "Exclusive Leads for You", body)
    print("Done!")

if __name__ == "__main__":
    # Command line se email input lena
    email = input("Enter email to send: ")
    manual_run(email)
