import requests
from typing import Optional, Dict, Any
import os
from tqdm import tqdm

def ckan_request(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: str = 'https://opendata.swiss/api/3/action/'
) -> Optional[Dict[str, Any]]:
    """
    Makes a request to the CKAN API and returns the result.

    Parameters:
    - base_url (str): The base URL of the CKAN API.
    - action (str): The API action to perform (e.g., 'package_list', 'package_show').
    - params (dict, optional): A dictionary of query parameters.

    Returns:
    - dict: The JSON response if successful, otherwise None.
    """
    url = f"{base_url}{action}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            print()
            return data['result']
        else:
            print(f"API Error: {data.get('error', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        print(f"HTTP Error: {e}")
        return None


def get_data(id: str) -> Optional[str]:
    """
    Fetches a dataset from the CKAN API by its ID, downloads all available CSV files,
    and saves them to the 'raw' directory under their English or German title names.

    Parameters:
    - id (str): The dataset ID to fetch.

    Returns:
    - Optional[str]: The name of the last saved file if successful, otherwise None.

    Raises:
    - FileNotFoundError: If the 'raw' directory does not exist.
    - KeyError: If the dataset does not contain the expected keys like 'resources'.
    - ValueError: If no CSV resource is found in the dataset.
    - requests.RequestException: If an HTTP request fails.
    """
    base_url = 'https://opendata.swiss/api/3/action/'
    action = 'package_show'
    params = {"id": id}

    try:
        # Call the CKAN API
        result = ckan_request(action=action, params=params, base_url=base_url)
        if not result:
            raise ValueError(f"No result returned for dataset ID: {id}")

        # Extract resources
        resources = result.get('resources', [])
        if not resources:
            raise ValueError(f"No resources found in dataset ID: {id}")

        raw_dir = "../raw"
        if not os.path.exists(raw_dir):
            raise FileNotFoundError(f"Directory '{raw_dir}' does not exist.")

        # Process each resource
        last_saved_file = None
        for idx, resource in enumerate(tqdm(resources, desc="Processing resources")):
            if resource['url'].endswith('.csv'):
                # Generate the filename
                filename = resource['title'].get('en') or resource['title'].get('de') or f"{id}_{idx}.csv"
                filepath = os.path.join(raw_dir, filename)

                # Download the file with progress
                response = requests.get(resource['url'], stream=True)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                with open(filepath, 'wb') as file, tqdm(
                    desc=f"Downloading {filename}",
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024
                ) as bar:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                        bar.update(len(chunk))

                print(f"File saved as: {filepath}")
                last_saved_file = filepath

        if not last_saved_file:
            raise ValueError(f"No CSV resource found in dataset ID: {id}")

        return last_saved_file

    except requests.RequestException as e:
        print(f"HTTP error occurred while accessing the API: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data error: {e}")
    except FileNotFoundError as e:
        print(f"File system error: {e}")

    return None
