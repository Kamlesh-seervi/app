import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate("./diet-8571f-firebase-adminsdk-d43ko-de38d05eff.json")  # Replace with your Firebase service account key
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Title for the page
st.title("BMI Classification Chart")

# Placeholder for user authentication
def get_current_user_id():
    """
    Fetch the current user's ID.
    This should integrate Firebase Authentication to verify the user session/token.
    Replace the placeholder logic with actual Firebase Authentication logic.
    """
    if 'uid' in st.session_state:
        # UID is already stored in session state
        return st.session_state['uid']
    
    # Placeholder logic for demonstration purposes
    # In a real application, retrieve the UID using Firebase Authentication
    try:
        # Example: Retrieve and verify the user from a session token
        # Replace this with actual logic to fetch the user ID
        session_token = st.session_state.get('session_token')  # Assume session_token is stored
        if session_token:
            decoded_token = auth.verify_id_token(session_token)
            user_id = decoded_token.get('uid')
            st.session_state['uid'] = user_id  # Store in session state
            return user_id
        else:
            st.warning("User is not authenticated. Please log in.")
            return None
    except Exception as e:
        st.error(f"Error retrieving user ID: {e}")
        return None

# Fetch current user ID
user_id = get_current_user_id()

# BMI Classification Data
bmi_data = {
    "Classification": [
        "Severe Thinness", 
        "Moderate Thinness", 
        "Mild Thinness", 
        "Normal", 
        "Overweight", 
        "Obese Class I", 
        "Obese Class II", 
        "Obese Class III"
    ],
    "BMI Range (kg/m²)": [
        "< 16", 
        "16 - 17", 
        "17 - 18.5", 
        "18.5 - 25", 
        "25 - 30", 
        "30 - 35", 
        "35 - 40", 
        "> 40"
    ],
}

# Convert to DataFrame
bmi_df = pd.DataFrame(bmi_data)

# Display the table
st.markdown("### BMI Classification Table")
st.table(bmi_df)

# Fetch current user BMI from Firebase
user_bmi = None
try:
    user_doc = db.collection("user_calories").document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        user_bmi = user_data.get("bmi", None)
except Exception as e:
    st.error(f"Error fetching user BMI: {e}")

# Display user BMI and classification
if user_bmi is not None:
    st.markdown("### Your BMI Classification")
    st.metric("Your BMI", f"{user_bmi:.2f}")
    
    # Determine BMI classification
    if user_bmi < 16:
        classification = "Severe Thinness"
        feedback = "Your BMI is very low. Consider consulting a healthcare provider."
    elif 16 <= user_bmi < 17:
        classification = "Moderate Thinness"
        feedback = "Your BMI indicates thinness. Focus on a balanced diet to improve your health."
    elif 17 <= user_bmi < 18.5:
        classification = "Mild Thinness"
        feedback = "Your BMI is slightly below normal. Try to maintain a healthy weight."
    elif 18.5 <= user_bmi < 25:
        classification = "Normal"
        feedback = "Your BMI is in the normal range. Keep up the good work!"
    elif 25 <= user_bmi < 30:
        classification = "Overweight"
        feedback = "Your BMI indicates overweight. Consider a healthy diet and regular exercise."
    elif 30 <= user_bmi < 35:
        classification = "Obese Class I"
        feedback = "Your BMI indicates obesity. A healthier lifestyle is recommended."
    elif 35 <= user_bmi < 40:
        classification = "Obese Class II"
        feedback = "Your BMI is in the obesity range. Seek advice from a healthcare provider."
    else:
        classification = "Obese Class III"
        feedback = "Your BMI is very high. Immediate action is needed to improve your health."

    st.write(f"Classification: **{classification}**")
    st.write(feedback)
else:
    st.warning("Your BMI is not available. Please ensure it is updated in your profile.")

# BMI Classifications Bar Chart
st.markdown("### BMI Classifications Bar Chart")
bar_chart_data = pd.DataFrame({
        "Classification": [
            "Severe Thinness", 
            "Moderate Thinness", 
            "Mild Thinness", 
            "Normal", 
            "Overweight", 
            "Obese Class I", 
            "Obese Class II", 
            "Obese Class III"
        ],
        "Risk Level (1 = Lowest, 8 = Highest)": [1, 2, 3, 4, 5, 6, 7, 8]  # Assign risk levels for visualization
    })
st.bar_chart(bar_chart_data.set_index("Classification"))

# Footer
st.markdown("***")
st.write("This table and chart illustrate the BMI classification ranges and their categories.")
if st.button("DashBoard"):
            st.switch_page('pages/4_Dashboard.py')