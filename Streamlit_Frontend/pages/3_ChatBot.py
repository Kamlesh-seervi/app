import streamlit as st
import requests

st.set_page_config(page_title="Diet Planner Chatbot", page_icon="🤖", layout="wide")

class Chatbot:
    def __init__(self):
        # Initialize session state for conversation
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
        if 'generated' not in st.session_state:
            st.session_state.generated = False
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = ''

    def generate_response(self, message):
        # Add user message to conversation
        current_conversation = st.session_state.conversation.copy()
        current_conversation.append({
            'role': 'user', 
            'content': message
        })

        try:
            # Make API call
            response = requests.post('http://backend:8080/chat', json={
                'message': message,
                'conversation_history': current_conversation,
                'context': st.session_state.conversation_context
            })

            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Update conversation and context
                st.session_state.conversation = data['conversation_history']
                st.session_state.conversation_context = data['context']
                st.session_state.generated = True
                
                return data['conversation_history']
            
            else:
                # Handle error
                error_msg = f"**Error:** Unable to fetch response. Status code: {response.status_code}"
                st.session_state.conversation.append({
                    'role': 'assistant',
                    'content': error_msg
                })
                st.session_state.generated = True
                return st.session_state.conversation

        except requests.RequestException as e:
            # Handle network or request errors
            error_msg = f"**Network Error:** {str(e)}"
            st.session_state.conversation.append({
                'role': 'assistant',
                'content': error_msg
            })
            st.session_state.generated = True
            return st.session_state.conversation

class Display:
    def display_conversation(self, conversation):
        st.subheader('Chatbot Conversation')
        
        if conversation:
            for msg in conversation:
                if msg['role'] == 'user':
                    st.markdown(f"**User:** {msg['content']}")
                else:
                    st.markdown(f"**Assistant:** {msg['content']}")
        else:
            st.info('Start a conversation by typing a message', icon="💬")

# Page title
title = "<h1 style='text-align: center;'>Diet Planner Chatbot</h1>"
st.markdown(title, unsafe_allow_html=True)

# Initialize classes
chatbot = Chatbot()
display = Display()

# Conversation form
with st.form("chat_form"):
    st.header('Chat Options:')
    context_type = st.selectbox('Select Conversation Context', [
        'General Nutrition',
        'Diet Planning',
        'Weight Management',
        'Healthy Recipes',
        'Fitness Nutrition'
    ])
    max_tokens = st.slider('Response Length', 50, 500, 250, step=50)
    temperature = st.slider('Creativity Level', 0.0, 1.0, 0.7, step=0.1)
    
    # Chat input
    message = st.text_input('Your Message:', placeholder='Type your nutrition or diet-related question...')
    
    # Send button
    sent = st.form_submit_button("Send")

# Generate response when message is sent
if sent and message:
    with st.spinner('Generating response...'):
        conversation = chatbot.generate_response(message)

# Display conversation if generated
if st.session_state.generated:
    with st.container():
        display.display_conversation(st.session_state.conversation)