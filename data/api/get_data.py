from modules.ckan_api import get_ckan_data
from modules.open_meteo_api import open_meteo_request
import sys
import os
import csv
from tqdm import tqdm

raw_folder_path = os.path.join(os.path.dirname(__file__), '../raw')
os.makedirs(raw_folder_path, exist_ok=True)

def main():
    total_size_gb = 5.7  # Adjust the total size if necessary
    confirmation = input(
        f"You are about to download the entire project data, including CKAN datasets and weather data, "
        f"which requires approximately {total_size_gb} GB of free disk space.\n"
        "Are you sure you want to proceed? (y/n): "
    ).strip().lower()

    if confirmation == 'y':
        print("Starting the download process...")
        # ckan_success = ckan_data_download()
        meteo_success = open_meteo_data_download()

        """if ckan_success and meteo_success:
            print("\nAll datasets were downloaded successfully.")
        else:
            print("\nSome datasets failed to download.")
            if not ckan_success:
                print("Some CKAN datasets failed to download.")
            if not meteo_success:
                print("Open Meteo data failed to download.")
    else:
        print("Download process canceled.")"""


def ckan_data_download() -> bool:
    """
    Function to download datasets using the CKAN API.

    Returns:
        bool: True if all datasets were downloaded successfully, False otherwise.
    """

    # Dataset IDs
    dataset_ids = {
        'accidents': '1ef58626-827b-42c5-addb-36f39d49ff98',
        'traffic_volume': 'f80fd59a-e52a-4caa-8b39-287662c0c517',
        'pedestrian_volume': 'b5ae1507-d930-4448-a6d0-e08cde338d2b'
    }

    # Track the number of successfully downloaded datasets
    downloaded_datasets = 0
    failed_datasets = []

    for dataset_name, dataset_id in dataset_ids.items():
        print(f"\nDownloading dataset: {dataset_name} (ID: {dataset_id})")
        try:
            filepath = get_ckan_data(dataset_id)
            if filepath:
                print(f"Successfully downloaded and saved: {filepath}")
                downloaded_datasets += 1
            else:
                raise ValueError(f"Dataset '{dataset_name}' failed to download.")
        except Exception as e:
            print(f"Error while downloading '{dataset_name}': {e}")
            failed_datasets.append(dataset_name)

    # Summary of the process
    print("\nDownload process completed.")
    print(f"Successfully downloaded datasets: {downloaded_datasets}/{len(dataset_ids)}")
    if failed_datasets:
        print("The following datasets failed to download:")
        for failed in failed_datasets:
            print(f"- {failed}")

    success = downloaded_datasets == len(dataset_ids)
    return success


def open_meteo_data_download() -> bool:
    start_date = "2012-01-01"
    end_date = "2023-12-31"
    base_url = "https://archive-api.open-meteo.com/v1/archive"

    data = open_meteo_request(
        start_date=start_date,
        end_date=end_date,
        base_url=base_url,
    )

    if data is None:
        print("Failed to retrieve data.")
        return False

    try:
        total_rows = len(next(iter(data.values())))
        csv_file_path = os.path.join('..', 'raw', 'weather_data.csv')
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            writer.writeheader()
            # Transpose rows by zipping dictionary values
            for row in tqdm(zip(*data.values()), total=total_rows, desc="Saving data"):
                writer.writerow(dict(zip(data.keys(), row)))
        print(f"Weather data saved successfully at {csv_file_path}.")
        success = True
    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        return False


    if success:
        print("Weather data downloaded successfully.")
    else:
        print("Failed to download weather data.")
    return success


if __name__ == '__main__':
    main()
