import requests
import json
from .config import GABBE_API_URL, GABBE_API_KEY, GABBE_API_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT, Colors

def call_llm(prompt, system_prompt="You are a helpful assistant.", temperature=None, timeout=None):
    """
    Call an LLM via an OpenAI-compatible API.

    Raises EnvironmentError if GABBE_API_KEY is not set so callers can
    distinguish missing configuration from actual API failures.
    Returns the response string on success, or None on network/API error.
    """
    if not GABBE_API_KEY:
        raise EnvironmentError(
            "GABBE_API_KEY is not set. "
            "Set the environment variable before using LLM features."
        )

    if temperature is None:
        temperature = LLM_TEMPERATURE
    if timeout is None:
        timeout = LLM_TIMEOUT

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
        "temperature": temperature,
    }

    try:
        response = requests.post(GABBE_API_URL, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        else:
            # Avoid leaking raw API response which may contain sensitive tokens
            print(f"{Colors.FAIL}❌ Unexpected API response format (missing 'choices').{Colors.ENDC}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}❌ API Request Failed: {e}{Colors.ENDC}")
        return None
