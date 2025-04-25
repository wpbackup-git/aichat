from datetime import datetime
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Test Firestore connection on button click
if st.button("Test Firestore Connection"):
    try:
        test_doc = {
            "test": "Hello World",
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        db.collection("test_collection").add(test_doc)
        st.success("✅ Test Write Success! Check Firestore.")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Groq API settings
GROQ_API_KEY = "your_groq_api_key"
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
    try:
        db.collection("chat_history").add({
            "prompt": prompt,
            "response": reply,
            "timestamp": datetime.utcnow()
        })
        st.success("Chat saved to Firestore.")
    except Exception as e:
        st.error(f"Error saving chat to Firestore: {e}")
