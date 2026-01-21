import sys
import os # Ye zaroori hai
from core.ai_agent import generate_cold_email
from core.email_manager import send_email

def manual_run(target_email):
    print(f"Starting manual workflow for {target_email}...")
    
    # AI se email likhwana
    body = generate_cold_email("Valued Partner")
    
    # Email bhejna
    send_email(target_email, "Exclusive Leads for You", body)
    print("Done!")

if __name__ == "__main__":
    # Logic: Agar GitHub se command aayi hai to wo use karein, nahi to input maangein
    if len(sys.argv) > 1:
        # GitHub Actions pass karega: python manual_trigger.py "email@gmail.com"
        email = sys.argv[1]
    else:
        # Agar aap apne PC par chala rahe hain
        email = input("Enter email to send: ")
        
    manual_run(email)
