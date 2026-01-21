from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=os.getenv("HF_TOKEN"))

def generate_cold_email(business_name):
    prompt = f"""
    Write a short, professional cold email to {business_name}, a real estate business.
    Offer them high-quality real estate leads from Tier 1 countries.
    Ask a simple question: 'Would you be interested in seeing 2 free sample leads?'
    Keep it under 100 words.
    """
    response = client.text_generation(prompt, max_new_tokens=200)
    return response

def analyze_reply(email_body):
    """
    Decides the intent of the user.
    Returns: 'INTERESTED', 'BUY', 'NOT_INTERESTED', or 'OTHER'
    """
    prompt = f"""
    Analyze this email reply from a client: "{email_body}"
    
    1. If they want to see samples or say yes, output: INTERESTED
    2. If they ask for price, subscription, or how to pay, output: BUY
    3. If they say no or stop, output: NOT_INTERESTED
    4. Otherwise: OTHER
    
    Only output the single word.
    """
    response = client.text_generation(prompt, max_new_tokens=10)
    return response.strip()
