import streamlit as st
import pandas as pd
from firebase_admin import firestore
import random
from streamlit_echarts import st_echarts
from firebase_admin import credentials, firestore
import firebase_admin 
from random import uniform as rnd
from ImageFinder.ImageFinder import get_images_links as find_image
from datetime import datetime 
import pytz

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title='dashboard')
if not firebase_admin._apps:
    cred = credentials.Certificate("./diet-8571f-firebase-adminsdk-d43ko-de38d05eff.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
nutritions_values=['Calories','CholesterolContent','CarbohydrateContent','FiberContent','ProteinContent']
class Person:
    def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.meals_calories_perc = meals_calories_perc
        self.weight_loss = weight_loss

    @staticmethod
    def fetch_username(uid):
        """Fetch the username from Firestore using the UID."""
        db = firestore.client()
        try:
            user_doc = db.collection('user_profile').document(uid).get()
            if user_doc.exists:
                return user_doc.to_dict().get('name', 'User')
            else:
                return None
        except Exception as e:
            st.warning(f"Failed to fetch username: {e}")
            return None

    def fetch_user_data(uid):
        """Fetch the user's BMI, calories, and weight loss option from Firestore."""
        db = firestore.client()
        try:
            user_data_doc = db.collection('user_calories').document(uid).get()
            if user_data_doc.exists:
                data = user_data_doc.to_dict()
                bmi = data.get('bmi', 'N/A')
                calories = data.get('calories', 'N/A')
                weight_loss_option = data.get('weight_loss_option', 'N/A')
                return bmi, calories, weight_loss_option
            else:
                return None, None, None
        except Exception as e:
            st.warning(f"Failed to fetch user data: {e}")
            return None, None, None

    def get_random_motivation():
        """Get a random motivational health-related message."""
        messages = [
            "Every step is progress, no matter how small.",
            "Your body deserves the best care.",
            "Take care of your body; it's the only place you have to live.",
            "A healthy outside starts from the inside.",
            "Push yourself because no one else is going to do it for you.",
            "Stay positive, work hard, and make it happen!",
            "Good health is not something we can buy. However, it can be an invaluable savings account.",
            "Don’t wish for a healthy body; work for it.",
            "Your health is your greatest wealth.",
            "Small daily improvements lead to stunning results over time."
        ]
        return random.choice(messages)

    def calculate_bmr(self):
        """Calculate the Basal Metabolic Rate (BMR)."""
        if self.gender == "male":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr

    def calories_calculator(self):
        """Calculate the total maintenance calories based on activity level."""
        activities = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight = weights[activities.index(self.activity)]
        maintain_calories = self.calculate_bmr() * weight
        return maintain_calories


def dashboard():
    st.title("Dashboard")
    if 'uid' not in st.session_state:
        st.warning("You must be logged in to access this page.")
    else:
        uid = st.session_state['uid'] 
    # Ensure UID is in session state
    if 'uid' not in st.session_state or not st.session_state.uid:
        st.warning("You are not logged in. Please log in to access your dashboard.")
        return

    # Fetch username from Firestore
    username = Person.fetch_username(st.session_state.uid)
    if not username:
        username = "User"  # Default fallback

    # Get a random motivational message
    motivation = Person.get_random_motivation()
    timezone = pytz.timezone('Asia/Kolkata')  # Example: India timezone
    current_date = datetime.now(timezone).strftime("%d-%m-%Y")  # Ensure the format is correct
    
    st.markdown(f"### {current_date}")

    # Fetch user data (BMI, calories, and weight loss option)
    bmi, calories, weight_loss_option = Person.fetch_user_data(st.session_state.uid)

    # Initialize nutrition_graph_options in session_state if not already set
    if "nutrition_graph_options" not in st.session_state:
        total_nutrition_values = {
            'Calories': 0,
            'Protein': 0,
            'Carbs': 0,
            'Fat': 0,
            'Fiber': 0
        }
        st.session_state.nutrition_graph_options = {
            "tooltip": {"trigger": "item"},
            "legend": {"top": "center", "left": "right", "orient": "vertical"},
            "series": [
                {
                    "name": "Nutritional Values",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#fff",
                        "borderWidth": 2,
                    },
                    "label": {"show": False, "position": "center"},
                    "emphasis": {
                        "label": {"show": True, "fontSize": "30", "fontWeight": "bold"}
                    },
                    "labelLine": {"show": False},
                    "data": [
                        {"value": round(total_nutrition_values[key]), "name": key}
                        for key in total_nutrition_values
                    ],
                }
            ],
        }

    if 'recommendations' in st.session_state:
        meal_data = st.session_state.recommendations  # Access recommendations from session state
        print(f"Meal data to save: {meal_data}")
    else:
        print("No recommendations found in session state.")
  


    col1, col2 = st.columns([3, 2])  # 3 parts for text data, 2 parts for chart
    with col1:
        st.markdown(
            f"""
            ### Hey, **{username}** 👋  
            Welcome back!  
            *"{motivation}"*  
            Let's make today a healthy and productive day! 🚀
            """
        )
        st.subheader("Your Current Health Data")
        if bmi != 'N/A' and calories != 'N/A' and weight_loss_option != 'N/A':
            st.metric(label="BMI", value=f"{bmi}")
            if st.button("Know More"):
                st.switch_page('pages/7_graph.py')
            st.metric(label="Calories", value=f"{int(calories)} kcal")
            st.metric(label="Weight Option", value=weight_loss_option)
        else:
            st.warning("Health data not available. Please update your profile.")

    with col2:
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>', unsafe_allow_html=True)
        st_echarts(options=st.session_state.nutrition_graph_options, height="480px")

    # Create narrower columns for buttons
    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])  # Adjust the spacing column width
    with button_col1:
        if st.button("MealGpt 💬"):
            st.switch_page('pages/5_ChatBot.py')
    with button_col2:
        if st.button("Diet Plan 🥑"):
            st.switch_page('pages/3_Diet.py')
    with button_col3:
        # Ensure recommendations are available in session state
        if st.button("Food 🥗"):
            st.switch_page("pages/8_food.py")
    

# Run the dashboard
if __name__ == "__main__":
    dashboard()