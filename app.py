import streamlit as st
import requests

# ================= CONFIG =================
BACKEND_URL = "http://127.0.0.1:8000"
# ========================================

st.set_page_config(page_title="Banking ChatBot", layout="wide")

# ================= SESSION STATE =================
if "chats" not in st.session_state:
    st.session_state.chats = [{"title": "Chat #1", "messages": []}]

if "current_chat" not in st.session_state:
    st.session_state.current_chat = 0

# ================= SIDEBAR =================
with st.sidebar:
    st.title("💬 Banking ChatBot")
    st.markdown("### Saved Chats")

    for i, chat in enumerate(st.session_state.chats):
        label = f"▶ {chat['title']}" if i == st.session_state.current_chat else chat["title"]
        if st.button(label, key=f"chat_{i}"):
            st.session_state.current_chat = i

    st.markdown("---")

    if st.button("➕ New Chat"):
        idx = len(st.session_state.chats) + 1
        st.session_state.chats.append(
            {"title": f"Chat #{idx}", "messages": []}
        )
        st.session_state.current_chat = len(st.session_state.chats) - 1

# ================= HEADER =================
st.markdown("## 🏦 Banking ChatBot")
st.markdown("---")

# ================= CHAT DISPLAY =================
for sender, msg in st.session_state.chats[st.session_state.current_chat]["messages"]:
    if sender == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🏦 **Bot:** {msg}")

# ================= BACKEND CALL =================
def get_reply(text: str) -> str:
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={"message": text},
            timeout=180
        )
        return response.json().get("reply", "No reply from backend.")
    except:
        return "⚠️ Backend connection error"

# ================= CHAT INPUT (SAFE) =================
user_message = st.chat_input("Ask banking questions (e.g. What is a loan?)")

if user_message:
    # user message
    st.session_state.chats[st.session_state.current_chat]["messages"].append(
        ("user", user_message)
    )

    # bot reply
    with st.spinner("Assistant is typing..."):
        bot_reply = get_reply(user_message)

    st.session_state.chats[st.session_state.current_chat]["messages"].append(
        ("bot", bot_reply)
    )

    st.rerun()
