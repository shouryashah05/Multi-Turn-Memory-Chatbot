"""Streamlit UI for PS20: Multi-turn Memory Chatbot."""

from __future__ import annotations

import os
import streamlit as st
from dotenv import load_dotenv

from chat_engine import DEFAULT_MODEL, SYSTEM_PROMPT, generate_reply, get_api_key

load_dotenv()

st.set_page_config(
    page_title="Multi-turn Memory Chatbot (PS20)",
    page_icon="🧠",
    layout="centered",
)


def init_session_state() -> None:
    """Initialize Streamlit session state keys for conversation memory."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_name" not in st.session_state:
        st.session_state.model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def clear_conversation() -> None:
    """Reset the conversation history in session state."""
    st.session_state.messages = []


def main() -> None:
    init_session_state()

    st.title("🧠 Multi-turn Memory Chatbot")
    st.caption(
        "Problem Statement 20 — Remembers your conversation, name, and preferences within a session."
    )

    with st.sidebar:
        st.header("Session Settings")
        env_key_present = bool(get_api_key())
        sidebar_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="Loaded from .env" if env_key_present else "Paste GEMINI_API_KEY",
            help="Leave blank if GEMINI_API_KEY is set in your .env file.",
        )

        model_options = ["gemini-3.8-flash", "gemini-3.8-pro", "gemini-3.5-flash-lite"]
        if st.session_state.model_name not in model_options:
            model_options.insert(0, st.session_state.model_name)

        st.session_state.model_name = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(st.session_state.model_name),
        )

        st.divider()
        st.subheader("Session Memory Stats")
        total_msgs = len(st.session_state.messages)
        user_turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
        st.metric("Total Messages in Memory", total_msgs)
        st.metric("User Turns", user_turns)

        st.button("Clear Session Memory", on_click=clear_conversation, use_container_width=True)

        with st.expander("Inspect Memory Buffer"):
            if st.session_state.messages:
                st.json(st.session_state.messages)
            else:
                st.info("No messages yet. Start chatting to build session memory.")

        with st.expander("System Prompt"):
            st.write(SYSTEM_PROMPT)

    if not st.session_state.messages:
        st.info(
            "Try introducing yourself (e.g., *'Hi, I'm Shourya and I prefer concise Python examples'*), "
            "ask a few follow-up questions, and then test if the bot remembers your name and preferences!"
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking with full session history..."):
                try:
                    reply = generate_reply(
                        messages=st.session_state.messages,
                        api_key=sidebar_api_key,
                        model=st.session_state.model_name,
                    )
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as exc:
                    st.error(f"Error calling Gemini API: {exc}")
                    st.session_state.messages.pop()


if __name__ == "__main__":
    main()
