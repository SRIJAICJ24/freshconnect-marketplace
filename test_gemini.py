import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

print("=" * 50)
print("Testing Gemini API")
print("=" * 50)

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file!")
    print("\nMake sure .env file exists with:")
    print("GEMINI_API_KEY=your_key_here")
else:
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test message
        print("\n🧪 Testing API call...")
        response = model.generate_content("Say hello in one word")
        
        if response and response.text:
            print(f"✅ SUCCESS! API is working!")
            print(f"Response: {response.text}")
        else:
            print("❌ No response from API")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nPossible reasons:")
        print("1. API key is invalid")
        print("2. API key is not activated")
        print("3. No internet connection")
        print("4. API quota exceeded")

print("=" * 50)
