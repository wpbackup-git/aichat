import requests
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Check if Firebase has already been initialized
if not firebase_admin._apps:
    # Load the Firebase credentials from Streamlit secrets
    cred_dict = json.loads(st.secrets["firebase"]["private_key"])  # Load the private key string from secrets
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")  # Fix line breaks in the private key
    
    # Initialize Firebase with the loaded credentials
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Your chatbot logic continues as usual...


# Groq API settings
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"

st.set_page_config(page_title="Groq Chatbot + Firebase", page_icon="🤖")
st.title("🤖 AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq API call
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

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # Save to Firebase
    db.collection("chat_history").add({
        "prompt": prompt,
        "response": reply,
        "timestamp": datetime.utcnow()
    })
