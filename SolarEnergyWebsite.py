import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import csv
import datetime
import random

# import pytz
# import astral
# from geopy.geocoders import Nominatim
# import pycountry

MIN_HOUR_OF_INTEREST = 10
MAX_HOUR_OF_INTEREST = 15

def get_prediction(data={"Humidity":49.993895,"AmbientTemp":22.878300000000003,"Visibility":5,"Pressure":905.6,"Wind.Speed":24.5,"Cloud.Ceiling":361,"cos_mon":0,"sine_mon":0.9898214418809328,"cos_hr":-0.3090169943749473,"Season":"Summer","sine_hr":0.9510565162951536}):
  url = 'https://askai.aiclub.world/af9ffcbc-4f97-45c7-a304-eb48c361355e'
  r = requests.post(url, data=json.dumps(data))
  response = getattr(r,'_content').decode("utf-8")
  response = json.loads(response)
  response = json.loads(response["body"])
  print(response["predicted_label"])
  return response["predicted_label"]


def get_cyclical_values(month, hour):
    delta_hr = hour-MIN_HOUR_OF_INTEREST
    sine_mon = np.sin((month-1)*np.pi/11)
    cos_mon = np.cos((month - 1)*np.pi/11)
    sine_hr = np.sin(delta_hr*np.pi/(MAX_HOUR_OF_INTEREST - MIN_HOUR_OF_INTEREST))
    cos_hr = np.cos((delta_hr*np.pi/(MAX_HOUR_OF_INTEREST-MIN_HOUR_OF_INTEREST)))
    return sine_mon, cos_mon, sine_hr, cos_hr

st.set_page_config(page_title="Solar Energy Prediction", page_icon=":sunny:", layout="wide")
st.title("Solar Energy Prediction")
st.write("The dataset used to create this AI has 21045 samples. There are 14 features, where 6 are categorical and 8 are numerical. In this project, a regression type of AI called RandomForestRegressor is trained. It accepts 14 features as input. The range of values in the prediction column PolyPwr of the dataset is 0.25733 - 34.28502. The root mean square error (RMSE) value of this AI is 4.1848.")
st.markdown("<h2 style='font-size: 24px;'>How to use website & input features</h2>", unsafe_allow_html=True)
st.write("Enter all user input feature accurately to predict solar energy output[Make sure to select season], check values entered in side bar for accuracy. Then click generate predictions, output will be at the bottom underneath map.")
st.markdown("<h2 style='font-size: 24px;'>Latest weather data based on input</h2>", unsafe_allow_html=True)
# Initialize the page view count
page_views = 0

# Check if the page view count has been initialized in a previous session
if 'page_views' in st.session_state:
    page_views = st.session_state.page_views

# Increment the page view count
page_views += 1

# Store the updated page view count in the session state
st.session_state.page_views = page_views

# Display the page view count
st.write(f'This page has been viewed {page_views} times.')

st.sidebar.header('User Input Features')
location_city = st.sidebar.text_input("Enter city location", value="Dallas")
location_country = st.sidebar.text_input("Enter country location", value="United States")
selected_year = st.sidebar.selectbox('Select the year', (list(reversed(range(2010,2024)))))
selected_month = st.sidebar.number_input("Select the month", min_value=1, max_value=12, value=1, step=1)
selected_day = st.sidebar.number_input('Select the day', min_value=1, max_value=31, value=1, step=1)
selected_hour = st.sidebar.number_input('Select the hour', min_value=1, max_value=24, value=1, step=1)
selected_season = st.sidebar.selectbox('Select the season', ("", "Winter", "Spring", "Summer", "Fall"))
if selected_month % 2  == 0 and selected_day == 31:
    st.sidebar.write("Invalid date, please enter a valid date[Wrong Number of Days]")
elif selected_month == 2 and selected_year % 4 == 0 and selected_day >= 29:
    st.sidebar.write("Invalid date, please enter a valid date[Leap Year]")
predictedPolyPWR = 0

#country codes
dic = {}
with open("wikipedia-iso-country-codes.csv") as f:
    file= csv.DictReader(f, delimiter=',')
    for line in file:
        dic[line['English short name lower case']] = line['Alpha-2 code']
countries = ""
try:
    countries = dic[location_country]
except KeyError:
    st.error("Please enter the country in the right format(Will assume country otherwise)")
#api call
apikey = "b72f3551e770c27131559dfd1fa31e03"
city = location_city
country = location_country
url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{countries}&APPID=c78051870137cb6940ffb9c2075be6ec'

r = requests.get(url)
response = getattr(r,'_content').decode("utf-8")
data = json.loads(response)

latitude = 0
longitude = 0
temperature = 0
temp_feels_like = 0
temp_min = 0
temp_max = 0
humidity = 0
pressure = 0
wind_speed = 0
visibility = 0
clouds = 0
weather_description = "Placeholder"
sunrise_time = 3
Sunset = 3
sunset_time = 0
timezone = 0
response_dict = {}

sine_mon, cos_mon, sine_hr, cos_hr = get_cyclical_values(selected_month, selected_hour)

