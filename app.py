import ollama
import streamlit as st
import streamlit.components.v1 as components
from streamlit_chat import message
import folium
from streamlit_folium import st_folium
from datetime import date, datetime
import pandas as pd
import requests
import json
import hashlib
import pickle

# Load city data
city_data = pd.read_csv('cities/worldcities.csv')

# Define multiple agents
AGENT_WEATHER = "weather"
AGENT_ITINERARY = "itinerary"
AGENT_OPTIMIZATION = "optimization"

# Store user preferences
USER_DATA_FILE = 'user_data.pkl'
try:
    with open(USER_DATA_FILE, 'rb') as f:
        user_data = pickle.load(f)
except FileNotFoundError:
    user_data = {}

# Helper functions for user authentication
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    if username in user_data and user_data[username]['password'] == hash_password(password):
        return True
    return False

def register_user(username, password):
    if username in user_data:
        return False
    user_data[username] = {
        'password': hash_password(password),
        'preferences': {}
    }
    save_user_data()
    return True

def save_user_data():
    with open(USER_DATA_FILE, 'wb') as f:
        pickle.dump(user_data, f)

# Weather fetching function
def get_weather(city_name, travel_date):
    # Placeholder for actual weather API integration
    return "Sunny with a high of 25°C"

def chat_with_model(model_name, agent, system_prompt, conversation_history, user_message):
    messages = conversation_history.copy()
    if system_prompt and len(conversation_history) == 0:
        messages.append({
            'role': 'system',
            'content': system_prompt,
        })
    messages.append({
        'role': 'user',
        'content': user_message,
    })

    # Pass agent type to handle different tasks
    response = ollama.chat(model=model_name, messages=messages)
    messages.append({
        'role': 'assistant',
        'content': response['message']['content'],
    })
    return response['message']['content'], messages

def get_city_coordinates(city_name):
    city = city_data[city_data['city'].str.lower() == city_name.lower()]
    if not city.empty:
        return [city.iloc[0]['lat'], city.iloc[0]['lng']]
    else:
        st.write("City not found in the dataset.")
        return None

def display_city_map(city_name, points_of_interest=[]):
    coordinates = get_city_coordinates(city_name)
    if not coordinates:
        st.write("No coordinates found to display on the map.")
        return

    # Initialize map centered around the city
    city_map = folium.Map(location=coordinates, zoom_start=12)
    folium.Marker(location=coordinates, popup=city_name).add_to(city_map)

    # Add points of interest
    for poi in points_of_interest:
        folium.Marker(location=[poi['lat'], poi['lng']], popup=poi['name']).add_to(city_map)

    st_folium(city_map, width=700, height=500)

