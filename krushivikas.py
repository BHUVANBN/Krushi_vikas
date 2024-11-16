import google.generativeai as genai
import dotenv
import os
import streamlit as st
import mysql.connector
import pandas as pd
import folium
from streamlit_folium import folium_static
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from twilio.rest import Client
import matplotlib.pyplot as plt
import requests

styles = """
    <style>
        /* Main content background */
        [data-testid="stAppViewContainer"] {
            margin: 0;
            height: 100vh;
            background: linear-gradient(-45deg ,#2f6c7c,#6A9F84,#A1B295,#A58F86,#738F7E);
            background-size: 400% 400%;
            animation: bg 12s ease infinite;
        }

        @keyframes bg {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 100%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
       
        /* Transparent sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.75); /* 50% transparency */
            color: white; /* Ensure text remains visible */
        }

        /* Optional: Style sidebar headings */
        [data-testid="stSidebar"] h2 {
            color: white;
        }

        /* Adjust font color for better readability */
        [data-testid="stSidebar"] .css-1d391kg {
            color: white;
        }
        
        
        /* General app styling */
        .stMarkdown {
            color: white;
        }
    </style>
"""

st.markdown(styles, unsafe_allow_html=True)


# st.markdown('<div class="glass">', unsafe_allow_html=True)


# st.title("Farmer Crop Predictor") 
# st.markdown("</div>", unsafe_allow_html=True)

dotenv.load_dotenv()
API_KEY = os.environ.get("API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

# Configure API key for Google Generative AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Database connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="batman2003",
    database="farmer_Assistant"
)

cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        phone VARCHAR(20),
        plot_size FLOAT,
        location VARCHAR(100),
        crop VARCHAR(50)
    )
""")

# Helper functions
def save_farmer_details(name, phone, plot_size, location, crop):
    query = """
    INSERT INTO farmers (name, phone, plot_size, location, crop)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, phone, plot_size, location, crop))
    connection.commit()

def get_crop_price(crop_name,location):
    file_path = 'CropPriceDatasets.xlsx'
    excel_data = pd.ExcelFile(file_path)
    if crop_name not in excel_data.sheet_names:
        raise ValueError(f"Crop '{crop_name}' not found in the Excel file.")

    # Load the data for the specified crop
    crop_data = pd.read_excel(file_path, sheet_name=crop_name)

    # Ensure the column for price contains numeric values
    try:
        last_price = float(crop_data.iloc[-1, 1])  # Second column (price)
    except ValueError:
        raise ValueError(f"Price data for crop '{crop_name}' is not numeric or is invalid.")

    return last_price

# def get_crop_price_graph(crop_name):
#     file_path = 'CropPriceDatasets.xlsx'
#     crop_data = pd.read_excel(file_path, sheet_name=crop_name)
#     plt.figure(figsize=(10, 5))
#     plt.plot(crop_data['month'], crop_data['value'], marker='o')
#     plt.title(f"Price Trend for {crop_name}")
#     plt.xlabel("Date")
#     plt.ylabel("Price")
#     plt.grid()
#     st.pyplot(plt)

def get_crop_price_graph(crop_name):
    file_path = 'CropPriceDatasets.xlsx'
    crop_data = pd.read_excel(file_path, sheet_name=crop_name)
    crop_data = crop_data[['month', 'value']].rename(columns={'month': 'Date', 'value': 'Price'})
    crop_data.set_index('Date', inplace=True) 
    # st.area_chart(crop_data)
    # st.bar_chart(crop_data)
    st.line_chart(crop_data)


def get_government_schemes(location, crop_name, plot_size):
    schemes_prompt = f"List recent government schemes for {crop_name} in {location} for a plot size of {plot_size} acres.just list the schemes in point wise"
    response = model.generate_content(schemes_prompt)
    return response.text

def send_sms(phone_number, message):
    TWILIO_SID = "AC6e6c7eb3d710924d33c67403cd86e45d"
    TWILIO_AUTH_TOKEN = "6bd1437a18a31d11fe60f77cf3e5935d"
    TWILIO_PHONE_NUMBER = "+19785635181"
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