try:
    latitude = data['coord']['lat']
    longitude = data['coord']['lon']
    temperature = data['main']['temp']
    temp_feels_like = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind_speed = data['wind']['speed']
    visibility = data['visibility']
    clouds = data['clouds']['all']
    weather_description = data['weather'][0]['description']
    sunrise_time = data['sys']['sunrise']
    sunset_time = data['sys']['sunset']
    timezone = data['timezone']

    response_dict["Humidity"] = humidity
    response_dict["AmbientTemp"] = temperature
    response_dict["Wind.Speed"] = wind_speed
    response_dict["Visibility"] = visibility
    response_dict["Pressure"] = pressure
    response_dict["Cloud.Ceiling"] = clouds
    response_dict["Season"] = selected_season
    response_dict["sine_mon"] = sine_mon
    response_dict["cos_mon"] = cos_mon
    response_dict["sine_hr"] = sine_hr
    response_dict["cos_hr"] = cos_hr
except KeyError:
    st.error("Please enter a valid input in the 'User Input Features' Side-bar[Wrong city or country]/Unentered")


#Formatting api response
temperature_fahrenheit = round((temperature - 273.15) * 1.8 + 32, 2)
temp_feels_like_fahrenheit = round((temp_feels_like - 273.15) * 1.8 + 32, 2)
temp_min_fahrenheit = round((temp_min - 273.15) * 1.8 + 32, 2)
temp_max_fahrenheit = round((temp_max - 273.15) * 1.8 + 32, 2)

sunrise_datetime = datetime.datetime.fromtimestamp(sunrise_time)
sunrise_formatted = sunrise_datetime.strftime('%Y-%m-%d %H:%M:%S')

sunset_datetime = datetime.datetime.fromtimestamp(sunset_time)
sunset_formatted = sunset_datetime.strftime('%Y-%m-%d %H:%M:%S')

timezone_offset = datetime.timedelta(seconds=timezone)
timezone_formatted = str(timezone_offset)


weather_data = pd.DataFrame({
    'Latitude': [latitude],
    'Longitude': [longitude],
    'Temperature(°F)': [temperature_fahrenheit],
    'Feels Like(°F)': [temp_feels_like_fahrenheit],
    'Min Temp(°F)': [temp_min_fahrenheit],
    'Max Temp(°F)': [temp_max_fahrenheit],
    'Humidity': [humidity],
    'Pressure': [pressure],
    'Wind Speed': [wind_speed],
    'Visibility': [visibility],
    'Cloudiness': [clouds],
    'Weather Description': [weather_description],
    'Sunrise': [sunrise_formatted],
    'Sunset': [sunset_formatted],
    'Timezone(UTC)': [timezone_offset],
}, columns=['Latitude', 'Longitude', 'Temperature(°F)', 'Feels Like(°F)', 'Min Temp(°F)', 'Max Temp(°F)', 'Humidity', 'Pressure', 'Wind Speed', 'Visibility', 'Cloudiness', 'Weather Description', 'Sunrise', 'Sunset', 'Timezone'])

data = {'lat': [latitude],
        'lon': [longitude]}
df = pd.DataFrame(data)

#Making columns to display the dataframe and the mapr
cols = st.columns(2)
cols[0],cols[1] = st.columns((1,2))
cols[1].map(df)
cols[0].write(weather_data.T)
cols[0].markdown(f"<span style='font-size: 12px;'>^^Expand & Adjust dataframe config to view current weather data based on user input features(used to predict solar energy output)^^</span>", unsafe_allow_html=True)
predictedPolyPWR = format(get_prediction(response_dict))
st.write("")
st.markdown("<span style='font-size: 12px;'>By Sriram Polineni</span>", unsafe_allow_html=True)
# # Create a geolocator object
# geolocator = Nominatim(user_agent='my_app')

# # Combine the city and country into a single query string
# location = f'{location_city}, {location_country}'

# # Use the geolocator to retrieve the latitude and longitude coordinates
# location_data = geolocator.geocode(location)

# # Extract the latitude and longitude coordinates from the location data
# country_obj = pycountry.countries.search_fuzzy(location_country)[0]

# continent_name = country_obj.continent.name
# latitude = location_data.latitude
# longitude = location_data.longitude
# timezone_pytz = continent_name + '/' + location_city
# tz = pytz.timezone(timezone_pytz)

# # Create a datetime object with the specified date and time
# dt = tz.localize(datetime.datetime(selected_year, selected_month, selected_day, selected_hour))

# # Create an astral location object for the city
# location = astral.LocationInfo(location_city, location_country, timezone, latitude, longitude)

# # Determine the season for the specified date and time
# season = location.season(dt)
# season_bool = False
# # Check if the entered season matches the calculated season
# if selected_season.lower() != season.lower():
#     st.sidebar.write("The entered season is not accurate; select a valid season to continue.")
#     season_bool = False
# else:
#     season_bool = True

st.sidebar.markdown("<span style='font-size: 12px;'>*Please make sure that the season is correct according to hemisphere and location</span>", unsafe_allow_html=True)

if len(selected_season) != 0:
    if(st.sidebar.button("Generate Predictions")):
        cols[1].markdown(f"<span style='font-size: 18px;'>Predicted polyPWR(watts): <span style='color: #7FFF00; font-weight: bold; font-style: italic; border: 1px solid white; border-radius: 5px; padding: 5px;'>{(predictedPolyPWR)}</span></span>", unsafe_allow_html=True)
#Remove later
hide_streamlit_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