def chatbot_ui():
    st.set_page_config(page_title="Tour Planning Chatbot", page_icon="🏙️", layout="wide")
    st.markdown("""
        <style>
        .main {
            background-color: #1e1e1e;
            padding: 0;
        }
        .stTextInput > div > div > input {
            background-color: #333333;
            color: #ffffff;
            border-radius: 20px;
            padding: 10px;
            border: 1px solid #555555;
        }
        .stButton button {
            border-radius: 20px;
            background-color: #008CBA;
            color: white;
            padding: 10px 20px;
            border: none;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #006f9a;
        }
        .stSidebar {
            background-color: #2e2e2e;
            color: #ffffff;
        }
        .banner {
            position: relative;
            width: 100%;
            height: 250px;
            background: url('banner.jpg') no-repeat center;
            background-size: cover;
            filter: brightness(0.4);
        }
        .banner-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #ffffff;
            font-size: 3em;
            font-weight: bold;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
        }
        .chat-container {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="banner"><div class="banner-text">Tour Planning Chatbot 🚶‍♀️☕</div></div>', unsafe_allow_html=True)

    # Authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.authenticated:
        st.sidebar.header("Sign In / Sign Up")
        action = st.sidebar.radio("Select Action:", ("Sign In", "Sign Up"))
        username = st.sidebar.text_input("Username:", key="username_input")
        password = st.sidebar.text_input("Password:", type="password", key="password_input")

        if action == "Sign Up":
            if st.sidebar.button("Register", key="register_button"):
                if username and password:
                    if register_user(username, password):
                        st.sidebar.success("User registered successfully. Please sign in.")
                    else:
                        st.sidebar.error("Username already exists. Please choose a different username.")
                else:
                    st.sidebar.error("Please enter a valid username and password.")

        if action == "Sign In":
            if st.sidebar.button("Login", key="login_button"):
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.sidebar.success("Logged in successfully.")
                    else:
                        st.sidebar.error("Invalid username or password.")
                else:
                    st.sidebar.error("Please enter your username and password.")
    else:
        st.sidebar.header(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Log Out", key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.conversation_history = []
            st.experimental_rerun()

        # Load user preferences if available
        preferences = user_data[st.session_state.username].get('preferences', {})
        budget = st.sidebar.number_input("Enter your budget ($):", min_value=0, step=10, value=preferences.get('budget', 0))
        city_name = st.sidebar.text_input("Enter the city name:", value=preferences.get('city_name', ''))
        starting_point = st.sidebar.text_input("Enter starting point (e.g., hotel name):", value=preferences.get('starting_point', ''))
        preferred_activity = st.sidebar.selectbox("Preferred Activity:", ["Sightseeing", "Adventure", "Relaxation", "Cultural", "Food Tour"], index=["Sightseeing", "Adventure", "Relaxation", "Cultural", "Food Tour"].index(preferences.get('preferred_activity', "Sightseeing")))
        include_weather = st.sidebar.checkbox("Include Weather Forecast?", value=preferences.get('include_weather', False))
        travel_dates = st.sidebar.date_input("Select Estimated Range of Travel Dates:", min_value=date.today(), value=preferences.get('travel_dates', (date.today(), date.today())))

        # Save user preferences
        user_data[st.session_state.username]['preferences'] = {
            'budget': budget,
            'city_name': city_name,
            'starting_point': starting_point,
            'preferred_activity': preferred_activity,
            'include_weather': include_weather,
            'travel_dates': travel_dates
        }
        save_user_data()

        if include_weather and city_name:
            weather_info = get_weather(city_name, travel_dates[0])
            st.sidebar.write(f"Weather Forecast: {weather_info}")

        system_prompt = (
            "You are a tour planning assistant. You help users plan a trip based on their preferences.\n\n"
            "When planning the itinerary, consider the following preferences:\n\n"
            f"- **Budget**: ${budget}\n"
            f"- **Preferred Activity**: {preferred_activity}\n"
            f"- **Include Weather Forecast**: {'Yes' if include_weather else 'No'}\n"
            f"- **Location**: {city_name}\n"
            f"- **Starting Point**: {starting_point or 'First attraction'}\n"
            f"- **Estimated Range of Travel Dates**: {travel_dates[0]} to {travel_dates[1]}\n\n"
            "Provide a detailed itinerary for the user based on their preferences, including suggested locations and activities."
        )

        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        with st.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for i in range(len(st.session_state.conversation_history)):
                role = st.session_state.conversation_history[i]['role']
                content = st.session_state.conversation_history[i]['content']
                if role == 'user':
                    message(content, is_user=True, key=f"user_{i}")
                else:
                    message(content, key=f"bot_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

        user_message = st.text_input("", placeholder="Type your message here...", key="user_input")

        if st.button("Send", use_container_width=True) and user_message:
            response, updated_conversation_history = chat_with_model(
                model_name="llama3.1",
                agent=AGENT_ITINERARY,
                system_prompt=system_prompt,
                conversation_history=st.session_state.conversation_history,
                user_message=user_message,
            )
            st.session_state.conversation_history.append({"role": "user", "content": user_message})
            st.session_state.conversation_history.append({"role": "assistant", "content": response})
            st.experimental_rerun()

        if city_name:
            st.subheader("Map of the City")
            display_city_map(city_name)

if __name__ == "__main__":
    chatbot_ui()
