import requests
import json
import sys
from .config import GABBE_API_URL, GABBE_API_KEY, GABBE_API_MODEL, Colors

def call_llm(prompt, system_prompt="You are a helpful assistant."):
    """
    Generic function to call an LLM via API.
    Uses OpenAI-compatible format by default.
    """
    if not GABBE_API_KEY:
        print(f"{Colors.WARNING}⚠️  GABBE_API_KEY not set. Using mock response.{Colors.ENDC}")
        return "Log: API Key missing. Returning mock response."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GABBE_API_KEY}"
    }

    payload = {
        "model": GABBE_API_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GABBE_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Handle different response formats if needed, default to OpenAI
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: Unexpected API response format: {data}"

    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}❌ API Request Failed: {e}{Colors.ENDC}")
        return None