def get_weather_forecast(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("main"):
        return f"Weather in {location}: {response['weather'][0]['description']}, Temp: {response['main']['temp']}°C"
    return "Weather information not available."

# Page structure
#st.set_page_config(page_title="Farmer Assistant", layout="centered")
st.sidebar.image("Logo.png", use_container_width=True)
st.sidebar.write("Bringing technology to the heart of agriculture.")
page = st.sidebar.radio("Go to", ["Login", "Crop Prediction", "Chatbot", "Map", "Data Visualization", "Weather Forecasting"])

# Login Page
if page == "Login":
    st.title("Farmer Assistant - Login")
    name = st.text_input("Name")
    st.session_state.name = name
    phone = st.text_input("Phone Number")
    st.session_state.phone = phone
    if st.button("Submit"):
        st.sidebar.success(f"Welcome, {name}!")

# Crop Prediction Page
elif page == "Crop Prediction":
    st.title("Crop Prediction")
    plot_size = st.text_input("Plot Size (acres)")
    location = st.text_input("Location")
    st.session_state.location = location
    if st.button("Predict Crop"):
        prompt = f"Suggest suitable crops for a plot of {plot_size} acres in {location}. Separate with spaces.donot use comma for seperation"
        response = model.generate_content(prompt)
        crops = response.text.split()
        selected_crop = st.selectbox("Select a Crop", crops)
        st.session_state.selected_crop = selected_crop
        if selected_crop:
            crop_price = get_crop_price(selected_crop, location)
            schemes = get_government_schemes(location, selected_crop, plot_size)
            st.write(f"Latest Price for {selected_crop}: {crop_price}/quintal")
            st.write(f"Government Schemes: {schemes}")
            name = st.session_state.name 
            phone = st.session_state.phone
            save_farmer_details(name, phone, plot_size, location, selected_crop)
            send_sms(phone, f"Crop: {selected_crop}, Price: {crop_price}, Schemes: {schemes}")

# Chatbot Page
elif page == "Chatbot":
    st.title("AI Chatbot")
    user_query = st.text_input("Ask the Assistant")
    if st.button("Send"):
        response = model.generate_content(user_query)
        st.write(response.text)

# Map Page
# elif page == "Map":
#     loc_prompt = f"get the longitude and lattitude of the location {location} "
#     response = model.generate_content(loc_prompt)
#     loc = response.text
#     st.title("Map Section")
#     lat = st.number_input("Enter Latitude", value=28.6139)
#     lon = st.number_input("Enter Longitude", value=77.2090)
#     if st.button("Show Map"):
#         st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

elif page == "Map":
    st.title("Map Section")
    location = st.session_state.location
    # Use the 'location' entered on the Home Page
    if location:
        st.write(f"Fetching coordinates for: {location}")
        
        # Using OpenCage Geocoder or a similar API
        geocode_api_key = "69df31c2d3794ec896fbc711a9a19a11"  # Replace with your API key
        geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={geocode_api_key}"
        response = requests.get(geocode_url)
        
        if response.status_code == 200:
            geocode_data = response.json()
            if geocode_data['results']:
                lat = geocode_data['results'][0]['geometry']['lat']
                lon = geocode_data['results'][0]['geometry']['lng']
                st.success(f"Coordinates Found for {location}:")
                st.write(f"Latitude: {lat}, Longitude: {lon}")
                # Display the map
                st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
            else:
                st.error("No results found for the entered location.")
        else:
            st.error("Error fetching data from the API.")
    else:
        st.error("Location not found. Please enter a location on the Home Page.")


# Data Visualization Page
elif page == "Data Visualization":
    st.title("Crop Price Trends")
    crop_name = st.session_state.selected_crop
    if st.button("Show Graph"):
        get_crop_price_graph(crop_name)

# Weather Forecasting Page
elif page == "Weather Forecasting":
    st.title("Weather Forecasting")
    location = st.session_state.location
    prompt = f"give me the current weather in  {location}, just list the detailed weather information "
    response = model.generate_content(prompt)
    weather = response.text
    st.write(f"Suggested Crop: {weather}")