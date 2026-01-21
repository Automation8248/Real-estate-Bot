from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

def generate_cold_email(business_name):
    """
    Generates cold email using a RESPECTFUL GENERIC GREETING.
    Strictly forbids using 'Dear [Name]'.
    """
    # Prompt updated: Full constraints + Estavox Branding + No Names
    prompt = f"""
    Write a short, professional B2B cold email.
    
    1. Greeting: Start EXACTLY with "Hello," or "Hi there," (Do NOT use names like 'Dear {business_name}').
    2. Context: We are Estavox, specializing in verified real estate leads from premium markets.
    3. Offer: Ask if they want to see 2 free sample leads to test quality.
    4. Tone: Professional, direct, and respectful.
    5. Sign off: Lalan Singh, Founder, Estavox.
    
    Do NOT include any placeholders like [Name], [Company], or [Date].
    """
    
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat_completion(model="Qwen/Qwen2.5-72B-Instruct", messages=messages, max_tokens=300)
        content = response.choices[0].message.content
        
        # FINAL SAFETY FILTER:
        # Agar AI ne galti se [Name] likha, use hata kar 'Hello,' kar do
        content = content.replace("[Recipient's Name]", "there")
        content = content.replace("[Name]", "there")
        content = content.replace("Dear [Business Name]", "Hello")
        
        return content
    except Exception as e:
        # Fallback agar AI fail ho jaye
        return "Hello,\n\nI have verified real estate leads from premium markets. Would you like to see 2 free samples?\n\nBest,\nLalan Singh\nFounder, Estavox"

def analyze_and_plan(email_body):
    """
    Full Logic: Decides if user asked a Question, wants Custom Location, or Standard Leads.
    """
    prompt = f"""
    Analyze this email reply from a client:
    "{email_body}"
    
    Determine the INTENT and output strictly in JSON format:
    
    1. IF they ask for leads in a SPECIFIC location/niche (e.g., "Dubai only", "Commercial"):
       {{"action": "CUSTOM", "query": "Real Estate Agents in [Location/Niche]"}}
       
    2. IF they ask a general QUESTION (e.g., "How does it work?", "Are you legit?"):
       {{"action": "QUESTION", "reply_text": "[Write a short answer as Lalan Singh, Founder Estavox]"}}
       
    3. IF they say "Yes", "Interested", "Send samples", or "Price":
       {{"action": "STANDARD", "query": "None"}}
       
    OUTPUT ONLY THE JSON.
    """
    
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat_completion(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=messages,
            max_tokens=300
        )
        content = response.choices[0].message.content
        # Clean JSON
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {"action": "STANDARD"}
