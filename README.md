# CSV Reader & Intersection Finder and Taxi Route Generator based on data from Golden Taxi company to synchronize traffic lights in Pristina

This Python script automates the process of reading CSV files containing geolocation data, identifying routes with passengers, calculating route segments between intersections within a specified time range, and summarizing these routes and segments. It uses external APIs and libraries to enrich the data with road names and intersection proximity.

## Features

- Reads multiple CSV files from a specified directory.
- Filters and preprocesses data based on specific conditions (e.g., time range, presence of passengers).
- Identifies intersections from a JSON file and finds the nearest intersection to given points.
- Calculates average, minimum, and maximum time spent in each segment between intersections.
- Generates detailed summary files for each CSV processed, including route segments, times, and intersection data.
- Utilizes the `geopy` library for geodesic distance calculations and `requests` for reverse geocoding to find road names.

## Installation

Ensure you have Python installed on your system. This script has been tested with Python 3.8. Additionally, you will need to install the required dependencies:

```bash
pip install pandas geopy requests
````
## Installation

# Prepare Your Data:

Ensure your CSV files are located in a single input directory. These files should contain columns for latitude, longitude, device date-time, and other relevant flags (e.g., Di1, Di2, Di3).
Prepare a JSON file (input_pr.json) containing intersection data in the specified format.

# Set Up Directories:

Specify the path to your input folder containing the CSV files.
Specify the path to your output folder where the summary files will be saved. If the output folder does not exist, it will be created automatically.

# Run the Script:

Navigate to the script's directory.
Run the script using Python by entering the following command in your terminal or command prompt:

```
python semaphore.py
```

Follow the prompts to enter the paths for your input and output directories. For example:

```
Please enter the path to the input folder: path/to/input/folder
Please enter the path to the output folder: path/to/output/folder
```

The script will process each CSV file in the input directory, calculate the relevant route segment details, and generate summary files in the output directory.

# Contributing

Contributions to improve this script are welcome. Please feel free to fork the repository and submit a pull request with your enhancements.

# License

This project is open-source and available under the [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/valzagrainca/GoldenTaxiRouteGenerator_Gr_Teuta/blob/main/LICENSE.txt).



