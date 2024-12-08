import streamlit as st
import pandas as pd
from pyproj import Transformer
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import joblib
from datetime import datetime, timedelta, date, time
import random  # Import for random selection
from modules.utils import assign_average_volume, transform, get_weather, get_road_type, translate_columns, convert_lv95_to_wgs84
from modules.open_meteo_api import open_meteo_request
import numpy as np
import pickle

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Predict Accidents Severity", layout="wide")

# --- Initialize Session State ---
if 'predicted_locations' not in st.session_state:
    st.session_state.predicted_locations = []  # List to store (lat, lon)
if 'predictions' not in st.session_state:
    st.session_state.predictions = []  # List to store prediction results
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None  # To store (lat, lon)
if "selected_time" not in st.session_state:
    st.session_state.selected_time = time(datetime.now().hour)

# --- Load Pre-trained Model ---
@st.cache_resource
def load_model():
    model = pickle.load(open("data/models/finalized_model.sav", "rb"))
    return model

model = load_model()

# --- Load Additional Data ---
@st.cache_resource
def load_volume():
    data = pd.read_csv('data/inference/average_volume.csv')
    return data

average_volume = load_volume()

@st.cache_resource
def load_locations():
    data = pd.read_csv('data/inference/locations.csv')
    return data

locations = load_locations()

# --- Define Mapping Dictionaries ---
ACCIDENT_TYPE_MAPPING = {
    'at0': 'Accident with skidding or self-accident',
    'at1': 'Accident when overtaking or changing lanes',
    'at2': 'Accident with rear-end collision',
    'at3': 'Accident when turning left or right',
    'at4': 'Accident when turning into main road',
    'at5': 'Accident when crossing the lane(s)',
    'at6': 'Accident with head-on collision',
    'at7': 'Accident when parking',
    'at8': 'Accident involving pedestrian(s)',
    'at9': 'Accident involving animal(s)',
    'at00': 'Other',
}

ROAD_TYPE_MAPPING = {
    'rt432': 'Principal road',
    'rt433': 'Minor road',
    'rt439': 'Other',
}

WEEKDAY_MAPPING = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}

# --- Define Severity Colors (for consistency) ---
SEVERITY_COLOR_MAPPING = {
    'Accident with fatalities': 'red',
    'Accident with severe injuries': 'orange',
    'Accident with light injuries': 'yellow',
    'Accident with property damage': 'blue',
    'Unknown': 'gray'  # Fallback color for unmapped severities
}

# --- Define Allowed Map Area (e.g., Zurich) ---
# Define the bounding box for allowed area
MIN_LAT, MAX_LAT = 47.3568, 47.3988
MIN_LON, MAX_LON = 8.4655, 8.6155

def is_within_bounds(lat, lon):
    """Check if the given latitude and longitude are within the allowed bounds."""
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON

# --- Function to Add Legend ---
def add_legend(folium_map):
    legend_html = '''
     <div style="
     position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 160px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     padding: 10px;
     border-radius: 5px;
     ">
     &nbsp;<b>Severity Legend</b><br>
     &nbsp;<span style="background-color:red; width:10px; height:10px; display:inline-block; margin-right:5px;"></span>&nbsp;Fatalities<br>
     &nbsp;<span style="background-color:orange; width:10px; height:10px; display:inline-block; margin-right:5px;"></span>&nbsp;Severe Injuries<br>
     &nbsp;<span style="background-color:yellow; width:10px; height:10px; display:inline-block; margin-right:5px;"></span>&nbsp;Light Injuries<br>
     &nbsp;<span style="background-color:blue; width:10px; height:10px; display:inline-block; margin-right:5px;"></span>&nbsp;Property Damage<br>
     &nbsp;<span style="background-color:gray; width:10px; height:10px; display:inline-block; margin-right:5px;"></span>&nbsp;Unknown
     </div>
     '''
    folium_map.get_root().html.add_child(folium.Element(legend_html))
    return folium_map

