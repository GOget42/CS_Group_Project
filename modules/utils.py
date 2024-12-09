# Contains functions for getting average volume data and pre-trained Columntransformer during inference
import random
from joblib import load
import time
import pandas as pd
from datetime import timedelta, datetime
from modules.open_meteo_api import open_meteo_request
from pyproj import Transformer

def timed_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.6f} seconds")
        return result
    return wrapper

def convert_lv95_to_wgs84(df):
    transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
    df['lon'], df['lat'] = transformer.transform(df['x'].values, df['y'].values)
    return df


def get_road_type(lon, lat, locations, n=1):
    distances = (locations['lon'] - lon) ** 2 + (locations['lat'] - lat) ** 2
    closest_indices = distances.nsmallest(n*5).index.tolist()  # Get closest 100 indices
    n = min(n, len(closest_indices))  # Ensure n doesn't exceed available locations
    selected_indices = random.sample(closest_indices, n)  # Randomly select n indices

    roadtypes = locations.loc[selected_indices, 'RoadType'].tolist()
    closest_x = locations.loc[selected_indices, 'lon'].tolist()
    closest_y = locations.loc[selected_indices, 'lat'].tolist()

    return roadtypes, closest_x, closest_y

@timed_function
def assign_average_volume(df, volume, number_of_stations, number_of_periods):
    # Make a copy of df to avoid modifying the original
    result_df = df.copy()

    # For each period, we shift the hour and merge with the volume df
    for p in range(number_of_periods):
        # Compute the shifted hour
        # If you need to wrap around 24 hours:
        shifted_hour = (result_df['hour'] + p) % 24

        # Create a temporary dataframe to merge on month, weekday, shifted hour
        temp_merge_df = result_df[['month', 'weekday']].copy()
        temp_merge_df['hour_shifted'] = shifted_hour

        # Merge with the volume dataframe on month, weekday, and hour
        # Note: the volume df is assumed to have exactly these columns: month, weekday, hour, traffic, pedestrian
        merged = temp_merge_df.merge(volume, how='left',
                                     left_on=['month', 'weekday', 'hour_shifted'],
                                     right_on=['month', 'weekday', 'hour'])

        # After merge, we have the columns 'traffic' and 'pedestrian' from the volume dataframe
        # For each station s, we create duplicate columns
        for s in range(number_of_stations):
            traffic_col = f"traffic_volume_{s}_period_{p}"
            pedestrian_col = f"pedestrian_volume_{s}_period_{p}"

            # Assign the merged values
            result_df[traffic_col] = merged['traffic']
            result_df[pedestrian_col] = merged['pedestrian']

    return result_df

@timed_function
def assign_weather(df, weather, number_of_periods, features):
    """
    Assign weather features to the main dataframe based on shifted time periods.

    Parameters:
    - df (pd.DataFrame): Main dataframe containing at least 'dateTime'.
    - weather (pd.DataFrame): Weather dataframe containing 'dateTime' and weather features.
    - number_of_periods (int): Number of hourly periods to shift and merge.
    - features (list): List of weather feature column names to merge.

    Returns:
    - pd.DataFrame: Merged dataframe with weather features for each period.
    """
    df = df.copy()

    # Ensure 'dateTime' is datetime
    df['dateTime'] = pd.to_datetime(df['dateTime'], errors='coerce')
    weather['dateTime'] = pd.to_datetime(weather['dateTime'], errors='coerce')

    # Validate 'dateTime' conversion
    if df['dateTime'].isnull().any():
        raise ValueError("Some 'dateTime' values in df could not be converted to datetime.")
    if weather['dateTime'].isnull().any():
        raise ValueError("Some 'dateTime' values in weather could not be converted to datetime.")

    for p in range(number_of_periods):
        temp = weather.copy()

        # Shift the dateTime by p hours
        temp['dateTime'] = temp['dateTime'] + pd.Timedelta(hours=p)

        # Rename features to include the period
        rename_dict = {feature: f'{feature}_period_{p}' for feature in features}
        temp.rename(columns=rename_dict, inplace=True)

        # Merge with the main dataframe
        df = df.merge(
            temp,
            on=['dateTime'],
            how='left'
        )

    return df

