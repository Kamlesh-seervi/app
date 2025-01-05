import streamlit as st
from google.cloud import firestore
from datetime import datetime
import pytz
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Food", page_icon="🥗",layout="wide",initial_sidebar_state="collapsed")

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

# Fetch meals from Firestore
def fetch_food_data(uid, selected_date):
    try:
        formatted_date = selected_date.strftime('%d-%m-%Y')
        recommendations_ref = db.collection('user_recom_food').document(uid).collection(formatted_date).document('recommendations')
        meals = recommendations_ref.collections()
        meal_data = {}
        for meal in meals:
            meal_name = meal.id
            meal_data[meal_name] = []
            for recipe in meal.stream():
                meal_data[meal_name].append(recipe.to_dict())
        return meal_data
    except Exception as e:
        st.error(f"Error fetching food data: {e}")
        return None

# Display meals as cards
def display_meals(meal_data):
    if not meal_data:
        st.warning("No meals found for this date.")
        return

    for meal_name, recipes in meal_data.items():
        with st.expander(meal_name.capitalize()):
            for idx, recipe in enumerate(recipes):
                # Display each meal as a card
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(recipe['image_link'], width=100, caption=recipe['Name'])
                with col2:
                    st.markdown(f"**Name:** {recipe['Name']}")
                    st.markdown(f"- **Calories:** {recipe['Calories']}")
                    st.markdown(f"- **Protein:** {recipe['ProteinContent']}")
                    st.markdown(f"- **Carbs:** {recipe['CarbohydrateContent']}")

# Main app
def food_data_view_page():
    st.title("View Saved Meals")
    uid = st.session_state.get("uid")  # Use session state to get UID
    if not uid:
        st.warning("User not logged in.")
        return

    selected_date = st.date_input("Select a date to view saved meals", datetime.now())

    if st.button("Fetch Meals"):
        meal_data = fetch_food_data(uid, selected_date)
        if meal_data:
            display_meals(meal_data)

    # Add a switch (checkbox) to navigate to the Dashboard page
    if st.button("DashBoard"):
        st.switch_page("pages/4_Dashboard.py")

# Run the app
if __name__ == "__main__":
    food_data_view_page()