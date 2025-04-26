import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dualchatapp-default-rtdb.firebaseio.com/'
})

ref = db.reference("test_node")
ref.set({
    "message": "Hello from Python"
})

print("✅ Data pushed successfully!")
