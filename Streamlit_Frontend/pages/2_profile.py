import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import auth


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

# Function to fetch user profile from Firestore using the UID
def get_user_profile(uid):
    user_profile_ref = db.collection('user_profile').document(uid)
    doc = user_profile_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

# Function to save user profile to Firestore under the current user UID
def save_user_profile(uid, name, age, height, weight, gender):
    user_profile_ref = db.collection('user_profile').document(uid)
    user_profile_ref.set({
        'uid': uid,  # Save the UID in the profile document
        'name': name,  # Save the user's name
        'age': age,
        'height': height,
        'weight': weight,
        'gender': gender
    })

# Streamlit app
def main():
    st.title("User Profile Input")

    # Check if user is logged in
    if 'uid' not in st.session_state:
        st.warning("You must be logged in to access this page.")
        return

    uid = st.session_state['uid']  # UID of the currently logged-in user

    # Fetch existing user profile
    user_profile = get_user_profile(uid)

    # Prefill input fields with existing data if available
    name = st.text_input("Name", value=user_profile['name'] if user_profile else "")
    age = st.number_input("Age", min_value=0, max_value=120, value=user_profile['age'] if user_profile else 25)
    height = st.number_input("Height (cm)", min_value=0, max_value=300, value=user_profile['height'] if user_profile else 170)
    weight = st.number_input("Weight (kg)", min_value=0, max_value=300, value=user_profile['weight'] if user_profile else 70)
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(user_profile['gender']) if user_profile else 0)

    # Submit button
    if st.button("Submit"):
        if name.strip() == "":
            st.warning("Name cannot be empty!")
        else:
            save_user_profile(uid, name, age, height, weight, gender)
            st.success("Profile saved successfully!")
            st.switch_page("pages/3_Diet.py")

if __name__ == "__main__":
    main()