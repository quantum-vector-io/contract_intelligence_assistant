from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

print(f"API Key found: {bool(api_key)}")
if api_key:
    print(f"Key format: {api_key[:20]}...")

try:
    from openai import OpenAI
    print("✅ Import OK")
    
    client = OpenAI()
    print("✅ Client OK") 
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5
    )
    print(f"✅ API works: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
