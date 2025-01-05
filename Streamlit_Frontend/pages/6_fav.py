import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin

# Set page configuration
st.set_page_config(page_title="Favorites", page_icon="❤️", layout="wide", initial_sidebar_state="collapsed")

# Initialize Firebase
# Initialize Firebase if not already done
if not firebase_admin._apps:
    firebase_config = firebase_config = st.secrets["firebase"]
    cred = credentials.Certificate({
        "type": firebase_config["type"],
        "project_id": firebase_config["project_id"],
        "private_key_id": firebase_config["private_key_id"],
        "private_key": firebase_config["private_key"].replace('\\n', '\n'),  # Handle escaped newlines
        "client_email": firebase_config["client_email"],
        "client_id": firebase_config["client_id"],
        "auth_uri": firebase_config["auth_uri"],
        "token_uri": firebase_config["token_uri"],
        "auth_provider_x509_cert_url": firebase_config["auth_provider_x509_cert_url"],
        "client_x509_cert_url": firebase_config["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Page title
st.markdown("<h1 style='text-align: center;'>Your Favorite Recipes ❤️</h1>", unsafe_allow_html=True)

def get_user_profile(uid):
    user_profile_ref = db.collection('user_profile').document(uid)
    doc = user_profile_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        st.warning("User profile not found.")
        return None

# Function to get favorites from Firestore
def get_user_favorites(uid):
    user_fav_ref = db.collection('user_fav').document(uid)
    user_fav_doc = user_fav_ref.get()
    if user_fav_doc.exists:
        return user_fav_doc.to_dict().get('favorites', [])
    else:
        return []

# Function to save a new favorite dish with user's name to Firestore
def save_favorite_dish(uid, favorite_dish, user_name):
    user_fav_ref = db.collection('user_fav').document(uid)
    user_fav_doc = user_fav_ref.get()
    
    if user_fav_doc.exists:
        # Get existing favorites or initialize it as an empty list
        fav_dishes = user_fav_doc.to_dict().get('favorites', [])
    else:
        fav_dishes = []
    
    # Add the new favorite dish to the list if it's not already there
    if favorite_dish not in fav_dishes:
        fav_dishes.append(favorite_dish)
    
    # Save the updated list of favorites and the user's name in the document
    user_fav_ref.set({
        'favorites': fav_dishes,
        'user_name': user_name  # Save the current user's name
    })

# Ensure the user is logged in
if 'uid' not in st.session_state:
    st.warning("You must be logged in to access this page.")
else:
    uid = st.session_state['uid']  # UID of the logged-in user
    user_profile = get_user_profile(uid)
    
    # Get the user's favorite dishes from Firestore
    favorites = get_user_favorites(uid)

    # Initialize or update session state favorites if needed
    if 'favorites' not in st.session_state:
        st.session_state.favorites = favorites

    # Display favorites
    if favorites:
        for i, favorite in enumerate(favorites):
            st.write(f"**Recipe {i + 1}:** {favorite}")
        
    else:
        st.info("No favorites added yet! Go back to the chatbot and add some. 😊")

    # Ensure the user's name is available, and save a new favorite dish if added
    if user_profile:
        user_name = user_profile.get('name', 'Unknown')  # Default to 'Unknown' if name is not found
        # If a favorite dish is selected in the session, save it
        if 'new_favorite' in st.session_state:
            new_favorite = st.session_state['new_favorite']
            save_favorite_dish(uid, new_favorite, user_name)
            st.success(f"'{new_favorite}' has been added to your favorites!")
            # Clear the new favorite from session state after adding
            del st.session_state['new_favorite']    