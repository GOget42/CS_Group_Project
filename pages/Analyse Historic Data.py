# Page1.py

import streamlit as st
import pandas as pd
from modules.utils import convert_lv95_to_wgs84, translate_columns
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

# Set page configuration
st.set_page_config(
    page_title="Wreckognizer - City Accidents Map",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
SEVERITY_COLOR_MAPPING = {
    'Accident with fatalities': 'red',
    'Accident with severe injuries': 'orange',
    'Accident with light injuries': 'yellow',
    'Accident with property damage': 'blue',
}
MAP_BOUNDS = {
    'min_lat': 47.3568,
    'max_lat': 47.3988,
    'min_lon': 8.4655,
    'max_lon': 8.6155
}

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/clean/merged.csv")
    return df

@st.cache_data
def translate_data(df):
    return translate_columns(df)

@st.cache_data
def convert_coordinates(df):
    return convert_lv95_to_wgs84(df)

df = load_data()
df = translate_data(df)
df = convert_coordinates(df)

# --- Define Functions ---
def create_folium_map(data, map_type):
    if data.empty:
        return folium.Map(location=[0, 0], zoom_start=2, tiles='CartoDB Positron')

    center_lat = (MAP_BOUNDS['min_lat'] + MAP_BOUNDS['max_lat']) / 2
    center_lon = (MAP_BOUNDS['min_lon'] + MAP_BOUNDS['max_lon']) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB Positron')

    if map_type in ["Markers", "Both"]:
        marker_cluster = MarkerCluster(name='Accident Markers').add_to(m)
        for _, row in data.iterrows():
            severity = row['AccidentSeverityDesc']
            color = SEVERITY_COLOR_MAPPING.get(severity, 'gray')
            popup_text = f"""
                <b>Accident Type:</b> {row['AccidentTypeDesc']}<br>
                <b>Severity:</b> {severity}<br>
                <b>Road Type:</b> {row['RoadTypeDesc']}<br>
                <b>Date:</b> {row['year']}-{row['month']} (Weekday: {row['WeekdayDesc']})<br>
                <b>Time:</b> {row['hour']}:00<br>
            """
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7
            ).add_to(marker_cluster)

    if map_type in ["Heatmap", "Both"]:
        heat_data = data[['lat', 'lon']].dropna().values.tolist()
        HeatMap(
            heat_data,
            radius=10,
            blur=15,
            max_zoom=1,
            gradient={
                0.2: 'blue',
                0.4: 'lime',
                0.6: 'yellow',
                0.8: 'orange',
                1.0: 'red'
            },
            name='Heatmap'
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

# --- App Layout ---
st.title("🚦 City Accidents Map")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter the Data")

# Reset Filters Button
if 'reset_filters' not in st.session_state:
    st.session_state.reset_filters = False

def reset_filters():
    st.session_state.reset_filters = True

st.sidebar.button("🔄 Reset Filters", on_click=reset_filters)

# Date Filters
with st.sidebar.expander("📅 Date Filters", expanded=False):
    years = sorted(df['year'].unique())
    default_year = [years[-1]] if years else []
    selected_years = st.multiselect(
        "🗓️ Year",
        options=years,
        default=default_year,
        help="Select the year(s) of the accidents."
    )

    months = sorted(df['month'].unique())
    month_names = {1: "January", 2: "February", 3: "March", 4: "April",
                   5: "May", 6: "June", 7: "July", 8: "August",
                   9: "September", 10: "October", 11: "November", 12: "December"}
    month_options = [month_names.get(month, f"Month {month}") for month in months]
    selected_months = st.multiselect(
        "🗓️ Month",
        options=month_options,
        default=month_options,
        help="Select the month(s) of the accidents."
    )

    weekdays = sorted(df['WeekdayDesc'].unique())
    default_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    selected_weekdays = st.multiselect(
        "📅 Weekday",
        options=weekdays,
        default=default_weekdays,
        help="Select the day(s) of the week when accidents occurred."
    )

# Time Filters
with st.sidebar.expander("⏰ Time Filters", expanded=False):
    hours = sorted(df['hour'].unique())
    min_hour = int(df['hour'].min())
    max_hour = int(df['hour'].max())
    selected_hours = st.slider(
        "🕒 Hour of Day",
        min_value=min_hour,
        max_value=max_hour,
        value=(0, 23),
        step=1,
        help="Select the time range during which accidents occurred."
    )

# Accident Details Filters
with st.sidebar.expander("🚗 Accident Details", expanded=False):
    accident_types = sorted(df['AccidentTypeDesc'].unique())
    default_accident_types = [
        'Accident with rear-end collision',
        'Accident involving pedestrian(s)',
        'Accident when overtaking or changing lanes'
    ]
    default_accident_types = [atype for atype in default_accident_types if atype in accident_types]
    selected_accident_types = st.multiselect(
        "🚦 Accident Type",
        options=accident_types,
        default=default_accident_types,
        help="Select the type(s) of accidents to display."
    )

    severity_cats = sorted(df['AccidentSeverityDesc'].unique())
    default_severity_cats = ['Accident with fatalities', 'Accident with severe injuries']
    selected_severity_cats = st.multiselect(
        "⚠️ Accident Severity",
        options=severity_cats,
        default=default_severity_cats,
        help="Select the severity level(s) of accidents to display."
    )

# Involvement Filters
with st.sidebar.expander("👥 Accident Involvements", expanded=False):
    involvement_options = {
        "Pedestrian": "AccidentInvolvingPedestrian",
        "Bicycle": "AccidentInvolvingBicycle",
        "Motorcycle": "AccidentInvolvingMotorcycle"
    }
    selected_involvements = [label for label in involvement_options if st.checkbox(label, value=False, key=label)]

# Road Type Filters
with st.sidebar.expander("🛣️ Road Type", expanded=False):
    road_types = sorted(df['RoadTypeDesc'].unique())
    default_road_types = ['Principal road', 'Minor road']
    selected_road_types = st.multiselect(
        "🛤️ Road Type",
        options=road_types,
        default=default_road_types,
        help="Select the road type(s) where accidents occurred."
    )

# Map Type Selection
with st.sidebar.expander("🗺️ Map Type", expanded=False):
    map_type = st.radio(
        "🌐 Choose Map Visualization",
        options=["Markers", "Heatmap", "Both"],
        index=0,
        help="Select how you want to visualize the accidents on the map."
    )

# Reset session state after resetting filters
if st.session_state.reset_filters:
    st.session_state.reset_filters = False

# --- Apply Filters ---
selected_month_numbers = [month for month, name in month_names.items() if name in selected_months]

filtered_df = df[
    (df['year'].isin(selected_years) if selected_years else True) &
    (df['month'].isin(selected_month_numbers) if selected_months else True) &
    (df['WeekdayDesc'].isin(selected_weekdays) if selected_weekdays else True) &
    (df['AccidentTypeDesc'].isin(selected_accident_types) if selected_accident_types else True) &
    (df['AccidentSeverityDesc'].isin(selected_severity_cats) if selected_severity_cats else True) &
    (df['RoadTypeDesc'].isin(selected_road_types) if selected_road_types else True) &
    (df['hour'].between(selected_hours[0], selected_hours[1]))
]

# Apply involvement filters
for label in selected_involvements:
    col_name = involvement_options[label]
    filtered_df = filtered_df[filtered_df[col_name] == 1]

# Display filtered results
if filtered_df.empty:
    st.warning("⚠️ No accidents match the selected filters. Please adjust your selections.")
else:
    st.success(f"**Number of accidents:** {len(filtered_df)}")
    folium_map = create_folium_map(filtered_df, map_type)
    st_folium(
        folium_map,
        width=1200,
        height=700,
        key="city_accidents_map"
    )
