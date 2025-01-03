import streamlit as st
import pandas as pd
from Generate_Recommendations import Generator
from random import uniform as rnd
from ImageFinder.ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts
from firebase_admin import credentials, firestore
import firebase_admin 
from datetime import datetime
import pytz

st.set_page_config(page_title="Automatic Diet Recommendation", page_icon="💪",layout="wide",initial_sidebar_state="collapsed")
if not firebase_admin._apps:
    cred = credentials.Certificate("./diet-8571f-firebase-adminsdk-d43ko-de38d05eff.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()


nutritions_values=['Calories','CholesterolContent','CarbohydrateContent','FiberContent','ProteinContent']
# Streamlit states initialization
if 'person' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations=None
    st.session_state.person=None
    st.session_state.weight_loss_option=None
class Person:

    def __init__(self,age,height,weight,gender,activity,meals_calories_perc,weight_loss):
        self.age=age
        self.height=height
        self.weight=weight
        self.gender=gender
        self.activity=activity
        self.meals_calories_perc=meals_calories_perc
        self.weight_loss=weight_loss

    def calculate_bmi(self,):
        bmi=round(self.weight/((self.height/100)**2),2)
        return bmi

    def display_result(self,):
        bmi=self.calculate_bmi()
        bmi_string=f'{bmi} kg/m²'
        if bmi<18.5:
            category='Underweight'
            color='Red'
        elif 18.5<=bmi<25:
            category='Normal'
            color='Green'
        elif 25<=bmi<30:
            category='Overweight'
            color='Yellow'
        else:
            category='Obesity'    
            color='Red'
        return bmi_string,category,color

    def calculate_bmr(self):
        if self.gender=='Male':
            bmr=10*self.weight+6.25*self.height-5*self.age+5
        else:
            bmr=10*self.weight+6.25*self.height-5*self.age-161
        return bmr

    def calories_calculator(self):
        activites=['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights=[1.2,1.375,1.55,1.725,1.9]
        weight = weights[activites.index(self.activity)]
        maintain_calories = self.calculate_bmr()*weight
        return maintain_calories

    def generate_recommendations(self,):
        total_calories=self.weight_loss*self.calories_calculator()
        recommendations=[]
        for meal in self.meals_calories_perc:
            meal_calories=self.meals_calories_perc[meal]*total_calories
            if meal=='breakfast':        
                recommended_nutrition = [meal_calories,rnd(10,30),rnd(0,4),rnd(0,30),rnd(0,400),rnd(40,75),rnd(4,10),rnd(0,10),rnd(30,100)]
            elif meal=='lunch':
                recommended_nutrition = [meal_calories,rnd(20,40),rnd(0,4),rnd(0,30),rnd(0,400),rnd(40,75),rnd(4,20),rnd(0,10),rnd(50,175)]
            elif meal=='dinner':
                recommended_nutrition = [meal_calories,rnd(20,40),rnd(0,4),rnd(0,30),rnd(0,400),rnd(40,75),rnd(4,20),rnd(0,10),rnd(50,175)] 
            else:
                recommended_nutrition = [meal_calories,rnd(10,30),rnd(0,4),rnd(0,30),rnd(0,400),rnd(40,75),rnd(4,10),rnd(0,10),rnd(30,100)]
            generator=Generator(recommended_nutrition)
            recommended_recipes=generator.generate().json()['output']
            recommendations.append(recommended_recipes)
        for recommendation in recommendations:
            for recipe in recommendation:
                recipe['image_link']=find_image(recipe['Name']) 
        return recommendations
    
    

class Display:
    def __init__(self):
        self.plans=["Maintain weight","Mild weight loss","Weight loss","Extreme weight loss"]
        self.weights=[1,0.9,0.8,0.6]
        self.losses=['-0 kg/week','-0.25 kg/week','-0.5 kg/week','-1 kg/week']
        pass

    def display_bmi(self,person):
        st.header('BMI CALCULATOR')
        bmi_string,category,color = person.display_result()
        st.metric(label="Body Mass Index (BMI)", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 25px;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.markdown(
            """
            Healthy BMI range: 18.5 kg/m² - 25 kg/m².
            """)   

    def display_calories(self,person):
        st.header('CALORIES CALCULATOR')        
        maintain_calories=person.calories_calculator()
        st.write('The results show a number of daily calorie estimates that can be used as a guideline for how many calories to consume each day to maintain, lose, or gain weight at a chosen rate.')
        for plan,weight,loss,col in zip(self.plans,self.weights,self.losses,st.columns(4)):
            with col:
                st.metric(label=plan,value=f'{round(maintain_calories*weight)} Calories/day',delta=loss,delta_color="inverse")

    def display_recommendation(self, person, recommendations):
    # Initialize an empty dictionary for meal_data
        meal_data = {
            'Breakfast': [],
            'Lunch': [],
            'Dinner': [],
            'Snacks': [],
        }

        st.header('DIET RECOMMENDATOR')  
        with st.spinner('Generating recommendations...'): 
            meals = person.meals_calories_perc
            st.subheader('Recommended recipes:')
            for meal_name, column, recommendation in zip(meals, st.columns(len(meals)), recommendations):
                meal_name = meal_name.capitalize()
                with column:
                    st.markdown(f'##### {meal_name.upper()}')    
                    for recipe in recommendation:
                    # Add recipe to the meal_data dictionary
                        meal_data[meal_name].append({
                            'Name': recipe['Name'],
                            'CookTime': recipe['CookTime'],
                            'PrepTime': recipe['PrepTime'],
                            'TotalTime': recipe['TotalTime'],
                            'RecipeIngredientParts': recipe['RecipeIngredientParts'],
                            'Calories': recipe['Calories'],
                            'FatContent': recipe['FatContent'],
                            'SaturatedFatContent': recipe['SaturatedFatContent'],
                            'CholesterolContent': recipe['CholesterolContent'],
                            'SodiumContent': recipe['SodiumContent'],
                            'CarbohydrateContent': recipe['CarbohydrateContent'],
                            'FiberContent': recipe['FiberContent'],
                            'SugarContent': recipe['SugarContent'],
                            'ProteinContent': recipe['ProteinContent'],
                            'RecipeInstructions': recipe['RecipeInstructions'],
                            'image_link': recipe['image_link'],
                        })

                        if isinstance(recipe['RecipeInstructions'], str):
                            recipe['RecipeInstructions'] = [recipe['RecipeInstructions']]

                    # Existing code for displaying the recipe details
                        expander = st.expander(recipe['Name'])
                        recipe_link = recipe['image_link']
                        recipe_img = f'<div><center><img src={recipe_link} alt={recipe["Name"]}></center></div>'     
                        nutritions_df = pd.DataFrame({value: [recipe[value]] for value in nutritions_values})      
                    
                        expander.markdown(recipe_img, unsafe_allow_html=True)  
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>', unsafe_allow_html=True)                   
                        expander.dataframe(nutritions_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>', unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            expander.markdown(f"- {ingredient}")
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>', unsafe_allow_html=True)    
                        for instruction in recipe['RecipeInstructions']:
                            expander.markdown(f"- {instruction}") 
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Cooking and Preparation Time:</h5>', unsafe_allow_html=True)   
                        expander.markdown(f"""
                            - Cook Time       : {recipe['CookTime']}min
                            - Preparation Time: {recipe['PrepTime']}min
                            - Total Time      : {recipe['TotalTime']}min
                        """)


        st.session_state.meal_data = meal_data
        


    def display_meal_choices(self, person, recommendations):
        st.subheader('Choose your meal composition:')
        choices = []

    # Choose meals based on the recommendations
        if len(recommendations) == 3:
            breakfast_column, lunch_column, dinner_column = st.columns(3)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'Choose your breakfast:', [recipe['Name'] for recipe in recommendations[0]])
            with lunch_column:
                lunch_choice = st.selectbox(f'Choose your lunch:', [recipe['Name'] for recipe in recommendations[1]])
            with dinner_column:
                dinner_choice = st.selectbox(f'Choose your dinner:', [recipe['Name'] for recipe in recommendations[2]])
            choices = [breakfast_choice, lunch_choice, dinner_choice]

    # Additional logic for more meals (if applicable)
        elif len(recommendations) == 4:
            breakfast_column, morning_snack_column, lunch_column, dinner_column = st.columns(4)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'Choose your breakfast:', [recipe['Name'] for recipe in recommendations[0]])
            with morning_snack_column:
                morning_snack_choice = st.selectbox(f'Choose your morning snack:', [recipe['Name'] for recipe in recommendations[1]])
            with lunch_column:
                lunch_choice = st.selectbox(f'Choose your lunch:', [recipe['Name'] for recipe in recommendations[2]])
            with dinner_column:
                dinner_choice = st.selectbox(f'Choose your dinner:', [recipe['Name'] for recipe in recommendations[3]])
            choices = [breakfast_choice, morning_snack_choice, lunch_choice, dinner_choice]
    
        else:
            breakfast_column, morning_snack_column, lunch_column, afternoon_snack_column, dinner_column = st.columns(5)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'Choose your breakfast:', [recipe['Name'] for recipe in recommendations[0]])
            with morning_snack_column:
                morning_snack_choice = st.selectbox(f'Choose your morning snack:', [recipe['Name'] for recipe in recommendations[1]])
            with lunch_column:
                lunch_choice = st.selectbox(f'Choose your lunch:', [recipe['Name'] for recipe in recommendations[2]])
            with afternoon_snack_column:
                afternoon_snack_choice = st.selectbox(f'Choose your afternoon snack:', [recipe['Name'] for recipe in recommendations[3]])
            with dinner_column:
                dinner_choice = st.selectbox(f'Choose your dinner:', [recipe['Name'] for recipe in recommendations[4]])
            choices = [breakfast_choice, morning_snack_choice, lunch_choice, afternoon_snack_choice, dinner_choice]

    # Calculating the sum of nutritional values for the chosen recipes
        total_nutrition_values = {nutrition_value: 0 for nutrition_value in nutritions_values}
        for choice, meals_ in zip(choices, recommendations):
            for meal in meals_:
                if meal['Name'] == choice:
                    for nutrition_value in nutritions_values:
                        total_nutrition_values[nutrition_value] += meal[nutrition_value]
    
        total_calories_chose = total_nutrition_values['Calories']
        loss_calories_chose=round(person.calories_calculator()*person.weight_loss)
        st.session_state.nutrition_values = total_nutrition_values

    # Save the selected meals into the meal data structure
        meal_data = {
            'Breakfast': [],
            'Lunch': [],
            'Dinner': [],
        }

    # Assuming your meal names map directly to the meal categories (you can adjust if needed)
        if 'Breakfast' in meal_data:
            meal_data['Breakfast'].append(next(meal for meal in recommendations[0] if meal['Name'] == breakfast_choice))
        if 'Lunch' in meal_data:
            meal_data['Lunch'].append(next(meal for meal in recommendations[1] if meal['Name'] == lunch_choice))
        if 'Dinner' in meal_data:
            meal_data['Dinner'].append(next(meal for meal in recommendations[2] if meal['Name'] == dinner_choice))
    
    # Call your save function here
        st.session_state.selected_meals = choices
        st.session_state.nutrition_values = total_nutrition_values
        # Display corresponding graphs
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Total Calories in Recipes vs {st.session_state.weight_loss_option} Calories:</h5>', unsafe_allow_html=True)
        total_calories_graph_options = {
    "xAxis": {
        "type": "category",
        "data": ['Total Calories you chose', f"{st.session_state.weight_loss_option} Calories"],
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "data": [
                {"value":total_calories_chose, "itemStyle": {"color":["#33FF8D","#FF3333"][total_calories_chose>loss_calories_chose]}},
                {"value": loss_calories_chose, "itemStyle": {"color": "#3339FF"}},
            ],
            "type": "bar",
        }
    ],
}
        st_echarts(options=total_calories_graph_options,height="400px",)
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>', unsafe_allow_html=True)
        nutritions_graph_options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
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
                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": [{"value":round(total_nutrition_values[total_nutrition_value]),"name":total_nutrition_value} for total_nutrition_value in total_nutrition_values],
        }
    ],
}       
        st_echarts(options=nutritions_graph_options, height="500px",)
        st.session_state.nutrition_graph_options = nutritions_graph_options

        if st.button("Dashboard🥗"):
            st.switch_page('pages/4_Dashboard.py')

