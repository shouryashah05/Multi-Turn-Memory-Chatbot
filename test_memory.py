"""Unit tests for the multi-turn memory chatbot engine."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from chat_engine import build_genai_contents, generate_reply, get_api_key


class FakeModels:
    """Fake Gemini models client that records received contents."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate_content(self, model: str, contents: list, config: object) -> SimpleNamespace:
        self.calls.append({"model": model, "contents": contents, "config": config})
        # Verify the full history was passed and echo the remembered name if present.
        joined = " ".join(
            part.text for item in contents for part in item.parts if getattr(part, "text", None)
        )
        if "Shourya" in joined:
            return SimpleNamespace(text="Your name is Shourya and I remember your preferences.")
        return SimpleNamespace(text="Hello! How can I help you?")


class FakeClient:
    def __init__(self) -> None:
        self.models = FakeModels()


class TestMultiTurnMemory(unittest.TestCase):
    def test_build_genai_contents_preserves_order_and_roles(self) -> None:
        history = [
            {"role": "user", "content": "Hi, I am Shourya."},
            {"role": "assistant", "content": "Nice to meet you, Shourya!"},
            {"role": "user", "content": "I prefer concise Python examples."},
        ]
        contents = build_genai_contents(history)

        self.assertEqual(len(contents), 3)
        self.assertEqual([c.role for c in contents], ["user", "model", "user"])
        self.assertEqual(contents[0].parts[0].text, "Hi, I am Shourya.")
        self.assertEqual(contents[1].parts[0].text, "Nice to meet you, Shourya!")
        self.assertEqual(contents[2].parts[0].text, "I prefer concise Python examples.")

    def test_build_genai_contents_skips_blank_messages(self) -> None:
        history = [
            {"role": "user", "content": "   "},
            {"role": "user", "content": "Hello"},
        ]
        contents = build_genai_contents(history)
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0].parts[0].text, "Hello")

    def test_generate_reply_sends_full_history_and_recalls_name(self) -> None:
        fake_client = FakeClient()
        history = [
            {"role": "user", "content": "My name is Shourya and I like dark mode."},
            {"role": "assistant", "content": "Got it, Shourya!"},
            {"role": "user", "content": "What is my name?"},
        ]
        reply = generate_reply(messages=history, client=fake_client, model="gemini-3.8-flash")

        self.assertIn("Shourya", reply)
        self.assertEqual(len(fake_client.models.calls), 1)
        sent_contents = fake_client.models.calls[0]["contents"]
        self.assertEqual(len(sent_contents), 3)

    def test_generate_reply_requires_api_key_when_no_client(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            with patch("chat_engine.load_dotenv"):
                with self.assertRaises(ValueError):
                    generate_reply(messages=[{"role": "user", "content": "Hi"}], api_key="")

    def test_get_api_key_prefers_override(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}, clear=False):
            self.assertEqual(get_api_key("  override-key  "), "override-key")

    def test_generate_reply_falls_back_on_503(self) -> None:
        class FallbackModels:
            def __init__(self) -> None:
                self.models_tried: list[str] = []

            def generate_content(self, model: str, contents: list, config: object) -> SimpleNamespace:
                self.models_tried.append(model)
                if model == "gemini-3.8-flash":
                    raise RuntimeError("503 UNAVAILABLE")
                return SimpleNamespace(text="Fallback reply for Shourya.")

        fake_client = SimpleNamespace(models=FallbackModels())
        with patch("chat_engine.time.sleep"):
            reply = generate_reply(
                messages=[{"role": "user", "content": "Hi, I'm Shourya"}],
                client=fake_client,
                model="gemini-3.8-flash",
            )
        self.assertIn("Shourya", reply)
        self.assertEqual(
            fake_client.models.models_tried,
            ["gemini-3.8-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite"],
        )


if __name__ == "__main__":
    unittest.main()
