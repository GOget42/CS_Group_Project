from modules.ckan_api import get_data


def main():
    """
    Main function to download datasets using the CKAN API.
    Prompts the user for confirmation before downloading multiple datasets.
    """

    # Dataset IDs
    dataset_ids = {
        'accidents': '1ef58626-827b-42c5-addb-36f39d49ff98',
        'traffic_volume': 'f80fd59a-e52a-4caa-8b39-287662c0c517',
        'pedestrian_volume': 'b5ae1507-d930-4448-a6d0-e08cde338d2b'
    }

    # Notify the user about the size requirement
    total_size_gb = 5.7  # Example total size in GB, replace with actual size if known
    confirmation = input(
        f"You are about to download the entire project data, which requires approximately {total_size_gb} GB of free disk space.\n"
        "Are you sure you want to proceed? (y/n): "
    ).strip().lower()

    if confirmation == 'y':
        print("Starting the download process...")

        # Track the number of successfully downloaded datasets
        downloaded_datasets = 0
        failed_datasets = []

        for dataset_name, dataset_id in dataset_ids.items():
            print(f"\nDownloading dataset: {dataset_name} (ID: {dataset_id})")
            try:
                filepath = get_data(dataset_id)
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
    else:
        print("Download process canceled.")


if __name__ == '__main__':
    main()
