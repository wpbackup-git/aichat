import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Initialize Firebase with Realtime Database
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dualchatapp-default-rtdb.firebaseio.com/'
})

# Groq API settings
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"

# Streamlit app config
st.set_page_config(page_title="Groq Chatbot + Firebase", page_icon="🤖")
st.title("🤖 AI Chatbot")

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
prompt = st.chat_input("Type your message...")

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API Call to Groq
    with st.spinner("Groq is thinking..."):
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

    # Show assistant reply
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
        st.success("Chat saved to Firebase Realtime DB!")
    except Exception as e:
        st.error(f"Error saving to Firebase: {str(e)}")
