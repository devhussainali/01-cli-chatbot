# 🎓 Essay Mentor — CLI Chatbot

A command-line chatbot powered by **Llama 3.3 (via Groq API)** that acts as a personal English essay and précis mentor for CSS/PMS exam preparation. Built as a learning project to understand LLM fundamentals — conversation history, streaming responses, and prompt engineering.

## ✨ Features

- 💬 **Real-time streaming responses** — see the bot reply word-by-word, just like ChatGPT
- 🧠 **Persistent conversation memory** — chat history is saved to a local JSON file and reloaded on restart
- 🧹 **`/clear` command** — reset the conversation anytime without restarting the program
- 💾 **`/save <name>` command** — export the current conversation to a custom-named file
- ❓ **`/help` command** — view all available commands at any time
- 🎯 **Custom persona** — the bot is prompt-engineered to act as a CSS/PMS essay & précis mentor, giving structured feedback on grammar, vocabulary, and coherence
- 🆓 **Free to run** — uses Groq's free-tier API (no billing required)

## 🛠️ Tech Stack

- Python 3.9+
- [Groq API](https://groq.com/) (Llama 3.3 70B model)
- `python-dotenv` for environment variable management

## 📂 Project Structure

cli-chatbot/
├── .env.example # Template showing which environment variable is needed
├── .gitignore # Files/folders excluded from Git (keeps API keys safe)
├── requirements.txt # Python dependencies
├── README.md # Project documentation (this file)
└── chatbot.py # Main application code

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/cli-chatbot.git
cd cli-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Get a **free** API key from [Groq Console](https://console.groq.com/keys), then:

```bash
cp .env.example .env
```

Open the `.env` file and paste your key:

### 5. Run the chatbot

```bash
python chatbot.py
```

---

## 💻 Usage Example

CLI Chatbot - powered by Groq (Llama 3.3)
Type /help to see available commands
You: Here's my essay: "Education is very important thing for progress of nation and without education no country can develop..."
Bot: Good start! A few things to strengthen this essay:
Grammar: "is very important thing" → "is a vital factor"
Vocabulary: try "pivotal", "indispensable", or "cornerstone" instead of "important"
Structure: add a clear thesis statement in your introduction...


### Available Commands

| Command | Description |
|---|---|
| `/help` | Shows all available commands |
| `/clear` | Clears conversation history (fresh start) |
| `/save <name>` | Saves the current conversation to a custom-named file |
| `quit` / `exit` | Ends the chat session |

---

## 🧩 How It Works (Core LLM Concepts Demonstrated)

This project was built specifically to understand these foundational concepts:

- **Statelessness** — LLM APIs don't remember previous messages on their own. The entire conversation history is re-sent with every single request so the model has context.
- **Roles** — Every message is tagged as either `user` or `assistant`, which tells the model who said what.
- **System Prompt** — A separate instruction block that defines the bot's persona, tone, and rules. This is what turns a generic LLM into a specialized "mentor" tool — a basic but powerful example of prompt engineering.
- **Streaming** — Instead of waiting for the full response to generate, the API sends the reply back in small chunks (tokens), which are printed to the terminal as they arrive.
- **Persistence** — The conversation history (a list of dictionaries) is serialized to JSON and written to disk after every exchange, so nothing is lost between sessions.

---

## 🔮 Planned Improvements

- [ ] Colored terminal output for better readability (via `colorama`)
- [ ] Token usage tracking per message/session
- [ ] Support for switching between multiple mentor personas (e.g. essay vs. précis mode)
- [ ] Export conversation as a formatted PDF or text report

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋 About

Built by **Hussain Ali** — a CS student learning AI engineering fundamentals (LLMs, prompt engineering, agent frameworks, and RAG pipelines) as part of a self-directed roadmap.