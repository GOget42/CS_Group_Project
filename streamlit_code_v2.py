#requirements#title
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

#title
st.header("Wreckognizer")
st.markdown("Predict. Protect. Prevent")
st.markdown("Wreckognize leverages cutting-edge machine learning to analyze accident data and predit the severity and likelihood of personal injury or property damage. Designed for decision-makers and analysts, our tool transforms raw data into actionable insights, empowering communities and organizations to enhance saftey and prepare for potential risks. ")

#date picker
st.subheader("Date Picker ")

# Default date is today's date
default_date = date.today() 

# Date input widget
selected_date = st.date_input("Choose a date:", value=default_date)

# Display the selected date
st.write("You selected:", selected_date)

st.subheader("Define search radius")
age = st.slider("Chose your km radius", 0, 15)
st.write("You chose ", age, "km.")
#we chose 15 km bc zürich is 90 km2 and it's 30 in each direction, so we can chose 15 as a max. 

st.subheader("Risk Level")

option = st.selectbox(
    "Select the risk level:",
    ("Low Risk", "Moderate Risk", "High Risk", "Critical Risk"),
)

st.write("You selected:", option)


df = pd.DataFrame(
    np.random.randn(100,2) / [50, 50] + [47.366669, 8.55],
    columns=["lat", "lon"],
)

st.subheader("This is a randomized scatterplot of the city of Zürich")
st.map(df)


