#!/usr/bin/env python3
"""Debug OpenAI API issues"""

import os
import sys
import requests

# Load env manually
def load_env():
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

load_env()
api_key = os.getenv('OPENAI_API_KEY')

print("Testing OpenAI API Key...")
print(f"Key: {api_key[:20]}...{api_key[-10:]}")

# Test 1: List models (lightweight test)
print("\n=== Test 1: List Models ===")
try:
    response = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200:
        print("✓ API key is valid!")
    elif response.status_code == 401:
        print("✗ Invalid API key")
    elif response.status_code == 429:
        print("✗ Rate limit or quota exceeded")
        print(f"Full response: {response.text}")
    else:
        print(f"✗ Unexpected error: {response.status_code}")

except Exception as e:
    print(f"✗ Request failed: {str(e)}")

# Test 2: Check account/quota
print("\n=== Test 2: Simple Completion Test ===")
try:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        },
        timeout=10
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("✓ API is working!")
    elif response.status_code == 429:
        print("✗ Rate limit exceeded")
        print(f"Response: {response.text}")

        # Check if it's quota or rate limit
        resp_json = response.json()
        error_msg = resp_json.get('error', {}).get('message', '')
        print(f"Error message: {error_msg}")

        if 'quota' in error_msg.lower():
            print("\n⚠️  LIKELY CAUSE: Insufficient quota/credits")
            print("   Solution: Add credits to OpenAI account")
        elif 'rate' in error_msg.lower():
            print("\n⚠️  LIKELY CAUSE: Too many requests")
            print("   Solution: Wait a few minutes and retry")
    else:
        print(f"Response: {response.text}")

except Exception as e:
    print(f"✗ Request failed: {str(e)}")
