"""
AI Assistant — Web Interface
A clean, professional chat interface for a general-purpose AI assistant,
built with Streamlit. Backed by Llama 3.3 via the Groq API.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Change this to customize the assistant's behavior/persona.
SYSTEM_PROMPT = "You are a helpful, knowledgeable, and friendly AI assistant. Give clear, well-structured answers."

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

# ---- Render conversation ----
for message in st.session_state.conversation_history:
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---- Chat input ----
user_input = st.chat_input("Message the assistant...")

if user_input:
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.conversation_history,
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