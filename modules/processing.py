import time
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from tqdm.notebook import tqdm
from datetime import timedelta


def timed_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.6f} seconds")
        return result
    return wrapper

@timed_function
def assign_closest_volume(A, B, name, number_of_stations, number_of_periods):
    A = A.copy()
    errors = 0

    volume_columns = [f'{name}_volume_{station}_period_{period}'
                      for period in range(number_of_periods)
                      for station in range(number_of_stations)]
    for col in volume_columns:
        A[col] = np.full(len(A), np.nan, dtype='float64')

    B_grouped = B.groupby('dateTime')

    for period in tqdm(range(number_of_periods), desc="Processing periods"):
        adjusted_timestamps = A['dateTime'] - pd.to_timedelta(period, unit='h')

        unique_timestamps = set(adjusted_timestamps.unique())
        valid_timestamps = unique_timestamps.intersection(B_grouped.groups.keys())

        if len(valid_timestamps) == 0:
            errors += 1
            continue

        timestamp_to_indices = adjusted_timestamps.groupby(adjusted_timestamps).groups

        for timestamp in tqdm(valid_timestamps, desc=f"Period {period}: Processing timestamps", leave=False):
            idxs = timestamp_to_indices.get(timestamp, [])

            B_filtered = B_grouped.get_group(timestamp)
            if B_filtered.empty:
                errors += 1
                continue

            kd_tree = cKDTree(B_filtered[['x', 'y']].values)

            points = A.loc[idxs, ['x', 'y']].values

            distances, indices = kd_tree.query(points, k=number_of_stations)

            if indices.ndim == 1:
                indices = indices[:, np.newaxis]

            volumes = B_filtered['volume'].values[indices]

            for station in range(number_of_stations):
                col_name = f'{name}_volume_{station}_period_{period}'
                A.loc[idxs, col_name] = volumes[:, station]

    print(f'{A.isna().sum().sum()} values are nan and thus set to 0.')
    A[volume_columns] = A[volume_columns].fillna(0)
    print(f'Number of errors encountered: {errors}')

    return A