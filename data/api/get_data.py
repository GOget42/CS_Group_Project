from modules.ckan_api import get_ckan_data
from modules.open_meteo_api import get_open_meteo_data


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
    """Download weather data from Open Meteo API and save it to a CSV file.

    Returns:
        bool: True if data was downloaded successfully, False otherwise.
    """
    start_date = "2012-01-01"
    end_date = "2023-12-31"
    success = get_open_meteo_data(start_date, end_date)
    if success:
        print("Weather data downloaded successfully.")
    else:
        print("Failed to download weather data.")
    return success


if __name__ == '__main__':
    main()
