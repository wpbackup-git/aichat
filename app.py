import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os
import time
from google.api_core.exceptions import RetryError

# Initialize Firebase
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Function to add messages to Firestore with retry logic
def add_to_firestore(data):
    for _ in range(5):  # Try up to 5 times
        try:
            # Add data to Firestore collection
            db.collection("chat_history").add(data)
            st.success("Message added to chat history.")
            break  # If successful, exit the loop
        except RetryError as e:
            st.error(f"Retrying due to error: {e}")
            time.sleep(2)  # Wait for 2 seconds before retrying

# Function to display chat history
def display_chat_history():
    try:
        # Fetch all messages from Firestore
        chats_ref = db.collection("chat_history").order_by("timestamp").stream()
        for chat in chats_ref:
            message = chat.to_dict()
            st.write(f"{message['timestamp']} - {message['message']}")
    except Exception as e:
        st.error(f"Error fetching chat history: {e}")

# Streamlit UI
st.title("AI Chat App")

# Input fields for user message
user_message = st.text_input("Enter your message:")

# Button to submit message
if st.button("Send"):
    if user_message:
        message_data = {
            "message": user_message,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        add_to_firestore(message_data)
    else:
        st.warning("Please enter a message.")

# Display chat history
st.subheader("Chat History:")
display_chat_history()

