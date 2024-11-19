#requirements / libraries
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import pydeck as pdk

# something for the map to work (idk what)
MAPBOX_API_TOKEN = "pk.eyJ1IjoidmljaWlpIiwiYSI6ImNtM211cmxkZDA3YTIya3Mzc2Vzd3JwaG0ifQ.Zzo3SdjM9RiwV1cLSnRIyw"

#title
st.header("Wreckognizer")
st.markdown("Predict. Protect. Prevent.")
st.write("Wreckognize leverages cutting-edge machine learning to analyze accident data and predit the severity and likelihood of personal injury or property damage. Designed for decision-makers and analysts, our tool transforms raw data into actionable insights, empowering communities and organizations to enhance saftey and prepare for potential risks. ")

st.write("To find the risk level at a specific date at a specific place, please input the following:")

#######

#date picker
st.subheader("Date Picker ")

default_date = date.today() 

selected_date = st.date_input("Choose a date:", value=default_date)

st.write("You selected:", selected_date)

# time picker
st.subheader("Time Picker")

default_time = datetime.datetime.now().time()

t = st.time_input("Chose a time of day:", value=default_time)
st.write("You selected", t)

########

st.subheader("Define search radius")
age = st.slider("Chose your km radius", 0, 15)
st.write("You chose ", age, "km.")
#we chose 15 km bc zürich is 90 km2 and it's 30 in each direction, so we can chose 15 as a max. 

#chose to find a location, street adress, etc. 

#######

st.subheader("Risk Level")

option = st.selectbox(
    "Select the risk level:",
    ("Low Risk", "Moderate Risk", "High Risk", "Critical Risk"),
)

st.write("You selected:", option)

######

##old map
# df = pd.DataFrame(
   # np.random.randn(100,2) / [50, 50] + [47.366669, 8.55],
    # columns=["lat", "lon"],
# )

# st.subheader("This is a randomized scatterplot of the city of Zürich")
# st.map(df)

######

### new map
st.subheader("New, better map")

# data for the coordinated of city of zürich
data = pd.DataFrame({
    'latitude': [47.366669],
    'longitude': [8.55],
})

# fixed place of map
view_state = pdk.ViewState(
    latitude=data['latitude'].mean(),
    longitude=data['longitude'].mean(),
    zoom=15,
    pitch=0,
)

# deck.gl map
layer = pdk.Layer(
    "ScatterplotLayer",
    data,
    get_position='[longitude, latitude]',
    get_radius=100,
    get_colour=[255, 0, 0],
)

# display style (like google maps)
deck = pdk.Deck(
    layers=[layer], 
    initial_view_state=view_state, 
    map_style="mapbox://styles/mapbox/streets-v11",
    )

# show the map in streamlit
st.pydeck_chart(deck)