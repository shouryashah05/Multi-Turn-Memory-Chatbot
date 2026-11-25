# Multi-turn Memory Chatbot (Problem Statement 20)

## Problem Statement
Basic bots forget earlier messages. Build a chatbot that remembers the conversation and the user's name and preferences within a session.

## How It Works
- Maintains a `messages` list in `st.session_state` across turns.
- Converts the entire conversation history into Gemini `Content` objects (`user` and `model` roles) and sends the full history on every API call.
- Uses a tailored system prompt instructing the model to recall user details (name, preferences, goals) shared earlier in the session without inventing facts.
- Includes a sidebar **Session Memory Inspector** to view the live message buffer and reset memory on demand.

## Setup & How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your API key:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Add your free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) to `.env`:
     ```env
     GEMINI_API_KEY=your_api_key_here
     ```
   *(Alternatively, you can paste the API key directly into the Streamlit sidebar at runtime.)*

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Run automated tests:**
   ```bash
   python -m unittest test_memory.py -v
   ```

## Screenshots
*(Add 1–2 screenshots of your running Streamlit app here before pushing to GitHub.)*
