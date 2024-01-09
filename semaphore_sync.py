# -*- coding: utf-8 -*-
import os
import pandas as pd
import math
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlon, dlat = lon2_rad - lon1_rad, lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def read_csv_files(input_folder):
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        path = os.path.join(input_folder, file)
        dataframes[file] = pd.read_csv(path)
    return dataframes

def location_finder(lat, lon):
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse((lat, lon), exactly_one=True)
        if location and 'road' in location.raw.get('address', {}):
            return location.raw['address']['road'].replace(' ', '_')
        else:
            return None
    except (GeocoderTimedOut, Exception):
        return None

def process_csv_files(csv_data, output_folder):
    csv_file_counter = 1
    all_routes_summary = ""

    for filename, df in csv_data.items():
        print(f"Processing {filename}...")
        df['DeviceDateTime'] = pd.to_datetime(df['DeviceDateTime'], format='%M:%S.%f')
        df = df[df['Di2'] == 1]  # Assuming Di2 = 1 indicates relevant data

        # Krijimi i kohës fillestare (00:00:00) dhe kohës së përfundimit (23:59:59)
        start_time = datetime.combine(df['DeviceDateTime'].iloc[0].date(), datetime.min.time())
        end_time = datetime.combine(df['DeviceDateTime'].iloc[0].date(), datetime.max.time())

        # Llogaritja e kohëzgjatjes totale që nga ora 00:00 deri në kohën e fundit të regjistruar
        total_duration_seconds = (df['DeviceDateTime'].iloc[-1] - start_time).total_seconds()

        segments = []
        road_names = []  # To store the road names with indices
        for i in range(1, len(df)):
            distance = haversine(df.iloc[i-1]['Latitude'], df.iloc[i-1]['Longitude'], df.iloc[i]['Latitude'], df.iloc[i]['Longitude'])
            if distance > 0.05:  # Threshold for a new segment
                time_diff = (df.iloc[i]['DeviceDateTime'] - df.iloc[i-1]['DeviceDateTime']).total_seconds()
                if time_diff > 0:  # Exclude stationary points
                    road_name = location_finder(df.iloc[i-1]['Latitude'], df.iloc[i-1]['Longitude'])
                    segments.append(f"{i-1} {i} {road_name}_{i-1}_{i} {time_diff:.2f}")
                    road_names.append(f"{road_name}_{i - 1}_{i}")  # Append road name with indices

        # Adding to the overall summary
        all_routes_summary += f"{len(segments)} "  # Numri i segmenteve
        all_routes_summary += ' '.join(road_names) + '\n\n'  # Shto vetëm emrat e rrugëve me indekse

        # Write segments and overall summary to a file
        output_file_path = os.path.join(output_folder, f'route_{csv_file_counter}.txt')
        with open(output_file_path, 'w') as file:
            file.write(f"{int(total_duration_seconds)} {len(df)} {len(segments)} {csv_file_counter} 100\n")
            for seg in segments:
                file.write(f"{seg}\n")  # Lista e segmenteve në rreshta të veçantë
            file.write(all_routes_summary)  # Shkruaj përmbledhjen e të gjitha shtigjeve

        csv_file_counter += 1

def main():
    print("Welcome to the CSV reader")
    input_folder = input("Please enter the path to the input folder: ")
    output_folder = input("Please enter the path to the output folder: ")

    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} does not exist.")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    csv_data = read_csv_files(input_folder)
    process_csv_files(csv_data, output_folder)
    print("Operation completed.")

if __name__ == "__main__":
    main()