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
                msg = "Unexpected API response format"
                print(f"{Colors.FAIL}❌ {msg}.{Colors.ENDC}")
                logger.error("%s: %s", msg, str(data)[:200]) # Log truncated data for debug
                return None

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status in (429, 500, 502, 503, 504) and attempt < _LLM_MAX_RETRIES:
                logger.warning("Retriable HTTP %d error: %s", status, e)
                # Exponential backoff
            elif status == 401 or status == 403:
                print(f"{Colors.FAIL}❌ Authentication Failed (Check GABBE_API_KEY).{Colors.ENDC}")
                return None
            else:
                print(f"{Colors.FAIL}❌ API Error (Status {status}).{Colors.ENDC}")
                logger.error("Non-retriable HTTP error: %s", e)
                return None

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("LLM transient error: %s", e)
            # Proceed to sleep logic

        except requests.exceptions.RequestException as e:
            # Catch-all for other requests errors
            print(f"{Colors.FAIL}❌ Request Failed.{Colors.ENDC}")
            logger.error("LLM RequestException: %s", e)
            return None
        
        # Backoff logic
        if attempt < _LLM_MAX_RETRIES:
            sleep_time = _LLM_RETRY_DELAY * (2 ** (attempt - 1))
            logger.debug("Retrying in %.1fs...", sleep_time)
            time.sleep(sleep_time)
        else:
            print(f"{Colors.FAIL}❌ Operation failed after {attempt} attempts.{Colors.ENDC}")
    
    return None