def get_weather(df, selected_datetime):
    now = datetime.now()
    buffer_time = now - timedelta(days=6)

    start_date = (selected_datetime - timedelta(days=1))
    end_date = selected_datetime

    if selected_datetime < buffer_time:
        base_url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        base_url = "https://api.open-meteo.com/v1/forecast"

    weather = open_meteo_request(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        base_url=base_url,
    )
    weather = pd.DataFrame(weather)
    weather_features = ['temperature_2m', 'precipitation', 'snowfall', 'snow_depth', 'surface_pressure', 'cloud_cover']
    weather['dateTime'] = pd.to_datetime(weather['time'])
    weather.drop(columns=['time'], inplace=True)
    df = assign_weather(df, weather, 4, weather_features)
    return df

def transform(df):
    # Drop the unwanted columns
    drop_features = ['dateTime']
    df = df.drop(columns=drop_features, inplace=False)

    # Load the preprocessor
    preprocessor = load('data/inference/preprocessor.pkl')

    # Define the feature lists as used during preprocessing
    numerical_features = [
        'traffic_volume_0_period_0', 'traffic_volume_1_period_0', 'traffic_volume_2_period_0',
        'traffic_volume_0_period_1', 'traffic_volume_1_period_1', 'traffic_volume_2_period_1',
        'pedestrian_volume_0_period_0', 'pedestrian_volume_1_period_0', 'pedestrian_volume_2_period_0',
        'pedestrian_volume_0_period_1', 'pedestrian_volume_1_period_1', 'pedestrian_volume_2_period_1',
        'temperature_2m_period_0', 'precipitation_period_0', 'snowfall_period_0', 'snow_depth_period_0',
        'surface_pressure_period_0', 'cloud_cover_period_0', 'temperature_2m_period_1',
        'precipitation_period_1', 'snowfall_period_1', 'snow_depth_period_1',
        'surface_pressure_period_1', 'cloud_cover_period_1', 'temperature_2m_period_2',
        'precipitation_period_2', 'snowfall_period_2', 'snow_depth_period_2',
        'surface_pressure_period_2', 'cloud_cover_period_2', 'temperature_2m_period_3',
        'precipitation_period_3', 'snowfall_period_3', 'snow_depth_period_3',
        'surface_pressure_period_3', 'cloud_cover_period_3'
    ]

    categorical_features = [
        'AccidentType', 'AccidentInvolvingPedestrian', 'AccidentInvolvingBicycle',
        'AccidentInvolvingMotorcycle', 'RoadType', 'month', 'weekday', 'hour'
    ]

    # Transform the dataframe
    transformed = preprocessor.transform(df)

    # Get the one-hot encoded feature names for categorical variables
    cat_onehot_features = preprocessor.named_transformers_['cat'] \
        .named_steps['onehot'].get_feature_names_out(categorical_features)

    # Combine numerical and categorical feature names
    processed_features = numerical_features + list(cat_onehot_features)

    # Convert the transformed ndarray to a DataFrame with the appropriate column names
    df_transformed = pd.DataFrame(transformed, columns=processed_features, index=df.index)

    return df_transformed

def translate_columns(df):
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

    ACCIDENT_SEVERITY_MAPPING = {
        'as1': 'Accident with fatalities',
        'as2': 'Accident with severe injuries',
        'as3': 'Accident with light injuries',
        'as4': 'Accident with property damage',
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

    # Translate AccidentType
    df['AccidentTypeDesc'] = df['AccidentType'].map(ACCIDENT_TYPE_MAPPING)

    # Translate AccidentSeverityCategory
    df['AccidentSeverityDesc'] = df['AccidentSeverityCategory'].map(ACCIDENT_SEVERITY_MAPPING)

    # Translate RoadType
    df['RoadTypeDesc'] = df['RoadType'].map(ROAD_TYPE_MAPPING)

    # Translate Weekday
    df['WeekdayDesc'] = df['weekday'].map(WEEKDAY_MAPPING)

    # Handle unmapped values (if any)
    df['AccidentTypeDesc'] = df['AccidentTypeDesc'].fillna('Unknown')
    df['AccidentSeverityDesc'] = df['AccidentSeverityDesc'].fillna('Unknown')
    df['RoadTypeDesc'] = df['RoadTypeDesc'].fillna('Unknown')
    df['WeekdayDesc'] = df['WeekdayDesc'].fillna('Unknown')

    return df