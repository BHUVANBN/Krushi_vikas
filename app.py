import google.generativeai as genai
import dotenv
import os
import streamlit as st
import mysql.connector
# from googletrans import Translator

# translator = Translator()
# indian_languages = {
#     'Hindi': 'hi',
#     'Tamil': 'ta',
#     'Telugu': 'te',
#     'Bengali': 'bn',
#     'Kannada': 'kn',
#     'Malayalam': 'ml',
#     'Gujarati': 'gu',
#     'Punjabi': 'pa',
#     'Marathi': 'mr',
#     'Odia': 'or'
# }

dotenv.load_dotenv() 
API_KEY = os.environ.get("API_KEY")

# Configure API key for Google Generative AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Streamlit app UI setup
st.set_page_config(page_title="Farmer Assistant")
st.title("Farmer Assistant - Crop Prediction")

# Input fields for Farmer's details
name = st.text_input("Farmer's Name")  
phone = st.text_input("Phone Number")
plot_size = st.text_input("Plot Size")
location = st.text_input("Location")

# Connect to the MySQL database
connection = mysql.connector.connect(
    host="localhost",       # Replace with your MySQL host (usually "localhost")
    user="root",   # Replace with your MySQL username
    password="batman2003", # Replace with your MySQL password
    database="farmer_Assistant"   # Replace with your database name
)

# Check if the connection is successful
if connection.is_connected():
    print("Connected to MySQL database")

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
print("Table created successfully.")

def save_farmer_details(name, phone, plot_size, location, crop):
    query = """
    INSERT INTO farmers (name, phone, plot_size, location, crop)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, phone, plot_size, location, crop))
    connection.commit()
    print("Farmer added successfully.")

# Function to get the latest crop price
#def get_crop_price(crop_name,location):
    # price_prompt = f"predict the currect price of {crop_name} in {location}. give me price per kg with this format: The price of the crop is XXXXX rupees/kg."
    # response = model.generate_content(price_prompt)
    # price = response.text
    #st.write(price)

    # return price

    # import requests
    # url = f"https://api.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi?format=json&crop={crop_name}"
    # response = requests.get(url)
    # if response.status_code == 200:
    #     return response.json()['data'][0]['price']  # Adjust based on the actual API response structure
    # return "Price not available"

    
    # from bs4 import BeautifulSoup

    # url = "https://krama.karnataka.gov.in/MainPage/DailyMrktPriceRep2.aspx?Rep=Var&CommCode=1&VarCode=70&Date=09/11/2024&CommName=Wheat&VarName=Sona"
    # response = requests.get(url)

    # soup = BeautifulSoup(response.content, "html.parser")

    # # Find the table containing the price data
    # table = soup.find("table", {"class": "DataTable"})

    # # Extract the model price (assuming it's in the second row and second column)
    # rows = table.find_all("tr")
    # price = rows[1].find_all("td")[1].text.strip()

    # st.write(f"Model Price: {price}")
    # return price


#Function to fetch government schemes based on crop and location
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

import pandas as pd

def get_crop_price(crop_name,location):
    # Load the Excel file
    file_path = 'CROPS.xlsx'
    excel_data = pd.ExcelFile(file_path)

    # Check if the crop exists in the Excel sheets
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


# def get_crop_price(crop_name, location):
#     # Step 1: Load historical crop data from the uploaded Excel file
#     file_path = 'CROPS.xlsx'
#     data = pd.read_excel(file_path)
    
#     price_prompt = f"predict the currect price of {crop_name}from {data}, if you cannot predict price just give the last price of the particular crop data given in the excel sheet , the provided excel sheet contains data and price of the particular crop. give me price per kg with this format: The price of the crop is XXXXX rupees/quintal."
#     response = model.generate_content(price_prompt)
#     price = response.text

#     return price

    # # Step 2: Filter data by crop and location
    # filtered_data = data[(data['Crop'] == crop_name) & (data['Location'] == location)]
    
    # # Check if there is enough data for prediction
    # if filtered_data.shape[0] < 5:
    #     return "Insufficient data to make a prediction."
    
    # # Step 3: Prepare the data for modeling
    # filtered_data['Year'] = pd.to_datetime(filtered_data['Date']).dt.year
    # X = filtered_data[['Year']]
    # y = filtered_data['Price_per_kg']
    
    # # Step 4: Train-test split
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # # Step 5: Train the model
    # model = LinearRegression()
    # model.fit(X_train, y_train)
    
    # # Step 6: Predict the current price for the most recent year
    # current_year = pd.Timestamp.now().year
    # predicted_price = model.predict([[current_year]])[0]
    
    # Format and return the prediction
    #return f"The predicted price of {crop_name} in {location} is {predicted_price:.2f} rupees/kg."

def get_government_schemes(location, crop_name , plot_size):
    schemes_prompt = f"just list the recent government scheme names for {crop_name} in {location} for plot size of {plot_size} acres."
    response = model.generate_content(schemes_prompt)
    schemes = response.text
    #st.write(price)

    return schemes

    # url = f"https://raitamitra.karnataka.gov.in/english?location={location}&crop={crop_name}"
    # response = requests.get(url)
    # if response.status_code == 200:
    #     return response.json()['schemes']
    # return "No schemes available"

# Function to send SMS using Twilio
def send_sms(phone_number, message):
    from twilio.rest import Client
    #from config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
    TWILIO_SID="AC939cc278f9f948bc0fed65d9d67aa873"
    TWILIO_AUTH_TOKEN="d8ad8df498999d886ba42b173905dca2"
    TWILIO_PHONE_NUMBER="+13185954455"
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

# When button is clicked, predict crop and display information
words = ["wheat","Rice","Ragi" ]
crop = None 
if st.button("Predict Crop"):
    prompt = f"give me a list of suitable crop names for a plot of {plot_size} located in {location}.donot separate the crop with two words by spcae. seperate the different crop with space and list them , choose the crop given - paddy, wheat, tomato, tea, sunflower, sugarcane, rice, ragi, mustard "
    response = model.generate_content(prompt)
    
    crop_suggestion = response.text
    words = crop_suggestion.split()
    st.write(f"Suggested Crop: {crop_suggestion}")

    #Allow user to select a crop
    crop = st.selectbox("options", words)  # Default crop suggestions
    st.write(f"Selected Crop: {crop}")
    # language = st.selectbox("Select language", list(indian_languages.keys()))

if crop:
# Fetch Crop Price & Government Schemes (via API)
    crop_price = get_crop_price(crop,location)
    schemes = get_government_schemes(location, crop, plot_size)

    st.write(f"Latest Price: {crop_price}")
    st.write(f"Government Schemes: {schemes}")

    # Save Farmer details and crop to the database (function below)
    save_farmer_details(name, phone, plot_size, location, crop)
    message = f"Crop: {crop}\nPrice: {crop_price}\n Government Schemes: {schemes}\n Thank you💚"
    send_sms(phone, message)

    st.write("Notification sent!")




# Function to translate message
def translate_message(message, target_language):
    # Translate the message using Google Translate
    translated = translator.translate(message, dest=target_language)
    return translated.text

# List of supported Indian languages for dropdown

# Translate the message when the button is clicked
# if st.button("Translate"):
#     # Get the language code from the dropdown selection
#     target_language = indian_languages[language]
    
#     # Translate the message
#     translated_message = translate_message(message, target_language)
    
#     # Display the translated message
#     st.write(f"Translated message in {language}: {translated_message}") 
    

