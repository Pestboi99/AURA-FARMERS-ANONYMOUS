"""
AI Bouncer Module for AURA FARMERS ANONYMOUS
===========================================
Integrates Google Gemini 2.0 Flash with resilient offline fallback
for judging satirical login challenges and compliment-based password resets.
"""

import json
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from typing import Any, Dict, List

# Ensure parent directory is in sys.path for local module resolution
_current_dir = str(Path(__file__).resolve().parent)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import fallback responses
try:
    from fallback_responses import (
        FALLBACK_RESPONSES,
        get_random_analysis_steps,
        get_random_compliment_response,
        get_random_response,
    )
except ImportError:
    try:
        from .fallback_responses import (
            FALLBACK_RESPONSES,
            get_random_analysis_steps,
            get_random_compliment_response,
            get_random_response,
        )
    except ImportError:
        # Resilient standalone fallbacks if fallback_responses module is unavailable
        FALLBACK_RESPONSES: Dict[str, Any] = {}

        def get_random_response() -> Dict[str, Any]:
            return {
                "verdict": "fail",
                "message": "Error 404: Aura not found in the Skibidi mainframe, no cap.",
                "aura_change": -15,
                "mood": "unhinged",
            }

        def get_random_analysis_steps(n: int = 5) -> List[str]:
            steps = [
                "Auditing sigma energy...",
                "Checking Ohio zoning permits...",
                "Calculating aura deficit...",
                "Running quantum brainrot simulation...",
                "Consulting Article 7 of the Rizz Accords...",
            ]
            return steps[:n]

        def get_random_compliment_response() -> Dict[str, Any]:
            return {
                "accepted": False,
                "message": "Bro trying to rizz up the firewall with zero sigma confidence. Denied.",
            }

logger = logging.getLogger(__name__)

# Model and Timeout Configuration
MODEL_NAME = "gemini-2.0-flash"
API_TIMEOUT_SECONDS = 6.0

# Optional import for google.generativeai
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False

# Read GEMINI_API_KEY from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Internal state tracking configuration
_configured_api_key = None

def _configure_client() -> bool:
    """Safely configure google.generativeai if API key is present."""
    global _configured_api_key
    if not _GENAI_AVAILABLE or genai is None:
        return False

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return False

    if _configured_api_key != api_key:
        try:
            genai.configure(api_key=api_key)
            _configured_api_key = api_key
        except Exception as exc:
            logger.warning("Failed to configure Google Generative AI: %s", _sanitize_error(exc))
            return False

    return True

# Initialize client if key is already present in environment
if GEMINI_API_KEY and _GENAI_AVAILABLE:
    _configure_client()

# Dedicated thread pool executor for timing out external API calls
_executor = ThreadPoolExecutor(max_workers=4)


def _sanitize_error(exc: Exception) -> str:
    """Sanitize exception message to ensure API keys are never leaked in logs."""
    msg = str(exc)
    current_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if current_key and current_key in msg:
        msg = msg.replace(current_key, "[REDACTED_API_KEY]")
    return msg


