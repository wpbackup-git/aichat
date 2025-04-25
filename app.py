import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Access the Firebase credentials from Streamlit secrets
firebase_key_str = st.secrets["firebase"]["key"]

# Debugging: print the key to check its format
st.write("Firebase Key: ", firebase_key_str)

# Try loading the JSON string
try:
    firebase_key = json.loads(firebase_key_str)
except json.decoder.JSONDecodeError as e:
    st.error(f"JSON Decode Error: {str(e)}")
    st.stop()

# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key)  # Firebase service key
    firebase_admin.initialize_app(cred)
else:
    st.write("Firebase app already initialized")

# Initialize Firestore
db = firestore.client()

# Function to add messages to Firestore
def add_to_firestore(data):
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            db.collection("chat_history").add(data)
            st.success("Message added to chat history.")
            break
        except Exception as e:
            st.error(f"Error: {e}")
            if attempt < retry_attempts - 1:
                st.info(f"Retrying... Attempt {attempt + 2}/{retry_attempts}")
                time.sleep(3)
            else:
                st.error("Failed to add message after several attempts.")
                break

# Streamlit UI
st.title("AI Chat App")
user_message = st.text_input("Enter your message:")

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
    msg_data = msg.to_dict()
    ts = msg_data.get("timestamp")
    readable_time = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else "Time not available"
    st.markdown(f"🗨️ **{msg_data['message']}**  \n🕒 *{readable_time}*")
