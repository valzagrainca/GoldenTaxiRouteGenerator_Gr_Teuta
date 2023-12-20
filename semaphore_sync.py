import os
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

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
            road_name = location.raw['address']['road']
            return road_name.replace(' ', '_')
        else:
            return None
    except (GeocoderTimedOut, Exception):
        return None

def process_csv_files(csv_data, output_folder):
    csv_file_counter = 1

    for filename, df in csv_data.items():
        print(f"Processing {filename}...")

        all_routes_info = ""

        df = df[~((df['Di1'] == 0) & (df['Di3'] == 0))]
        df = df[~((df['Di1'] == 0) & (df['Di3'] == 1))]

        # Identify the start and end of each route
        df['route_change'] = df['Di2'].diff().ne(0).cumsum()

        df_with_passengers = df[df['Di2'] == 1]

        if df_with_passengers.empty:
            print("No routes with passengers were found.")
            continue

        routes = df_with_passengers.groupby('route_change')

        for _, route_data in routes:
            route_addresses = route_data.apply(lambda row: location_finder(row['Latitude'], row['Longitute']), axis=1).dropna()
            if route_addresses.empty:
                continue

            unique_addresses = route_addresses.unique()
            filtered_addresses = [unique_addresses[i] for i in range(len(unique_addresses)) if i == 0 or unique_addresses[i] != unique_addresses[i-1]]
            location_count = len(filtered_addresses)
            route_description = ' '.join(filtered_addresses)

            all_routes_info += f"{location_count} {route_description}\n"

        if all_routes_info:
            output_file_path = os.path.join(output_folder, f'route_{csv_file_counter}.txt')
            with open(output_file_path, 'w') as file:
                file.write(all_routes_info)
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
