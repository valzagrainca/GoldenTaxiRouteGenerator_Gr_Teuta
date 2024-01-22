# -*- coding: utf-8 -*-
import os
import pandas as pd
from datetime import datetime
import osmnx as ox  # Import osmnx library for OSM data
from geopy.exc import GeocoderTimedOut


def read_csv_files(input_folder):
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        path = os.path.join(input_folder, file)
        dataframes[file] = pd.read_csv(path)
    return dataframes


def intersection_finder(lat, lon, df, i):
    try:
        # Create a network graph of the area around the given latitude and longitude
        graph = ox.graph_from_point((lat, lon), dist=100, network_type='all')  # Use dist parameter

        # Get all nodes (intersections) in the graph
        nodes = list(graph.nodes())

        # Find the nearest intersection to the provided coordinates
        nearest_node = ox.distance.nearest_nodes(graph, lon, lat)

        # Find the edges (roads) connected to the nearest node
        edges = list(graph.edges(nearest_node, keys=True))

        # Try to get the 'name' attribute of the first edge if it exists, otherwise use 'unknown_road'
        if edges:
            road_name = graph.edges[edges[0]].get('name', 'unknown_road')
        else:
            road_name = 'unknown_road'

        # Check if the road name is 'unknown_road,' and skip segment creation
        if road_name == 'unknown_road':
            return None

        # Calculate time_diff using the previous and current timestamps
        time_diff = (df.iloc[i]['DeviceDateTime'] - df.iloc[i - 1]['DeviceDateTime']).total_seconds()

        # Construct the segment with start node, end node, road name including numbers, and time
        segment = f"{i - 1} {i} {road_name.replace(' ', '_')}_{i - 1}_{i} {time_diff:.2f}"

        return segment
    except:
        return None  # Return None in case of an error or no edges


def process_csv_files(csv_data, output_folder):
    csv_file_counter = 1
    all_routes_summary = ""
    previous_road_name = None

    for filename, df in csv_data.items():
        print(f"Processing {filename}...")
        df['DeviceDateTime'] = pd.to_datetime(df['DeviceDateTime'], format='%M:%S.%f')
        df = df[df['Di2'] == 1]  # Assuming Di2 = 1 indicates relevant data

        # Creating the start time (00:00:00) and end time (23:59:59)
        start_time = datetime.combine(df['DeviceDateTime'].iloc[0].date(), datetime.min.time())
        end_time = datetime.combine(df['DeviceDateTime'].iloc[0].date(), datetime.max.time())

        # Calculating the total duration from 00:00 until the last recorded time
        total_duration_seconds = (df['DeviceDateTime'].iloc[-1] - start_time).total_seconds()

        segments = []

        for i in range(1, len(df)):
            # Use the intersection_finder function to get the segment
            segment = intersection_finder(df.iloc[i - 1]['Latitude'], df.iloc[i - 1]['Longitude'], df, i)

            # Check if segment is None (unknown_road), and skip if so
            if segment is not None:
                # Check if the road name has changed
                if previous_road_name != segment.split()[-2]:
                    all_routes_summary += segment.split()[-2] + ' '
                    previous_road_name = segment.split()[-2]
                segments.append(segment)

        # Write segments and overall summary to a file
        output_file_path = os.path.join(output_folder, f'output_solution_2_file_{csv_file_counter}.txt')
        with open(output_file_path, 'w') as file:
            file.write(f"{int(total_duration_seconds)} {len(df)} {len(segments)} {csv_file_counter} 100\n")
            for seg in segments:
                file.write(f"{seg}\n")  # List of segments in separate lines
            file.write(str(len(segments)) + " " + all_routes_summary.rstrip() + '\n\n')  # Write the summary of all routes without trailing space

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
