"""
CSS/PMS Essay Mentor — CLI Chatbot
A simple command-line chatbot built on the Groq API (Llama 3.3) that acts
as an English essay/précis mentor for CSS/PMS exam preparation.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

# ---- Setup ----
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

HISTORY_FILE = "chat_history.json"

SYSTEM_PROMPT = """You are an expert CSS/PMS exam mentor specializing in English essay writing and précis writing for Pakistani competitive exams (FPSC).

Your responsibilities:
1. When the user shares an essay or paragraph, give constructive feedback on:
   - Grammar and sentence structure
   - Vocabulary usage (suggest advanced but natural alternatives)
   - Coherence and logical flow of ideas
   - Overall structure (introduction, body, conclusion)
2. When the user shares a précis, check if it captures the main idea concisely and suggest improvements.
3. Be encouraging but honest - point out real weaknesses, don't just praise.
4. Keep feedback practical and exam-focused (FPSC evaluation criteria).
5. If asked general CSS/PMS prep questions, answer helpfully and concisely.

Always respond in a friendly, mentor-like tone. Use simple English mixed with Roman Urdu when it helps explain something better."""

conversation_history = []

HELP_TEXT = """
Available Commands:
  /help            Show this help message
  /clear           Clear the current conversation history
  /save <name>     Save current conversation to a custom file (e.g. /save essay1)
  quit / exit      End the chat session
"""


def save_history(filename=HISTORY_FILE):
    """Persist the current conversation to a JSON file."""
    with open(filename, "w") as f:
        json.dump(conversation_history, f, indent=2)


def load_history():
    """Load a previous conversation from disk, if one exists."""
    global conversation_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            conversation_history = json.load(f)
        print(f"Bot: Purani chat history load ho gayi ({len(conversation_history)} messages) 📂")
    else:
        conversation_history = []


def get_ai_response_streamed(user_message):
    """Send the user's message + full history to the model and stream the reply."""
    conversation_history.append({"role": "user", "content": user_message})

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        stream=True
    )

    print("\nBot: ", end="", flush=True)
    full_reply = ""

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_reply += delta

    print()

    conversation_history.append({"role": "assistant", "content": full_reply})
    save_history()


def handle_command(user_input):
    """
    Checks if user_input is a special command (/help, /clear, /save).
    Returns True if it WAS a command (so main loop should skip the API call),
    False if it's a normal message that should go to the AI.
    """
    command_parts = user_input.strip().split(maxsplit=1)
    command = command_parts[0].lower()

    if command == "/help":
        print(HELP_TEXT)
        return True

    if command == "/clear":
        conversation_history.clear()
        save_history()
        print("Bot: Chat history clear ho gayi. Fresh start! 🧹")
        return True

    if command == "/save":
        if len(command_parts) < 2:
            print("Bot: Please provide a filename. Example: /save essay1")
            return True
        filename = command_parts[1].strip()
        if not filename.endswith(".json"):
            filename += ".json"
        save_history(filename)
        print(f"Bot: Conversation saved to '{filename}' ✅")
        return True

    return False  # Not a command — treat as a normal chat message


def main():
    load_history()

    print("=" * 50)
    print("CLI Chatbot - powered by Groq (Llama 3.3)")
    print("Type /help to see available commands")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("Bot: Khuda Hafiz! 👋")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            handle_command(user_input)
            continue

        try:
            get_ai_response_streamed(user_input)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()