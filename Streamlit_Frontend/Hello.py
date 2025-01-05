import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import json
import requests

st.set_page_config(initial_sidebar_state="collapsed")

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

def app():
    st.title('Welcome to :violet[Diet Plan] :sunglasses:')

    # Initialize session state variables if not already set
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'uid' not in st.session_state:
        st.session_state.uid = ''  # To store the user's UID

    def sign_up_with_email_and_password(email, password, username=None, return_secure_token=True):
        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": return_secure_token
            }
            if username:
                payload["displayName"] = username
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyATYEvY2Ih0H4BRGRVXswkbjVEdn_wuCJo"}, data=payload)
            if r.status_code == 200:
                user_data = r.json()
                # Return UID along with email
                return user_data['email'], user_data['localId']
            else:
                st.warning(r.json())
        except Exception as e:
            st.warning(f'Signup failed: {e}')

    def sign_in_with_email_and_password(email=None, password=None, return_secure_token=True):
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        try:
            payload = {
                "returnSecureToken": return_secure_token
            }
            if email:
                payload["email"] = email
            if password:
                payload["password"] = password
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyATYEvY2Ih0H4BRGRVXswkbjVEdn_wuCJo"}, data=payload)
            if r.status_code == 200:
                data = r.json()
                user_info = {
                    'email': data['email'],
                    'username': data.get('displayName'),
                    'uid': data['localId']  # Get the UID here
                }
                st.session_state['uid'] = user_info['uid']
                return user_info
            else:
                st.warning(r.json())
        except Exception as e:
            st.warning(f'Signin failed: {e}')

    def reset_password(email):
        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
            payload = {
                "email": email,
                "requestType": "PASSWORD_RESET"
            }
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyATYEvY2Ih0H4BRGRVXswkbjVEdn_wuCJo"}, data=payload)
            if r.status_code == 200:
                return True, "Reset email Sent"
            else:
                error_message = r.json().get('error', {}).get('message')
                return False, error_message
        except Exception as e:
            return False, str(e)

    def f():
        try:
            userinfo = sign_in_with_email_and_password(st.session_state.email_input, st.session_state.password_input)
            st.session_state.username = userinfo['username']
            st.session_state.useremail = userinfo['email']
            st.session_state.uid = userinfo['uid']  # Store UID
            st.session_state.signedout = True
            st.session_state.signout = True

            # Add the switch to another page after successful login
            st.switch_page("pages/2_profile.py")  # Make sure this is a valid page in your app

            # Show the sidebar after successful login
            st.sidebar.title(f"Welcome, {st.session_state.username}")
            st.sidebar.write("You are logged in!")

        except Exception as e:
            st.warning(f"Login failed: {e}")

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''
        st.session_state.uid = ''  # Clear UID on signout

    def forget():
        email = st.text_input('Email')
        if st.button('Send Reset Link'):
            success, message = reset_password(email)
            if success:
                st.success("Password reset email sent successfully.")
            else:
                st.warning(f"Password reset failed: {message}")

    def additional_function():
        # New function logic here
        st.write("This is the additional function.")

    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False

    if not st.session_state.get("signedout", False):
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])

        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')

        st.session_state.email_input = email
        st.session_state.password_input = password

        if choice == 'Sign up':
            username = st.text_input("Enter your unique username")

            if st.button('Create my account'):
                user, uid = sign_up_with_email_and_password(email=email, password=password, username=username)
                if user:
                    st.session_state.uid = uid  # Store UID from signup
                    st.success('Account created successfully!')
                    st.markdown('Please Login using your email and password')
                    st.balloons()
                else:
                    st.warning("Signup failed. Please try again.")
        elif choice == 'Login':
            if st.button('Login'):
                userinfo = sign_in_with_email_and_password(email=email, password=password)
                if userinfo:
                    # Save login details to session state
                    st.session_state.username = userinfo.get('username', 'User')
                    st.session_state.useremail = userinfo['email']
                    st.session_state.uid = userinfo['uid']  # Store UID from login
                    st.session_state.signedout = False  # Reset logout state

                    # Navigate to another page
                    st.success("Login successful! Redirecting...")
                    st.session_state.logged_in = True
                    st.switch_page("pages/2_profile.py")  # Ensure this matches the name of the target page
                else:
                    st.warning("Login failed. Please check your credentials.")

        # Password reset functionality
        forget()

    # Sidebar with Sign Out button
    if st.session_state.get("signedout", False):
        with st.sidebar:
            st.markdown(f"### Welcome, {st.session_state.username}!")
            if st.button("Sign Out"):
                t()
                st.success("You have signed out successfully.")

    # Add additional function to the main UI
    additional_function()

# Redirect after login
if st.session_state.get("logged_in", False):
    # Ensure the user is redirected without rerun
    st.switch_page("pages/2_profile.py")  # Ensure this matches the name of the target page

    if st.session_state.signout:
        st.text('Name ' + st.session_state.username)
        st.text('Email id: ' + st.session_state.useremail)
        st.button('Sign out', on_click=t)

if __name__ == "__main__":
    app()