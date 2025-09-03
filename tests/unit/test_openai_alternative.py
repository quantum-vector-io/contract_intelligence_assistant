# Alternative: Create test with explicit client setup
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

try:
    from openai import OpenAI
    
    # Explicit client creation without relying on auto-detection
    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=2
    )
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello world'}],
        max_tokens=10
    )
    
    print(f'✅ SUCCESS: {response.choices[0].message.content}')
    
except Exception as e:
    print(f'Error: {e}')
    
    # Fallback - try with requests directly (debugging)
    import requests
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-4o-mini',
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'max_tokens': 5
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        result = response.json()
        if 'choices' in result:
            print(f'✅ Direct API works: {result["choices"][0]["message"]["content"]}')
        else:
            print(f'API Error: {result}')
    except Exception as e2:
        print(f'Direct API also failed: {e2}')
