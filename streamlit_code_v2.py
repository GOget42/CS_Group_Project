import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import datetime
import pydeck as pdk
from geopy.geocoders import Nominatim

# problems:
# damage: "you selected" has to display the right things 
# reset filters is not workingggg


# Mapbox API Token
MAPBOX_API_TOKEN = "pk.eyJ1IjoidmljaWlpIiwiYSI6ImNtM211cmxkZDA3YTIya3Mzc2Vzd3JwaG0ifQ.Zzo3SdjM9RiwV1cLSnRIyw"

# Title
st.header("Wreckognizer") 
st.markdown("Predict. Protect. Prevent.")


st.write("Wreckognize uses machine learning with clutters to analyze accident data and predict the severity and likelihood of personal injury or property damage. Designed for emergency services, such as police or ambulance, as well as city planners, our tool transforms raw data into actionable insights, empowering communities and organizations to enhance safety and prepare for potential risks.")

# Date picker
st.subheader("Date  and Time Picker")
default_date = date.today() 
selected_date = st.date_input("Choose a date:", value=default_date)
default_time = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)
t = st.time_input("Choose a time of day:", value=default_time)
st.write("You selected:", selected_date, t)

# Risk Level
st.subheader("Risk Level")
option = st.selectbox("Select the risk level:", ("Low Risk", "Moderate Risk", "High Risk", "Critical Risk"))
st.write("You selected:", option)

# personal or property damage
st.subheader("Type of Damage")
personal_injury = st.checkbox("Personal Injury")
property_damage = st.checkbox("Property Damage")
st.write("You selected:") # make it workk

# reset filters button
st.button("Reset All Filters") # make it work..

# put in "you selected: "

# Coordinates for the center of Zürich
latitude_zurich = 47.366669
longitude_zurich = 8.55

# Input field for address search
st.subheader("Interactive Map with Address Search")
address = st.text_input("Enter an address to locate on the map:")

st.subheader("Radius Level")
# Map view state centered on Zürich
scatterplot_radius = st.slider("Select the radius (in meters)", min_value=100, max_value=2000, value=500, step=50)  # User-controlled zoom level
view_state = pdk.ViewState(
    latitude=latitude_zurich,
    longitude=longitude_zurich,
    zoom=12,
    pitch=0,
)

# Initialize map with no markers
layer = pdk.Layer(
    "ScatterplotLayer",
    data=[],  # Empty data for the initial map
    get_position='[longitude, latitude]',
    get_radius=0,  # No markers initially
    get_color=[0, 0, 0, 0],  # Transparent marker
)

# Display the base map
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/streets-v11",
)

# Geocode address function
def geocode_address(address):
    geolocator = Nominatim(user_agent="streamlit-app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


if address:
    # Geocode the entered address
    lat, lon = geocode_address(address)
    if lat and lon:
        # Update the map view to center on the geocoded address
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=12,
            pitch=0,
        )

        # Scatterplot layer to mark the location
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame({"latitude": [lat], "longitude": [lon]}),
            get_position="[longitude, latitude]",
            get_color=[128, 128, 128, 128],  # Grey to have it be half transparent
            get_radius=scatterplot_radius,
        )

        # Update the map with the marker
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/streets-v11",
        )

        # Show the updated map with the location marked
        
    else:
        st.error("Address not found. Please try again.")

st.pydeck_chart(deck)