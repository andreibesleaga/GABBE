import time
import requests
import json
import logging
from .config import GABBE_API_URL, GABBE_API_KEY, GABBE_API_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT, Colors

logger = logging.getLogger("gabbe.llm")

_LLM_MAX_RETRIES = 3
_LLM_RETRY_DELAY = 1  # seconds

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

    for attempt in range(1, _LLM_MAX_RETRIES + 1):
        try:
            logger.debug("LLM Request (Attempt %d/%d) to %s", attempt, _LLM_MAX_RETRIES, GABBE_API_URL)
            response = requests.post(GABBE_API_URL, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and data["choices"]:
                content = data["choices"][0]["message"]["content"].strip()
                logger.debug("LLM Response received (%d chars)", len(content))
                return content
            else:
                # Avoid leaking raw API response which may contain sensitive tokens
                msg = "Unexpected API response format (missing 'choices')"
                print(f"{Colors.FAIL}❌ {msg}.{Colors.ENDC}")
                logger.error(msg)
                return None

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("LLM transient error (attempt %d): %s", attempt, e)
            if attempt < _LLM_MAX_RETRIES:
                time.sleep(_LLM_RETRY_DELAY)
            else:
                print(f"{Colors.FAIL}❌ API Request Failed after {attempt} attempts: {e}{Colors.ENDC}")
                logger.error("LLM failed after max retries: %s", e)
                return None
        
        except requests.exceptions.RequestException as e:
            # 4xx/5xx errors or other non-retriable issues
            print(f"{Colors.FAIL}❌ API Request Failed: {e}{Colors.ENDC}")
            logger.error("LLM non-retriable error: %s", e)
            return None
