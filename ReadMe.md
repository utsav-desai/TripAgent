# Tour Planning Chatbot

![Tour Planning Chatbot](banner.jpg)

A tour planning chatbot built with Streamlit and Ollama, designed to provide users with customized travel itineraries, weather forecasts, city maps, and optimized routes based on user preferences. This chatbot is built with a focus on ease of use and personalization, featuring user authentication, saved preferences, and interactive map visualization.

## Features

- **User Authentication**: Allows users to register, log in, and save their travel preferences securely.
- **Weather Forecasts**: Fetches the weather information for the selected city and date range.
- **Customizable Itinerary Planning**: Generates a personalized travel itinerary based on user-defined budget, travel dates, city of interest, activity preferences, and starting location.
- **City Map with Points of Interest**: Displays an interactive map of the selected city with notable locations marked.
- **Interactive Chat Interface**: Engages users in a natural conversation, providing responses based on specific travel-related queries.

## Tech Stack

- **Python**: Backend language
- **Streamlit**: UI framework for an interactive web application
- **Ollama**: Model interaction for natural language responses
- **Folium**: Map visualization
- **Pandas**: Data handling and city data processing
- **SHA-256**: Password hashing for secure user authentication
- **Pickle**: Storage of user data locally for quick access and preference retention
- 

## Installation

1. [ ] **Clone the repository**:

    ```bash
    git clone https://github.com/utsav-desai/TripAgent
    cd TripAgent
    ```
2. [ ] **Ollama setup**:

    ```bash
    pip install ollama
    ollama pull llama3.1
    ```
3. [ ] **Run the app**:

    ```bash
    streamlit run app.py
    ```

## References

- **Cities database:** [https://simplemaps.com/data/world-cities]()
- **Streamlit**:[https://streamlit.io](https://streamlit.io)
- **Ollama**:[https://ollama.com](https://ollama.com)
- **Folium**:[https://python-visualization.github.io/folium/]()
- **SHA-256**: [https://en.wikipedia.org/wiki/SHA-2](https://en.wikipedia.org/wiki/SHA-2)
