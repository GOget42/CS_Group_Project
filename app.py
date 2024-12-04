import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import datetime
import pydeck as pdk
from geopy.geocoders import Nominatim

def main():

    st.image("logo.png", width=400)

    st.logo("logo.png", size="large", icon_image="logo.png")
    # Mapbox API Token
    MAPBOX_API_TOKEN = "pk.eyJ1IjoidmljaWlpIiwiYSI6ImNtM211cmxkZDA3YTIya3Mzc2Vzd3JwaG0ifQ.Zzo3SdjM9RiwV1cLSnRIyw"

    # Title
    # st.header("Wreckognizer") 
    # st.markdown("Predict. Protect. Prevent.")
    st.write("")
    st.write("Wreckognizer uses machine learning with clutters to analyze accident data and predict the severity and likelihood of personal injury or property damage. Designed for emergency services, such as police or ambulance, as well as city planners, our tool transforms raw data into actionable insights, empowering communities and organizations to enhance safety and prepare for potential risks.")
    st.write("")

    # Date picker
    st.sidebar.subheader("Date  and Time Picker")
    default_date = date.today() 
    selected_date = st.sidebar.date_input("Choose a date:", value=default_date, format="DD.MM.YYYY")
    default_time = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)
    t = st.sidebar.time_input("Choose a time of day:", value=default_time)
    st.sidebar.write("You selected:", selected_date, t)
    st.sidebar.write("")

    # Risk Level
    st.sidebar.subheader("Risk Level")
    option = st.sidebar.selectbox("Select the risk level:", ("Low Risk", "Moderate Risk", "High Risk", "Critical Risk"))
    st.sidebar.write("You selected:", option)
    st.sidebar.write("")

    # personal or property damage
    st.sidebar.subheader("Type of Damage")
    personal_injury = st.sidebar.checkbox("Personal Injury")
    property_damage = st.sidebar.checkbox("Property Damage")

    if personal_injury and property_damage:
        st.sidebar.write("You selected: Personal Injury and Property Damage")
    elif property_damage:
        st.sidebar.write("You selected: Propery Damage")
    elif personal_injury:
        st.sidebar.write("You selected: Personal Injury")
    else: 
        st.sidebar.write("You selected: ")

    # Coordinates for the center of Zürich
    latitude_zurich = 47.366669
    longitude_zurich = 8.55

    # Input field for address search
    st.subheader("Address Search")
    address = st.text_input("Enter an address to locate on the map:")
    st.write("")

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
            circle_layer = pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame({"latitude": [lat], "longitude": [lon]}),
                get_position="[longitude, latitude]",
                get_color=[128, 128, 128, 128],  # Grey to have it be half transparent
                get_radius=scatterplot_radius,
            )

            marker_layer = pdk.Layer(
                "IconLayer",
                data=pd.DataFrame({
                    "latitude": [lat],
                    "longitude": [lon],
                    "icon_data": ["pin"],
                }),
                get_position="[longitude, latitude]",
                icon_atlas="C:/Users/waffe/streamlit/pin.png",  # Replace with your image path
                icon_mapping={
                    "pin": {
                        "x": 0,
                        "y": 0,
                        "width": 128,
                        "height": 128,
                        "anchorY": 128,
                    }
                },
                size_scale=15,
            )



            # Update the map with the marker
            deck = pdk.Deck(
                layers=[circle_layer, marker_layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/streets-v11",
            )

            # Show the updated map with the location marked

        else:
            st.error("Address not found. Please try again.")

    st.pydeck_chart(deck)

if __name__ == "__main__":
    main()
