import re
import time
import logging
from groq import RateLimitError
from config import client

logger = logging.getLogger(__name__)

MAX_RATE_LIMIT_RETRIES = 3


def _parse_retry_after(error: RateLimitError) -> float:
    """Extract the suggested wait time from a Groq RateLimitError message."""
    msg = str(error)
    match = re.search(r"try again in (\d+(?:\.\d+)?)s", msg, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 10.0  # default fallback


def call_groq_with_retry(model: str, messages: list, temperature: float = 0.1, max_tokens: int = 4000) -> object:
    """
    Call the Groq chat completions API with automatic retry on rate limit errors.
    Returns the full response object (not just text) so callers can use it as before.
    """
    for retry in range(MAX_RATE_LIMIT_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response
        except RateLimitError as e:
            wait_time = _parse_retry_after(e)
            # Add a small buffer and exponential factor for subsequent retries
            wait_time = wait_time + (retry * 2) + 1
            logger.warning(
                f"Rate limit hit (attempt {retry + 1}/{MAX_RATE_LIMIT_RETRIES}). "
                f"Waiting {wait_time:.1f}s before retrying..."
            )
            time.sleep(wait_time)

    # Final attempt — let it raise if it still fails
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response
