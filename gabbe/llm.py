# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional, Tuple

import requests

from .config import (
    GABBE_API_KEY,
    GABBE_API_MODEL,
    GABBE_API_URL,
    LLM_MAX_RETRIES,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
)

logger = logging.getLogger("gabbe.llm")

_LLM_RETRY_DELAY = 1  # seconds


def _create_payload(
    prompt: str, system_prompt: str, temperature: Optional[float]
) -> Dict[str, Any]:
    return {
        "model": GABBE_API_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }


def _handle_response(response: requests.Response) -> Tuple[Optional[str], Dict[str, Any]]:
    response.raise_for_status()
    data = response.json()
    usage = data.get("usage", {})
    if "choices" in data and data["choices"]:
        content = data["choices"][0]["message"]["content"].strip()
        logger.debug("LLM Response received (%d chars)", len(content))
        return content, usage

    msg = "Unexpected API response format"
    # Redact before logging: an error body can echo request fragments / identifiers
    # that may contain PII or secrets, and logs are a storage path like any other.
    from .audit import _redact_text

    logger.error("%s: %s", msg, _redact_text(str(data)[:200]))
    return None, usage


def _call_with_retry(
    prompt: str, system_prompt: str, temperature: Optional[float], timeout: Optional[float]
) -> Tuple[Optional[str], Dict[str, Any]]:
    """Shared retry loop. Returns (content, usage) tuple."""
    if not GABBE_API_KEY:
        raise EnvironmentError(
            "GABBE_API_KEY is not set. Set the environment variable before using LLM features."
        )

    temperature = temperature if temperature is not None else LLM_TEMPERATURE
    timeout = timeout if timeout is not None else LLM_TIMEOUT

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GABBE_API_KEY}",
    }
    payload = _create_payload(prompt, system_prompt, temperature)

    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            logger.debug(
                "LLM Request (Attempt %d/%d) to %s",
                attempt,
                LLM_MAX_RETRIES,
                GABBE_API_URL,
            )
            response = requests.post(GABBE_API_URL, headers=headers, json=payload, timeout=timeout)
            return _handle_response(response)

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 500
            if status in (429, 500, 502, 503, 504) and attempt < LLM_MAX_RETRIES:
                logger.warning("Retriable HTTP %d error: %s", status, e)
            elif status == 401 or status == 403:
                logger.error("Authentication failed (HTTP %d). Check GABBE_API_KEY.", status)
                return None, {}
            else:
                logger.error("Non-retriable HTTP error (status %d): %s", status, e)
                return None, {}

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("LLM transient error: %s", e)

        except requests.exceptions.RequestException as e:
            logger.error("LLM request failed: %s", e)
            return None, {}

        except ValueError as e:
            logger.warning("LLM returned malformed JSON (ValueError): %s", e)

        # Backoff logic
        if attempt < LLM_MAX_RETRIES:
            sleep_time = _LLM_RETRY_DELAY * (2 ** (attempt - 1))
            logger.debug("Retrying in %.1fs...", sleep_time)
            time.sleep(sleep_time)
        else:
            logger.error("LLM call failed after %d attempts.", attempt)

    return None, {}


def call_llm(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
) -> Optional[str]:
    """
    Call an LLM via an OpenAI-compatible API.

    Raises EnvironmentError if GABBE_API_KEY is not set so callers can
    distinguish missing configuration from actual API failures.
    Returns the response string on success, or None on network/API error.
    """
    content, _ = _call_with_retry(prompt, system_prompt, temperature, timeout)
    return content


def call_llm_with_usage(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    temperature: Optional[float] = None,
    timeout: Optional[float] = None,
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Like call_llm() but also returns the token usage dict for budget tracking.
    Returns (str|None, dict) where dict contains prompt_tokens, completion_tokens, total_tokens.

    Cost optimization: when GABBE_LLM_CACHE is enabled, identical
    (model, system, prompt, temperature) requests are served from a local
    content cache — zero tokens, zero cost — instead of re-calling the API.
    Only enable this for deterministic calls (e.g. temperature 0); it is OFF by
    default so it never changes behavior silently.
    """
    from .config import GABBE_API_MODEL, GABBE_DIR, GABBE_LLM_CACHE

    if not GABBE_LLM_CACHE:
        return _call_with_retry(prompt, system_prompt, temperature, timeout)

    from .cache import ContentCache, content_key

    temp = LLM_TEMPERATURE if temperature is None else temperature
    cache = ContentCache(GABBE_DIR / ".cache", namespace="llm")
    key = content_key(GABBE_API_MODEL, system_prompt, prompt, temp)
    hit = cache.get(key)
    if hit is not None:
        # Served from cache: no tokens billed for this call.
        logger.debug("LLM cache hit for %s", key[:12])
        return hit.get("content"), {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}

    content, usage = _call_with_retry(prompt, system_prompt, temperature, timeout)
    if content is not None:
        cache.set(key, {"content": content})
    return content, usage
