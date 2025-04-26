import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# ✅ Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # Your service account key JSON file
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://dualchatapp-default-rtdb.firebaseio.com/'
    })

# 🔐 Groq API Configuration
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"

# 💬 Streamlit UI Setup
st.set_page_config(page_title="Groq Chatbot + Firebase", page_icon="🤖")
st.title("🤖 AI Chatbot")

# 🔄 Session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📜 Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Chat input
prompt = st.chat_input("Type your message...")

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 🤖 Call Groq API
    with st.spinner("Groq is thinking..."):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": st.session_state.messages
                }
            )
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
        except Exception as e:
            reply = "❌ Error getting response from Groq."
            st.error(str(e))

    # Show AI reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # ✅ Save chat to Firebase Realtime Database
    try:
        ref = db.reference("chat_history")
        ref.push({
            "prompt": prompt,
            "response": reply,
            "timestamp": datetime.utcnow().isoformat()
        })
        st.success("✅ Chat saved to Firebase!")
    except Exception as e:
        st.error(f"❌ Error saving to Firebase: {str(e)}")
