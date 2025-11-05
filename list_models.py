import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    print("🔑 API Key found!")
    print(f"Key: {api_key[:20]}...")
    print("\n" + "="*50)
    print("Available Models:")
    print("="*50)
    
    try:
        genai.configure(api_key=api_key)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 This might mean:")
        print("1. API not enabled in Google Cloud Console")
        print("2. Go to: https://console.cloud.google.com/")
        print("3. Enable 'Generative Language API'")
else:
    print("❌ No API key found in .env")
