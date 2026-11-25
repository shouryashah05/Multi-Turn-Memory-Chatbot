"""Core multi-turn conversation engine using the Google GenAI SDK."""

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-pro"]

SYSTEM_PROMPT = (
    "You are a helpful, friendly, and attentive AI assistant with session memory. "
    "Pay close attention to details the user shares earlier in the conversation—such as "
    "their name, role, interests, preferences, goals, and constraints—and naturally recall "
    "and use them in later turns when relevant. "
    "If the user asks what you remember about them, accurately summarize only the facts "
    "they have explicitly shared in the current conversation. Never invent details they did not state."
)


def get_api_key(override_key: str | None = None) -> str:
    """Return the Gemini API key from an explicit override or environment variables."""
    if override_key and override_key.strip():
        return override_key.strip()
    load_dotenv()
    return os.getenv("GEMINI_API_KEY", "").strip()


def build_genai_contents(messages: list[dict[str, str]]) -> list[types.Content]:
    """Convert session chat messages into Gemini Content objects preserving full history.

    Each message dict must have 'role' ('user' or 'assistant'/'model') and 'content'.
    """
    contents: list[types.Content] = []
    for msg in messages:
        text = msg.get("content", "").strip()
        if not text:
            continue
        role = "model" if msg.get("role") in ("assistant", "model") else "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=text)],
            )
        )
    return contents


def generate_reply(
    messages: list[dict[str, str]],
    api_key: str | None = None,
    model: str | None = None,
    system_prompt: str = SYSTEM_PROMPT,
    client: Any | None = None,
) -> str:
    """Send the full conversation history to Gemini and return the assistant reply."""
    resolved_key = get_api_key(api_key)
    if client is None and not resolved_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file or enter it in the sidebar."
        )

    contents = build_genai_contents(messages)
    if not contents:
        raise ValueError("Conversation history is empty; cannot generate a reply.")

    active_client = client or genai.Client(api_key=resolved_key)
    selected_model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    candidate_models = [selected_model] + [m for m in FALLBACK_MODELS if m != selected_model]

    last_exc: Exception | None = None
    for candidate in candidate_models:
        for attempt in range(2):
            try:
                response = active_client.models.generate_content(
                    model=candidate,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                    ),
                )
                return (response.text or "").strip() or "(Empty response from model)"
            except Exception as exc:
                last_exc = exc
                msg = str(exc)
                is_transient = "503" in msg or "UNAVAILABLE" in msg or "429" in msg
                is_not_found = "404" in msg or "NOT_FOUND" in msg
                if is_transient and attempt == 0:
                    time.sleep(1.5)
                    continue
                if is_transient or is_not_found:
                    break
                raise

    assert last_exc is not None
    raise last_exc