# --- Function to Create Folium Map ---
def create_folium_map():
    """
    Creates a Folium map centered on the allowed area with markers based on session state.
    """
    # Initialize Folium map centered on allowed area
    m = folium.Map(location=[(MIN_LAT + MAX_LAT) / 2, (MIN_LON + MAX_LON) / 2],
                   zoom_start=12,
                   tiles='CartoDB Positron')

    # Add Predicted Markers
    if st.session_state.predicted_locations and st.session_state.predictions:
        for loc, pred in zip(st.session_state.predicted_locations, st.session_state.predictions):
            marker_color = 'red' if pred == 1 else 'green'
            severity_label = "Severe" if pred == 1 else "Minor"
            folium.Marker(
                location=loc,
                popup=f'Predicted Severity: {severity_label}',
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(m)

    # Add Selected Location Marker
    if st.session_state.selected_location:
        folium.Marker(
            location=st.session_state.selected_location,
            popup='Selected Location',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Add Click Control to allow user to select location
    folium.ClickForMarker(popup='Selected Location').add_to(m)

    # Add Legend
    m = add_legend(m)

    return m

# --- Streamlit App Layout ---

st.title("🔮 Predict Accident Severity")

# --- Main Area: Instructions ---
st.markdown("""
## **Instructions:**
1. **Select the accident type**, involvements, and pick the date and time from the sidebar.
2. **Click on the map** to select the accident location within the allowed area.
3. **Choose the number of predictions** using the slider.
4. **Submit the form** to see the predicted severity of the accident(s).
""")

# --- Sidebar: User Inputs within Expanders ---
with st.sidebar:
    st.header("🔮 Prediction Inputs")

    # --- Accident Type Selector ---
    with st.expander("🚦 Accident Type", expanded=False):
        accident_type = st.selectbox(
            "Accident Type",
            label_visibility='hidden',
            options=ACCIDENT_TYPE_MAPPING.values(),
            help="Select the type of accident."
        )

    # --- Accident Involvements Selectors ---
    with st.expander("👥 Accident Involvements", expanded=False):
        involving_pedestrian = st.checkbox("Pedestrian")
        involving_bicycle = st.checkbox("Bicycle")
        involving_motorcycle = st.checkbox("Motorcycle")

    # --- Date and Time Selectors ---
    with st.expander("📅 Date and Time", expanded=False):
        today = date.today()
        one_month_later = today + timedelta(days=30)
        selected_date = st.date_input(
            "Date",
            label_visibility='hidden',
            value=today,
            min_value=date(2012, 1, 1),
            max_value=one_month_later,
            help="Select the date of the accident (between 2012 and up to 30 days in the future)."
        )
        selected_time = st.time_input(
            "Time",
            label_visibility='hidden',
            step=3600,
            value=st.session_state.selected_time,
            help="Select the time of the accident."
        )

    # --- Prediction Count Slider ---
    with st.expander("🔢 Number of Predictions", expanded=False):
        prediction_count = st.slider(
            "Select number of predictions:",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
            help="Choose how many accident severity predictions you want to generate."
        )

    # --- Submit Button ---
    submit_button = st.button("🔮 Predict Severity")

# --- Prediction Logic ---
if submit_button:
    # Validate the selected date
    date_validity = (date(2012, 1, 1) <= selected_date <= (date.today() + timedelta(days=30)))
    if not date_validity:
        st.error("Please select a date between January 1, 2012, and up to 30 days into the future.")

    # Validate the selected location
    if not st.session_state.selected_location:
        st.error("Please select a valid location within the allowed area to make a prediction.")
    else:
        if date_validity and st.session_state.selected_location:
            try:
                # Combine date and time into a single datetime object
                selected_datetime = datetime.combine(selected_date, selected_time)

                # Extract month, weekday, hour
                month = selected_datetime.month
                weekday = selected_datetime.isoweekday()  # Monday=1, Sunday=7
                hour = selected_datetime.hour

                # Extract x and y (longitude and latitude)
                lon, lat = st.session_state.selected_location[1], st.session_state.selected_location[0]

                # Get Road Type and closest training accident coordinates
                roadtypes, closest_lons, closest_lats = get_road_type(lon, lat, locations, n=prediction_count)

                # Construct the DataFrame with 'dateTime' included
                input_data = {
                    'dateTime': [selected_datetime] * prediction_count,
                    'AccidentType': [accident_type] * prediction_count,
                    'AccidentInvolvingPedestrian': [int(involving_pedestrian)] * prediction_count,
                    'AccidentInvolvingBicycle': [int(involving_bicycle)] * prediction_count,
                    'AccidentInvolvingMotorcycle': [int(involving_motorcycle)] * prediction_count,
                    'RoadType': roadtypes,
                    'month': [month] * prediction_count,
                    'weekday': [weekday] * prediction_count,
                    'hour': [hour] * prediction_count,
                }

                input_df = pd.DataFrame(input_data)

                # Assign the average traffic and pedestrian volumes
                input_df = assign_average_volume(input_df, average_volume, 3, 2)

                # Get weather data
                input_df = get_weather(input_df, selected_datetime)

                # Transform input data using preprocessor
                input_df_transformed = transform(input_df)

                # Predict severity
                predictions = model.predict(input_df_transformed)

                # Update session_state with predicted locations and predictions
                predicted_locations = list(zip(closest_lats, closest_lons))  # List of (lat, lon)
                st.session_state.predicted_locations = predicted_locations
                st.session_state.predictions = predictions.tolist()

                # Clear the initially selected location
                st.session_state.selected_location = None

                # Display the results
                # Display the consolidated results
                severe_count = predictions.sum()
                minor_count = prediction_count - severe_count
                severity_labels = ["Severe" if pred == 1 else "Minor" for pred in predictions]
                results_message = "\n".join([f"Prediction {i + 1}: {label}" for i, label in enumerate(severity_labels)])
                st.success(f"**Prediction Results:**"
                           f"\nNumber of minor accidents: {minor_count}"
                           f"\nNumber of severe accidents: {severe_count}"
                           )

                # --- Show Weather Data for First Period ---
                # Extract weather columns for the first period
                weather_features = ['temperature_2m', 'precipitation', 'snowfall', 'snow_depth', 'surface_pressure', 'cloud_cover']
                first_period_columns = [f'{feature}_period_0' for feature in weather_features]

                # Ensure that input_df has the weather columns for the first period
                missing_weather_cols = [col for col in first_period_columns if col not in input_df.columns]
                if missing_weather_cols:
                    st.error(f"The following weather columns for the first period are missing in the input data: {missing_weather_cols}")
                else:
                    # Extract the weather data for the first period
                    first_period_weather = input_df.loc[0, first_period_columns]

                    # Display weather feature values
                    st.markdown("### Weather Data (Historic or Forecast)")
                    st.caption('Credit to Open-Meteo for their API: Open-Meteo.com')
                    st.write(f"- Temperature: {first_period_weather['temperature_2m_period_0']} °C")
                    st.write(f"- Precipitation: {first_period_weather['precipitation_period_0']} mm")
                    st.write(f"- Snowfall: {first_period_weather['snowfall_period_0']} cm")
                    st.write(f"- Snow Depth: {first_period_weather['snow_depth_period_0']} cm")
                    st.write(f"- Surface Pressure: {first_period_weather['surface_pressure_period_0']} hPa")
                    st.write(f"- Cloud Cover: {first_period_weather['cloud_cover_period_0']}%")

            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")


# --- Handle Map Clicks ---
# Create and display the map
folium_map = create_folium_map()
map_click = st_folium(
    folium_map,
    width=1200,
    height=700,
    returned_objects=["last_clicked"],
    key="predict_map"  # Fixed key to maintain state
)

# --- Retrieve Clicked Location ---
if map_click and "last_clicked" in map_click and map_click["last_clicked"]:
    clicked_lat = map_click["last_clicked"]["lat"]
    clicked_lon = map_click["last_clicked"]["lng"]

    # Check if clicked location is within bounds
    if is_within_bounds(clicked_lat, clicked_lon):
        st.session_state.selected_location = (clicked_lat, clicked_lon)
        st.markdown(f"**Selected Location:** Latitude {clicked_lat:.5f}, Longitude {clicked_lon:.5f}")
    else:
        st.error("Selected location is outside the allowed area. Please select a location within the map bounds.")
        st.session_state.selected_location = None
else:
    # If no location is selected and no prediction has been made
    if not (st.session_state.predicted_locations and st.session_state.predictions):
        st.info("Click on the map to select a location.")

# --- Reset Prediction Button (Optional) ---
if st.button("🔄 Reset Prediction"):
    st.session_state.predicted_locations = []
    st.session_state.predictions = []
    st.session_state.selected_location = None
    st.rerun()
