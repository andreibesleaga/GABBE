import time
import requests
import logging
from .config import (
    GABBE_API_URL,
    GABBE_API_KEY,
    GABBE_API_MODEL,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
)

logger = logging.getLogger("gabbe.llm")

_LLM_MAX_RETRIES = 3
_LLM_RETRY_DELAY = 1  # seconds


def _create_payload(prompt, system_prompt, temperature):
    return {
        "model": GABBE_API_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }


def _handle_response(response):
    response.raise_for_status()
    data = response.json()
    if "choices" in data and data["choices"]:
        content = data["choices"][0]["message"]["content"].strip()
        logger.debug("LLM Response received (%d chars)", len(content))
        return content
    
    msg = "Unexpected API response format"
    logger.error("%s: %s", msg, str(data)[:200])
    return None


def call_llm(
    prompt, system_prompt="You are a helpful assistant.", temperature=None, timeout=None
):
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

    temperature = temperature if temperature is not None else LLM_TEMPERATURE
    timeout = timeout if timeout is not None else LLM_TIMEOUT
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GABBE_API_KEY}",
    }
    payload = _create_payload(prompt, system_prompt, temperature)

    for attempt in range(1, _LLM_MAX_RETRIES + 1):
        try:
            logger.debug(
                "LLM Request (Attempt %d/%d) to %s",
                attempt,
                _LLM_MAX_RETRIES,
                GABBE_API_URL,
            )
            response = requests.post(
                GABBE_API_URL, headers=headers, json=payload, timeout=timeout
            )
            return _handle_response(response)

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 500
            if status in (429, 500, 502, 503, 504) and attempt < _LLM_MAX_RETRIES:
                logger.warning("Retriable HTTP %d error: %s", status, e)
            elif status == 401 or status == 403:
                logger.error("Authentication failed (HTTP %d). Check GABBE_API_KEY.", status)
                return None
            else:
                logger.error("Non-retriable HTTP error (status %d): %s", status, e)
                return None

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("LLM transient error: %s", e)

        except requests.exceptions.RequestException as e:
            logger.error("LLM request failed: %s", e)
            return None

        # Backoff logic
        if attempt < _LLM_MAX_RETRIES:
            sleep_time = _LLM_RETRY_DELAY * (2 ** (attempt - 1))
            logger.debug("Retrying in %.1fs...", sleep_time)
            time.sleep(sleep_time)
        else:
            logger.error("LLM call failed after %d attempts.", attempt)

    return None
