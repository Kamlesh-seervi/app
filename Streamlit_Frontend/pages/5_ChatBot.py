import streamlit as st
import requests
from firebase_admin import credentials, firestore
import firebase_admin

st.set_page_config(
    page_title="Diet Planner Chatbot", 
    page_icon="🤖", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("./path-to-your-firebase-adminsdk.json")  # Provide the correct path to your Firebase credentials
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Chatbot Class
class Chatbot:
    def __init__(self):
        # Initialize session state for conversation and favorites
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
        if 'favorites' not in st.session_state:
            st.session_state.favorites = []

    def generate_response(self, message):
        st.session_state.conversation.append({
            'role': 'user',
            'content': message
        })

        try:
            response = requests.post('http://backend:8080/chat', json={
                'message': message,
                'conversation_history': st.session_state.conversation
            })

            if response.status_code == 200:
                data = response.json()
                st.session_state.conversation.append({
                    'role': 'assistant',
                    'content': data.get('response', "No response generated.")
                })
            else:
                st.session_state.conversation.append({
                    'role': 'assistant',
                    'content': f"**Error:** Unable to fetch response. Status code: {response.status_code}"
                })

        except requests.RequestException as e:
            st.session_state.conversation.append({
                'role': 'assistant',
                'content': f"**Network Error:** {str(e)}"
            })

# Page title
st.markdown("<h1 style='text-align: center;'>Diet Planner Chatbot 🤖</h1>", unsafe_allow_html=True)

# Initialize the chatbot
chatbot = Chatbot()

# Conversation form
with st.form("chat_form", clear_on_submit=True):
    message = st.text_input("💬 Type your message:")
    sent = st.form_submit_button("Send")

# Generate response
if sent and message:
    with st.spinner("The chatbot is thinking..."):
        chatbot.generate_response(message)

# Get user profile from Firestore
def get_user_profile(uid):
    user_profile_ref = db.collection('user_profile').document(uid)
    doc = user_profile_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        st.warning("User profile not found.")
        return None

# Save favorite dish to Firestore and include user name
def save_favorite_dish(uid, favorite_dish):
    # Fetch the user's profile to get the name
    user_profile = get_user_profile(uid)
    if not user_profile:
        st.warning("Unable to fetch user profile.")
        return
    
    user_name = user_profile.get('name', '')  # Fetch user's name from the profile

    # Retrieve the favorites from the user_fav collection
    user_fav_ref = db.collection('user_fav').document(uid)
    user_fav_doc = user_fav_ref.get()

    # Initialize the favorites list if document does not exist
    if user_fav_doc.exists:
        fav_dishes = user_fav_doc.to_dict().get('favorites', [])
    else:
        fav_dishes = []

    # Add the new favorite dish
    fav_dishes.append(favorite_dish)

    # Update Firestore with the new favorites list and user's name
    user_fav_ref.set({
        'favorites': fav_dishes,
        'name': user_name  # Save the user's name in the user_fav document
    })

# Display conversation
if st.session_state.conversation:
    for i, msg in enumerate(st.session_state.conversation):
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        elif msg['role'] == 'assistant':
            with st.chat_message("assistant"):
                st.write(msg['content'])
                
                # Heart button for saving favorites
                if st.button("❤️", key=f"fav_{i}"):
                    # Add the message content to the favorites list
                    st.session_state.favorites.append(msg['content'])
                    st.success(f"'{msg['content']}' has been added to your favorites!")

                    # Ensure the user is logged in
                    if 'uid' not in st.session_state:
                        st.warning("You must be logged in to save favorites.")
                    else:
                        uid = st.session_state['uid']
                        user_profile = get_user_profile(uid)  # Optional: Fetch user profile info

                        # Save favorite dish to Firestore
                        save_favorite_dish(uid, msg['content'])