display = Display()
title = "<h1 style='text-align: center;'>Automatic Diet Recommendation</h1>"
st.markdown(title, unsafe_allow_html=True)
# Save BMI and calories to Firestore for the selected weight loss option

def save_to_firestore(user_profile, bmi, calories, weight_loss_option):
    user_calories_ref = db.collection('user_calories').document(user_profile['uid'])

    # Data to be saved
    user_calories_data = {
        'name': user_profile['name'],
        'bmi': bmi,
        'calories': calories,
        'weight_loss_option': weight_loss_option,
        'timestamp': firestore.SERVER_TIMESTAMP  # Optional: Add a timestamp
    }

    # Save data to Firestore
    user_calories_ref.set(user_calories_data)
    print("BMI and calories saved to Firestore.")


def save_selected_meal(uid, meal_data):
        try:
            timezone = pytz.timezone('Asia/Kolkata')  # Example: India timezone
            current_date = datetime.now(timezone).strftime('%d-%m-%Y')  # Fo
       
            for meal_name, meal_recipes in meal_data.items():
                for recipe in meal_recipes:
                    
                    meal_id = recipe['Name']  # or any unique identifier for the recipe
                    meal_ref = db.collection('user_recom_food').document(uid).collection(current_date).document('recommendations').collection(meal_name).document(meal_id)
                # Saving the recipe data to Firestore
                    meal_ref.set({
                        'Name': recipe['Name'],
                        'CookTime': recipe['CookTime'],
                        'PrepTime': recipe['PrepTime'],
                        'TotalTime': recipe['TotalTime'],
                        'RecipeIngredientParts': recipe['RecipeIngredientParts'],
                        'Calories': recipe['Calories'],
                        'FatContent': recipe['FatContent'],
                        'SaturatedFatContent': recipe['SaturatedFatContent'],
                        'CholesterolContent': recipe['CholesterolContent'],
                        'SodiumContent': recipe['SodiumContent'],
                        'CarbohydrateContent': recipe['CarbohydrateContent'],
                        'FiberContent': recipe['FiberContent'],
                        'SugarContent': recipe['SugarContent'],
                        'ProteinContent': recipe['ProteinContent'],
                        'RecipeInstructions': recipe['RecipeInstructions'],
                        'image_link': recipe['image_link']
                    })
                    
        except Exception as e:
            st.write(f"Error saving meal data: {e}")# Fetch user profile from Firestore
