from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

def generate_cold_email(business_name):
    """
    Standard cold email generator for daily marketing.
    """
    prompt = f"""
    Write a short, professional B2B cold email to {business_name}.
    
    My Offer: High-quality, verified real estate leads (use 'premium markets', not 'Tier 1').
    My Goal: Ask if they want 2 free sample leads to test quality.
    
    Tone: Professional, direct, no fake promises.
    
    Sign off exactly as:
    Lalan Singh
    Founder, Estavox
    """
    
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat_completion(model="Qwen/Qwen2.5-72B-Instruct", messages=messages, max_tokens=200)
        return response.choices[0].message.content
    except Exception as e:
        return f"Hello {business_name}, checking if you need leads? - Lalan Singh"

def analyze_and_plan(email_body):
    """
    AI decides if the user asked a Question, wants a Custom Location, or is just Interested.
    """
    prompt = f"""
    Analyze this email reply from a real estate client:
    "{email_body}"
    
    Determine the INTENT and output strictly in JSON format:
    
    1. IF they ask for leads in a SPECIFIC location or niche (e.g., "Do you have leads in London?", "Commercial only"):
       {{"action": "CUSTOM", "query": "Real Estate Agents in [Location/Niche]"}}
       
    2. IF they ask a general question (e.g., "How does it work?", "Who are you?"):
       {{"action": "QUESTION", "reply_text": "[Write a short professional answer as Lalan Singh, Founder Estavox]"}}
       
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
        # Cleaning AI output
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {"action": "STANDARD"}
