from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

# Client Setup
client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

def generate_cold_email(business_name):
    """
    Generates the cold email with Estavox branding.
    """
    prompt = f"""
    Write a short, professional B2B cold email to {business_name}.
    
    My Offer: High-quality, verified real estate leads (do not use the phrase 'Tier 1 countries', use 'premium markets' instead).
    My Goal: Ask if they want 2 free sample leads to test quality.
    
    Tone: Professional, direct, no fake promises.
    
    Sign off exactly as:
    Lalan Singh
    Founder, Estavox
    """
    
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat_completion(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=messages,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating email: {e}"

def analyze_reply(email_body):
    """
    Analyzes the reply to see if they are interested.
    (Yeh function missing tha, isliye error aaya)
    """
    prompt = f"""
    Analyze this email reply from a client: "{email_body}"
    
    1. If they want to see samples, say yes, or ask for price: output INTERESTED
    2. If they say no, stop, or unsubscribe: output NOT_INTERESTED
    
    Only output the single word.
    """
    
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat_completion(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=messages,
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except:
        return "INTERESTED" # Fallback: Assume interested if AI fails
