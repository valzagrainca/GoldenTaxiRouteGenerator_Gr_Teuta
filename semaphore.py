import os
import pandas as pd
import json
from geopy.distance import geodesic
import requests

def read_csv_files(input_folder):
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        path = os.path.join(input_folder, file)
        dataframes[file] = pd.read_csv(path)
    return dataframes

def read_intersections_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data.get("intersections", [])

def find_nearest_intersection(point, intersections):
    """Find the nearest intersection to the given point."""
    nearest_intersection = None
    min_distance = float('inf')
    for intersection in intersections:
        distance = geodesic((point['Latitude'], point['Longitude']), (intersection['lat'], intersection['lng'])).meters
        if distance <= 200:  # Within 200 meters radius
            if distance < min_distance:
                nearest_intersection = intersection
                min_distance = distance
    return nearest_intersection

def find_road_name(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    
    response = requests.get(url, headers={"User-Agent": "AppName"})
    if response.status_code == 200:
        data = response.json()
    
        road_name = data.get('address', {}).get('road', 'Unknown Road')
        
        road_name = road_name.replace(' ', '_')
        return road_name
    else:
        print(f"Error fetching road name: {response.status_code}")
        return "Unknown_Road"
    
def parse_device_time(time_str):
    """Parse the time duration from a string in the format 'MM:SS.s'."""
    minutes, seconds = map(float, time_str.split(':'))
    return int(minutes * 60 + seconds)

def process_csv_files(csv_data, intersections, output_folder):
    route_intersections_data = [] 
    total_intersections = 0
    total_segments = 0
    total_time_seconds = 0
    counter=1
    
    for filename, df in csv_data.items():
        print(f"Processing {filename}...")

        # Convert DeviceDateTime from 'MM:SS.s' format to total seconds
        df['DeviceTimeSeconds'] = df['DeviceDateTime'].apply(parse_device_time)

        # Existing preprocessing steps
        df = df[~((df['Di1'] == 0) & (df['Di3'] == 0))]
        df = df[~((df['Di1'] == 0) & (df['Di3'] == 1))]
        df['route_change'] = df['Di2'].diff().ne(0).cumsum()
        df_with_passengers = df[df['Di2'] == 1]

        if df_with_passengers.empty:
            print("No routes with passengers were found.")
            continue

        routes = df_with_passengers.groupby('route_change')
        all_segments=[]
        for route_id, route_data in routes:
            segments = []
            previous_intersection = None
            previous_time = None
            for index, row in route_data.iterrows():
                point = {'Latitude': row['Latitude'], 'Longitude': row['Longitute']}
                nearest_intersection = find_nearest_intersection(point, intersections)
                if nearest_intersection:
                    # Increment total intersections
                    current_time = row['DeviceTimeSeconds']
                    if nearest_intersection != previous_intersection:
                        if previous_intersection:
                            total_intersections += 2
                            total_segments += 1
                            # Calculate time spent in segment
                            time_spent = current_time - previous_time if previous_time is not None else 0
                            # Accumulate total time in seconds
                            total_time_seconds += time_spent
                            road_name = find_road_name(row['Latitude'], row['Longitute'])
                            segment_info = f"{previous_intersection['id']} {nearest_intersection['id']} {road_name}_{previous_intersection['id']}_{nearest_intersection['id']}"
                            segment_info_details = f"{previous_intersection['id']} {nearest_intersection['id']} {road_name}_{previous_intersection['id']}_{nearest_intersection['id']} {time_spent}"
                            segments.append(segment_info)
                            all_segments.append(segment_info_details)
                        previous_intersection = nearest_intersection
                        previous_time = current_time

            if segments:
                route_intersections_data.append((route_id, segments))

        # Output logic to write totals and segments to the file...
        output_file = os.path.join(output_folder, f"route_segments_summary_{counter}.txt")
        with open(output_file, "w") as file:
            # Write the totals as the first row
            file.write(f"{total_time_seconds} {total_intersections} {total_segments} {len(route_intersections_data)} 100\n")
            for segment in all_segments:
                    file.write(f"{segment}\n")
            for route_id, segments in route_intersections_data:
                file.write(f"{len(segments)+1}\t")
                for segment in segments:
                    file.write(f"{segment}  ")
                file.write(f"{segment}\n")
        counter+=1
                


def main():
    global intersections_list
    print("Welcome to the CSV reader")

    input_folder = input("Please enter the path to the input folder: ")
    output_folder = input("Please enter the path to the output folder: ")

    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} does not exist.")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    csv_data = read_csv_files(input_folder)
    file_path_json = "../../Desktop/semm/input_pr.json"
    intersections_list = read_intersections_from_file(file_path_json)
    process_csv_files(csv_data, intersections_list, output_folder)

    print("Operation completed.")

if __name__ == "__main__":
    main()
