from datetime import date, datetime
import os
import json
import requests
import csv
from typing import Dict, Any, Optional, List, Tuple
from tqdm import tqdm
from config import TRACKER_PATH


def load_tracker_data() -> Dict[str, Any]:
    """Load the tracker data from the JSON file.

    Returns:
        Dict[str, Any]: The tracker data.
    """
    if not os.path.exists(TRACKER_PATH):
        # Return default tracker data
        return {
            "daily": {"date": date.today().isoformat(), "requests": 0},
            "hourly": {"datetime": datetime.now().strftime("%Y-%m-%d %H"), "requests": 0},
            "minutely": {"datetime": datetime.now().strftime("%Y-%m-%d %H:%M"), "requests": 0}
        }
    try:
        with open(TRACKER_PATH, "r") as file:
            tracker_data = json.load(file)
        return tracker_data
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading tracker file: {e}")
        # Return default tracker data
        return {
            "daily": {"date": date.today().isoformat(), "requests": 0},
            "hourly": {"datetime": datetime.now().strftime("%Y-%m-%d %H"), "requests": 0},
            "minutely": {"datetime": datetime.now().strftime("%Y-%m-%d %H:%M"), "requests": 0}
        }


def save_tracker_data(tracker_data: Dict[str, Any]) -> None:
    """Save the tracker data to the JSON file.

    Args:
        tracker_data (Dict[str, Any]): The tracker data to save.
    """
    try:
        with open(TRACKER_PATH, "w") as file:
            json.dump(tracker_data, file)
    except IOError as e:
        print(f"Error writing to tracker file: {e}")


def get_tracker_data() -> Dict[str, Any]:
    """Load the tracker data and reset counts if time periods have changed.

    Returns:
        Dict[str, Any]: The current tracker data.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)

    tracker_data = load_tracker_data()

    # Get current date and times
    current_date = date.today().isoformat()
    current_hour = datetime.now().strftime("%Y-%m-%d %H")
    current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Flag to check if data has changed
    data_changed = False

    # Reset daily requests if date has changed
    if tracker_data["daily"]["date"] != current_date:
        tracker_data["daily"] = {"date": current_date, "requests": 0}
        print(f"Daily tracker reset for a new day: {current_date}")
        data_changed = True

    # Reset hourly requests if hour has changed
    if tracker_data["hourly"]["datetime"] != current_hour:
        tracker_data["hourly"] = {"datetime": current_hour, "requests": 0}
        print(f"Hourly tracker reset for a new hour: {current_hour}")
        data_changed = True

    # Reset minutely requests if minute has changed
    if tracker_data["minutely"]["datetime"] != current_minute:
        tracker_data["minutely"] = {"datetime": current_minute, "requests": 0}
        print(f"Minutely tracker reset for a new minute: {current_minute}")
        data_changed = True

    # Save tracker data if any changes were made
    if data_changed:
        save_tracker_data(tracker_data)

    return tracker_data


def update_tracker(amount: int) -> None:
    """Update the tracker by incrementing the request counts.

    Args:
        amount (int): The number of requests to add.
    """
    tracker_data = get_tracker_data()

    # Update the counts
    tracker_data["daily"]["requests"] += amount
    tracker_data["hourly"]["requests"] += amount
    tracker_data["minutely"]["requests"] += amount

    save_tracker_data(tracker_data)


def check_tracker(number_of_requests: int) -> Tuple[bool, Optional[str]]:
    """Check if the number of requests can be made without exceeding the limits.

    Args:
        number_of_requests (int): The number of requests to check.

    Returns:
        Tuple[bool, Optional[str]]: (True, None) if requests can be made,
            (False, limit_name) if limit exceeded.
    """
    tracker_data = get_tracker_data()

    daily_remaining = 10000 - tracker_data["daily"]["requests"]
    hourly_remaining = 5000 - tracker_data["hourly"]["requests"]
    minutely_remaining = 600 - tracker_data["minutely"]["requests"]

    if number_of_requests > daily_remaining:
        return False, "daily"
    elif number_of_requests > hourly_remaining:
        return False, "hourly"
    elif number_of_requests > minutely_remaining:
        return False, "minutely"
    else:
        return True, None


def open_meteo_request(
    start_date: str,
    end_date: str,
    latitude: float = 47.36667,
    longitude: float = 8.55,
    hourly: Optional[List[str]] = None,
    timezone: str = 'Europe/Berlin',
    temperature_unit: str = 'celsius',
    windspeed_unit: str = 'kmh',
    precipitation_unit: str = 'mm',
    base_url: str = "https://archive-api.open-meteo.com/v1/archive"
) -> Optional[Dict[str, Any]]:
    """Send a request to the Open Meteo API and return the data.

    Args:
        start_date (str): The start date for the data retrieval in YYYY-MM-DD format.
        end_date (str): The end date for the data retrieval in YYYY-MM-DD format.
        latitude (float, optional): The latitude coordinate. Defaults to 47.36667.
        longitude (float, optional): The longitude coordinate. Defaults to 8.55.
        hourly (List[str], optional): List of hourly variables to request. Defaults to None.
        timezone (str, optional): The timezone for the data. Defaults to 'Europe/Berlin'.
        temperature_unit (str, optional): The unit for temperature. Defaults to 'celsius'.
        windspeed_unit (str, optional): The unit for wind speed. Defaults to 'kmh'.
        precipitation_unit (str, optional): The unit for precipitation. Defaults to 'mm'.
        base_url (str, optional): The base URL for the Open Meteo API. Defaults to 'https://archive-api.open-meteo.com/v1/archive'.

    Returns:
        Optional[Dict[str, Any]]: The data retrieved from the API, or None if an error occurred.
    """

    allowed, limit_name = check_tracker(number_of_requests=1)
    if not allowed:
        print(f"Open Meteo API {limit_name} limit reached!")
        return None

    update_tracker(amount=1)

    if hourly is None:
        hourly = ["temperature_2m", "precipitation", "snowfall", "snow_depth", "surface_pressure", "cloud_cover"]

    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': ','.join(hourly),
        'timezone': timezone,
        'temperature_unit': temperature_unit,
        'windspeed_unit': windspeed_unit,
        'precipitation_unit': precipitation_unit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

        if 'hourly' not in result:
            print("No 'hourly' data found in the response.")
            return None

        data = result['hourly']
        return data

    except requests.RequestException as e:
        print(f"HTTP Error: {e}")
        return None


def get_open_meteo_data(
        start_date: str = "2012-01-01",
        end_date: str = "2012-01-02"
) -> bool:
    """Retrieve data from Open Meteo API and save it to a CSV file.

    Args:
        start_date (str, optional): The start date in 'YYYY-MM-DD' format.
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.

    Returns:
        bool: True if data was successfully retrieved and saved, False otherwise.
    """
    data = open_meteo_request(start_date=start_date, end_date=end_date)

    if data is None:
        print("Failed to retrieve data.")
        return False

    try:
        total_rows = len(next(iter(data.values())))
        # Save the CSV file in the same directory as this script
        csv_file_path = os.path.join('..', 'raw', 'weather_data.csv')
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            writer.writeheader()
            # Transpose rows by zipping dictionary values
            for row in tqdm(zip(*data.values()), total=total_rows, desc="Saving data"):
                writer.writerow(dict(zip(data.keys(), row)))
        print(f"Weather data saved successfully at {csv_file_path}.")
        return True
    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        return False
