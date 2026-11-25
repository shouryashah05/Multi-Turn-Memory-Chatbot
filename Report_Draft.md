# Two-Page Procedure Report Draft (PS20)

> Copy this into Word or Google Docs (A4, 12-pt font), fill in your details and screenshots, and export as `Report.pdf`.

---

## Header
- **Project Title:** Multi-turn Memory Chatbot
- **PS Number:** PS20
- **Name:** `<Your Name>`
- **Roll Number:** `<Your Roll Number>`
- **Class:** `<Your Class / Section>`
- **GitHub Link:** `https://github.com/<username>/llm-ps20-<RollNo>`

## Problem Statement
Basic chatbots treat each prompt independently and forget earlier messages. This project builds a multi-turn memory chatbot that remembers the ongoing conversation, including the user's name and preferences, throughout a session—helping users have natural, personalized interactions without repeating themselves.

## Tools & Model
- **Language:** Python 3.12
- **Libraries:** `google-genai`, `python-dotenv`, `streamlit`
- **LLM Used:** Gemini 3.8 Flash via Google Gemini API
- **UI Framework:** Streamlit

## Procedure
1. Obtained a free Gemini API key from Google AI Studio and stored it securely in a `.env` file (excluded from Git via `.gitignore`).
2. Tested multi-turn prompts in Google AI Studio to verify that passing prior user/model turns enabled accurate recall of names and preferences.
3. Built `chat_engine.py` to convert the session message list into `types.Content` objects (`user` and `model` roles) and send the full history to `gemini-3.8-flash` with a memory-aware system instruction.
4. Built `app.py` with Streamlit using `st.session_state.messages` to persist chat history across reruns, along with a sidebar showing memory stats, a live memory buffer inspector, and a reset button.
5. Verified multi-turn recall across 5+ test inputs (introducing name, coding/food preferences, follow-up questions, and explicit recall checks) and wrote unit tests in `test_memory.py`.

## Prompt Used
**Final System Prompt:**
> "You are a helpful, friendly, and attentive AI assistant with session memory. Pay close attention to details the user shares earlier in the conversation—such as their name, role, interests, preferences, goals, and constraints—and naturally recall and use them in later turns when relevant. If the user asks what you remember about them, accurately summarize only the facts they have explicitly shared in the current conversation. Never invent details they did not state."

**One Improvement Made:**
Initially, the prompt only said *"Remember the user's name and preferences."* When asked what it knew about the user, the model occasionally guessed unstated details. Adding *"accurately summarize only the facts they have explicitly shared in the current conversation. Never invent details they did not state"* eliminated hallucinated user attributes.

## Results
*(Insert 1–2 screenshots of the running Streamlit app showing a multi-turn conversation where the user introduces their name and preferences, asks unrelated questions, and then tests recall.)*

- **Sample Input (Turn 1):** `"Hi, my name is Shourya and I prefer short, bulleted Python answers."`
- **Sample Input (Turn 3):** `"What is my name and how do I prefer my answers?"`
- **Sample Output:** `"Your name is Shourya, and you prefer short, bulleted Python answers."`

## Challenges
1. **Stateless API calls:** Sending only the latest user message caused the bot to forget earlier turns. Fixed by storing all turns in `st.session_state.messages` and passing the full `contents` list on every request.
2. **Error recovery on failed API calls:** If an API error occurred (e.g., missing key or rate limit), the failed user message stayed in history without a reply. Fixed by popping the failed user message on exception so the session remains clean.

## Conclusion
- **What works:** The chatbot reliably remembers the user's name, preferences, and conversation context across multiple turns within a session, and users can inspect or clear memory from the sidebar.
- **What doesn't:** Memory is tied to the active browser session (`st.session_state`) and resets when the page is refreshed or the server restarts.
- **Future improvement:** Persist conversation memory to a local database (e.g., SQLite) or summarize older turns automatically to stay within token limits for very long chats.
