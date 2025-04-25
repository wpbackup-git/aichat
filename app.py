import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    firebase_config = st.secrets["firebase"]
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Function to add messages to Firestore with retry logic
def add_to_firestore(data):
    retry_attempts = 5
    retry_message = st.empty()  # Create an empty placeholder for retry message

    for attempt in range(retry_attempts):
        try:
            # Add data to Firestore collection
            db.collection("chat_history").add(data)
            st.success("Message added to chat history.")
            break
        except Exception as e:
            retry_message.write(f"Error: {e}")
            if attempt < retry_attempts - 1:
                retry_message.info(f"Retrying... Attempt {attempt + 2}/{retry_attempts}")
            else:
                st.error("Failed to add message after several attempts.")
                break

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

# Display the chat history
st.subheader("Chat History")
messages_ref = db.collection("chat_history").order_by("timestamp", direction=firestore.Query.ASCENDING)
messages = messages_ref.stream()

for msg in messages:
    st.write(f"**{msg.to_dict()['message']}**")