def get_user_profile(uid):
    user_profile_ref = db.collection('user_profile').document(uid)
    doc = user_profile_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        st.warning("User profile not found.")
        return None

# Ensure the user is logged in
if 'uid' not in st.session_state:
    st.warning("You must be logged in to access this page.")
else:
    uid = st.session_state['uid']  # UID of the logged-in user
    user_profile = get_user_profile(uid)

    # Default values if no profile data exists
    default_age = 25
    default_height = 170
    default_weight = 70
    default_gender = 'Male'

    # Extract user profile data or fallback to defaults
    if user_profile:
        age_value = user_profile.get('age', default_age)
        height_value = user_profile.get('height', default_height)
        weight_value = user_profile.get('weight', default_weight)
        gender_value = user_profile.get('gender', default_gender)
    else:
        age_value, height_value, weight_value, gender_value = default_age, default_height, default_weight, default_gender

    with st.form("recommendation_form"):
        st.write("Modify the values and click the Generate button to use")
        age = st.number_input('Age', min_value=2, max_value=120, step=1, value=age_value)
        height = st.number_input('Height(cm)', min_value=50, max_value=300, step=1, value=height_value)
        weight = st.number_input('Weight(kg)', min_value=10, max_value=300, step=1, value=weight_value)
        gender = st.radio('Gender', ('Male', 'Female'), index=0 if gender_value == 'Male' else 1)
        activity = st.select_slider('Activity', options=[
            'Little/no exercise', 
            'Light exercise', 
            'Moderate exercise (3-5 days/wk)', 
            'Very active (6-7 days/wk)', 
            'Extra active (very active & physical job)'
        ])
        option = st.selectbox('Choose your weight loss plan:', display.plans)
        st.session_state.weight_loss_option = option
        weight_loss = display.weights[display.plans.index(option)]
        number_of_meals = st.slider('Meals per day', min_value=3, max_value=5, step=1, value=3)
        if number_of_meals == 3:
            meals_calories_perc = {'breakfast': 0.35, 'lunch': 0.40, 'dinner': 0.25}
        elif number_of_meals == 4:
            meals_calories_perc = {'breakfast': 0.30, 'morning snack': 0.05, 'lunch': 0.40, 'dinner': 0.25}
        else:
            meals_calories_perc = {'breakfast': 0.30, 'morning snack': 0.05, 'lunch': 0.40, 'afternoon snack': 0.05, 'dinner': 0.20}
        generated = st.form_submit_button("Generate")
    if generated:
        st.session_state.generated = True
        person = Person(age, height, weight, gender, activity, meals_calories_perc, weight_loss)
        with st.container():
            display.display_bmi(person)
        with st.container():
            display.display_calories(person)
        with st.spinner('Generating recommendations...'):
            recommendations = person.generate_recommendations()
            st.session_state.recommendations = recommendations
            st.session_state.person = person

if st.session_state.generated:
    with st.container():
        display.display_recommendation(st.session_state.person, st.session_state.recommendations)
        st.success('Recommendation Generated Successfully !', icon="✅")
    with st.container():
        display.display_meal_choices(st.session_state.person, st.session_state.recommendations)

if generated:
    st.session_state.generated = True
    person = Person(age, height, weight, gender, activity, meals_calories_perc, weight_loss)
    
    # Calculate BMI
    bmi = person.calculate_bmi()
    
    # Calculate total calories adjusted for the selected weight loss option
    total_calories = person.calories_calculator() * display.weights[display.plans.index(st.session_state.weight_loss_option)]
    save_selected_meal(uid, st.session_state.meal_data)
    # Save the data to Firestore
    save_to_firestore(user_profile, bmi, total_calories, st.session_state.weight_loss_option)
    st.success('Recommendation Generated Successfully!', icon="✅")

    # Switch to the dashboard page
    st.switch_page("pages/4_Dashboard.py")