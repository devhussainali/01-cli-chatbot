"""
AI Assistant — Web Interface
A clean, professional chat interface for a general-purpose AI assistant,
built with Streamlit. Backed by Llama 3.3 via the Groq API.
"""

import os
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")

# Change this to customize the assistant's behavior/persona.
BASE_SYSTEM_PROMPT = "You are a helpful, knowledgeable, and friendly AI assistant. Give clear, well-structured answers."

MEMORY_FILE = "user_memory.json"

# Simple patterns to auto-detect a name mentioned in conversation.
# This is a lightweight heuristic, not a full NLP solution — good enough for
# understanding how persistent memory works.
NAME_PATTERNS = [
    r"\bmy name is ([A-Za-z]+)",
    r"\bi am ([A-Za-z]+)(?:\s|$|,|\.)",
    r"\bcall me ([A-Za-z]+)",
    r"\bmujhe ([A-Za-z]+) kehte",
]


def load_memory():
    """Load saved facts about the user from disk."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_memory(memory):
    """Persist facts about the user to disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def extract_and_store_facts(user_message, memory):
    """
    Looks at the user's message for things worth remembering:
    - Explicit: 'remember: <fact>' or 'remember that <fact>'
    - Implicit: name mentions like 'my name is X'
    Returns True if memory was updated.
    """
    updated = False
    lower_msg = user_message.lower()

    # Explicit "remember: ..." or "remember that ..." command
    explicit_match = re.search(r"remember(?:\s+that)?[:\s]+(.*)", lower_msg)
    if explicit_match:
        fact = explicit_match.group(1).strip()
        if fact:
            memory.setdefault("notes", [])
            if fact not in memory["notes"]:
                memory["notes"].append(fact)
                updated = True

    # Implicit name detection
    for pattern in NAME_PATTERNS:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            name = match.group(1).capitalize()
            if memory.get("name") != name:
                memory["name"] = name
                updated = True
            break

    if updated:
        save_memory(memory)

    return updated


def send_transcript_email(recipient_email, conversation_history):
    """
    Sends the conversation transcript to the given email address using Gmail's SMTP server.
    Requires SENDER_EMAIL and SENDER_APP_PASSWORD to be set in .env
    (SENDER_APP_PASSWORD must be a Gmail "App Password", not your normal password).
    """
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
        return False, "Email is not configured. Add SENDER_EMAIL and SENDER_APP_PASSWORD to your .env file."

    transcript = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in conversation_history
    )

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = "Your AI Assistant Conversation Transcript"
    msg.attach(MIMEText(transcript, "plain"))

    try:
        # Gmail's SMTP server, using TLS encryption on port 587
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
        return True, f"Transcript sent to {recipient_email} ✅"
    except Exception as e:
        return False, f"Failed to send email: {e}"


def build_system_prompt(memory):
    """Combine the base persona with any known facts about the user."""
    if not memory:
        return BASE_SYSTEM_PROMPT

    facts_lines = []
    if memory.get("name"):
        facts_lines.append(f"- The user's name is {memory['name']}.")
    for note in memory.get("notes", []):
        facts_lines.append(f"- {note}")

    if not facts_lines:
        return BASE_SYSTEM_PROMPT

    facts_block = "\n".join(facts_lines)
    return f"{BASE_SYSTEM_PROMPT}\n\nHere is what you know about the user from past conversations:\n{facts_block}\n\nUse this naturally when relevant, without explicitly saying 'according to my memory'."

st.set_page_config(page_title="AI Assistant", page_icon="💬", layout="centered")

# ---------------------------------------------------------------------------
# Clean, minimal chat UI styling — light background, dark sidebar,
# single accent color. No theme-specific branding, just a simple,
# professional chatbot look (similar to ChatGPT / Claude).
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #FFFFFF;
    color: #1A1A1A;
}

/* Header */
.app-header {
    padding: 0.5rem 0 1.2rem 0;
    border-bottom: 1px solid #EAEAEA;
    margin-bottom: 1.2rem;
}
.app-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1A1A1A;
    margin: 0;
}
.app-header p {
    color: #6B6B6B;
    font-size: 0.9rem;
    margin: 0.2rem 0 0 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #17171F;
}
section[data-testid="stSidebar"] * {
    color: #EDEDED !important;
}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}
.stat-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
}
.stat-number {
    font-size: 1.4rem;
    color: #818CF8 !important;
    font-weight: 700;
}
.stat-label {
    font-size: 0.72rem;
    opacity: 0.75;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Chat bubbles — explicit text color fixes the "invisible text" issue
   that happens when the system is on a dark theme */
[data-testid="stChatMessage"] {
    background: #F7F7F8;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.7rem;
    border: 1px solid #ECECEC;
    color: #1A1A1A !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #1A1A1A !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #EEF0FF;
    border: 1px solid #DCE0FF;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
    background-color: #4F46E5 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("""
<div class="app-header">
    <h1>💬 AI Assistant</h1>
    <p>Powered by Llama 3.3 (Groq)</p>
</div>
""", unsafe_allow_html=True)

# ---- Session state ----
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "user_memory" not in st.session_state:
    st.session_state.user_memory = load_memory()

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## Session")

    user_msgs = sum(1 for m in st.session_state.conversation_history if m["role"] == "user")

    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{user_msgs}</div>
        <div class="stat-label">Messages sent</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{st.session_state.total_tokens}</div>
        <div class="stat-label">Tokens used</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.total_tokens = 0
        st.rerun()

    if st.session_state.conversation_history:
        transcript = "\n\n".join(
            f"{'You' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in st.session_state.conversation_history
        )
        st.download_button(
            "💾 Download transcript",
            data=transcript,
            file_name="chat_transcript.txt",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("## 📧 Send Transcript")
        recipient = st.text_input("Recipient email", placeholder="someone@example.com")
        if st.button("Send via Email", use_container_width=True):
            if recipient:
                success, message = send_transcript_email(recipient, st.session_state.conversation_history)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please enter a recipient email first.")

    st.markdown("---")
    st.markdown("## 🧠 Memory")

    mem = st.session_state.user_memory
    if mem.get("name") or mem.get("notes"):
        if mem.get("name"):
            st.markdown(f"**Name:** {mem['name']}")
        for note in mem.get("notes", []):
            st.markdown(f"- {note}")
    else:
        st.markdown("*Nothing remembered yet. Try saying 'my name is...' or 'remember: I like chess'.*")

    if st.button("🗑️ Forget everything", use_container_width=True):
        st.session_state.user_memory = {}
        save_memory({})
        st.rerun()

# ---- Render conversation ----
for message in st.session_state.conversation_history:
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---- Chat input ----
user_input = st.chat_input("Message the assistant...")

if user_input:
    # Check the message for anything worth remembering permanently
    extract_and_store_facts(user_input, st.session_state.user_memory)

    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        current_system_prompt = build_system_prompt(st.session_state.user_memory)
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=[{"role": "system", "content": current_system_prompt}] + st.session_state.conversation_history,
            stream=True
        )

        usage_holder = {}

        def token_generator():
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                groq_meta = getattr(chunk, "x_groq", None)
                if groq_meta is not None:
                    usage = getattr(groq_meta, "usage", None)
                    if usage:
                        usage_holder["total"] = usage.total_tokens

        full_reply = st.write_stream(token_generator())

        if "total" in usage_holder:
            st.session_state.total_tokens += usage_holder["total"]

    st.session_state.conversation_history.append({"role": "assistant", "content": full_reply})
    st.rerun()