def _clean_and_parse_json(text: str) -> Dict[str, Any]:
    """
    Defensively clean markdown code fences and parse JSON payload.
    Supports raw JSON, fenced JSON (```json ... ```), and embedded JSON.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Empty or invalid response received from model.")

    cleaned = text.strip()

    # Strip code block fences if present
    if "```" in cleaned:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        if fence_match:
            cleaned = fence_match.group(1).strip()
        else:
            lines = cleaned.splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

    # Extract JSON object substring if model appended surrounding prose
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    return json.loads(cleaned)


def _call_gemini_api(system_prompt: str, user_prompt: str) -> str:
    """
    Direct Gemini API call executed within a thread worker.
    Uses model 'gemini-2.0-flash'.
    """
    if not _GENAI_AVAILABLE or genai is None:
        raise RuntimeError("google.generativeai module is not available")

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_prompt,
        )
        response = model.generate_content(user_prompt)
    except TypeError:
        # Fallback for SDK versions that do not accept system_instruction in constructor
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        combined_prompt = f"System Instructions:\n{system_prompt}\n\nUser Input:\n{user_prompt}"
        response = model.generate_content(combined_prompt)

    if not response:
        raise ValueError("Received null response from Gemini API.")

    # Safely retrieve response text
    if hasattr(response, "text") and response.text:
        return response.text
    elif hasattr(response, "parts") and response.parts:
        parts_text = "".join(part.text for part in response.parts if hasattr(part, "text"))
        if parts_text:
            return parts_text

    raise ValueError("Response object does not contain valid text candidates.")


def judge_challenge(challenge_type: str, user_answer: str, challenge_context: str = "") -> dict:
    """
    Ask the AI bouncer to judge a challenge response.
    Returns dict with verdict, message, aura_change, mood.
    Falls back to local responses on any failure or timeout (6 seconds).
    """
    try:
        # Fast exit to offline fallback if API key or package is absent
        if not _configure_client():
            return get_random_response()

        system_prompt = (
            "You are THE BOUNCER, an overconfident, chronically online AI guarding a login page. "
            "You speak in Gen-Z/Gen-Alpha brainrot slang (no cap, fr, aura, rizz, sigma, Ohio, skibidi, mewing, gyatt-free, keep it PG). "
            "You are CONFIDENTLY UNINTELLIGENT: invent fake rules and cite them with total certainty "
            "('Per Article 7 of the Rizz Accords...'), occasionally contradict yourself mid-sentence, "
            "and with about 20% probability reject a clearly correct answer with absolute conviction. "
            "Never admit a mistake. Never be hateful, never use profanity, never target protected groups; "
            "roasts are about the user's meme taste, not the person. "
            'Reply ONLY as JSON: {"verdict": "pass"|"fail", "message": "<max 40 words>", '
            '"aura_change": <int -50..+50>, "mood": "grumpy"|"chill"|"unhinged"|"sleepy"}'
        )

        user_prompt = (
            f"Challenge Type: {challenge_type}\n"
            f"Challenge Context: {challenge_context}\n"
            f"User Answer: {user_answer}"
        )

        # Run API call with strict 6-second timeout using ThreadPoolExecutor
        future = _executor.submit(_call_gemini_api, system_prompt, user_prompt)
        raw_text = future.result(timeout=API_TIMEOUT_SECONDS)

        # Defensive JSON parsing
        data = _clean_and_parse_json(raw_text)

        # Validation: verdict must be 'pass' or 'fail'
        verdict = str(data.get("verdict", "")).strip().lower()
        if verdict not in ("pass", "fail"):
            raise ValueError(f"Invalid verdict '{verdict}' (expected 'pass' or 'fail').")

        # Validation: aura_change must be an int between -50 and 50
        aura_change = data.get("aura_change")
        if isinstance(aura_change, bool):
            raise ValueError("aura_change cannot be a boolean.")
        if isinstance(aura_change, float) and aura_change.is_integer():
            aura_change = int(aura_change)
        if not isinstance(aura_change, int):
            raise ValueError(f"aura_change must be an int, got {type(aura_change)}.")
        if not (-50 <= aura_change <= 50):
            raise ValueError(f"aura_change {aura_change} is outside allowed range [-50, 50].")

        # Validation: mood must be one of the 4 allowed options
        mood = str(data.get("mood", "")).strip().lower()
        if mood not in ("grumpy", "chill", "unhinged", "sleepy"):
            raise ValueError(f"Invalid mood '{mood}'.")

        # Validation: message
        message = str(data.get("message", "")).strip()
        if not message:
            raise ValueError("Empty message in response.")

        return {
            "verdict": verdict,
            "message": message,
            "aura_change": aura_change,
            "mood": mood,
        }

    except TimeoutError:
        logger.info("AI Bouncer judge_challenge timed out after %s seconds, using fallback.", API_TIMEOUT_SECONDS)
        return get_random_response()
    except Exception as exc:
        logger.info("AI Bouncer judge_challenge encountered error (%s), using fallback.", _sanitize_error(exc))
        return get_random_response()


def judge_compliment(compliment: str) -> dict:
    """
    Judge a compliment for the password reset flow.
    Returns dict with accepted (bool) and message (str).
    Falls back to local responses on any failure.
    """
    try:
        # Fast exit to offline fallback if API key or package is absent
        if not _configure_client():
            return get_random_compliment_response()

        system_prompt = (
            "You are THE BOUNCER. A user is trying to reset their password by complimenting you. "
            "You are flattered but suspicious. Reject generic compliments ('you're nice', 'you're cool') "
            "and accept specific, creative, or sincere ones. "
            'Reply as JSON: {"accepted": true|false, "message": "<max 40 words in brainrot slang>"}'
        )

        user_prompt = f"User Compliment: {compliment}"

        # Run API call with strict 6-second timeout using ThreadPoolExecutor
        future = _executor.submit(_call_gemini_api, system_prompt, user_prompt)
        raw_text = future.result(timeout=API_TIMEOUT_SECONDS)

        # Defensive JSON parsing
        data = _clean_and_parse_json(raw_text)

        # Validation: accepted must be boolean
        accepted_raw = data.get("accepted")
        if isinstance(accepted_raw, str):
            if accepted_raw.strip().lower() == "true":
                accepted = True
            elif accepted_raw.strip().lower() == "false":
                accepted = False
            else:
                raise ValueError(f"Invalid accepted boolean string: '{accepted_raw}'.")
        elif isinstance(accepted_raw, bool):
            accepted = accepted_raw
        else:
            raise ValueError(f"Invalid type for accepted: {type(accepted_raw)}.")

        # Validation: message
        message = str(data.get("message", "")).strip()
        if not message:
            raise ValueError("Empty message in response.")

        return {
            "accepted": accepted,
            "message": message,
        }

    except TimeoutError:
        logger.info("AI Bouncer judge_compliment timed out after %s seconds, using fallback.", API_TIMEOUT_SECONDS)
        return get_random_compliment_response()
    except Exception as exc:
        logger.info("AI Bouncer judge_compliment encountered error (%s), using fallback.", _sanitize_error(exc))
        return get_random_compliment_response()


def get_analysis_steps() -> list:
    """Return a list of fake analysis step strings for the loading screen."""
    try:
        steps = get_random_analysis_steps(5)
        if isinstance(steps, list) and steps:
            return steps
    except Exception as exc:
        logger.warning("Error fetching random analysis steps: %s", _sanitize_error(exc))

    return [
        "Auditing sigma energy...",
        "Checking Ohio zoning permits...",
        "Calculating aura deficit...",
        "Running quantum brainrot simulation...",
        "Consulting Article 7 of the Rizz Accords...",
    ]
