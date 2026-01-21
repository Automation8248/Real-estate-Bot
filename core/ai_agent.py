from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

def generate_cold_email(business_name):
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
    
    response = client.chat_completion(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=messages,
        max_tokens=200
    )
    
    return response.choices[0].message.content

# analyze_reply function waisa hi rahega, kyunki ab hum har reply par same action le rahe hain.
