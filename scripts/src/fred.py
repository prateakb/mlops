import requests
import pandas as pd
import time
import os

# FRED API key
fred_api_key = 'bf783fb798c8f5e699c3290081b8e9f2'

# Function to get a list of releases from FRED
def get_fred_releases():
    endpoint = "https://api.stlouisfed.org/fred/releases"
    payload = {
        'file_type': 'json',
        'api_key': fred_api_key
    }
    response = requests.get(endpoint, params=payload)
    return response.json()

# Function to get a list of series within a release
def get_fred_series(release_id):
    endpoint = f"https://api.stlouisfed.org/fred/release/series"
    payload = {
        'release_id': release_id,
        'file_type': 'json',
        'api_key': fred_api_key
    }
    response = requests.get(endpoint, params=payload)

    try:
        json_data = response.json()
        if 'series' in json_data:
            return json_data['series']
        elif 'seriess' in json_data:
            return json_data['seriess']
        else:
            print(f"No series found for release ID {release_id}")
            return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON for release ID {release_id}: {e}")
        return e


# Function to get data points for a series
def get_fred_series_data(series_id):
    endpoint = f"https://api.stlouisfed.org/fred/series/observations"
    payload = {
        'series_id': series_id,
        'file_type': 'json',
        'api_key': fred_api_key
    }
    response = requests.get(endpoint, params=payload)
    return response.json()

# Function to convert FRED JSON response to pandas DataFrame
def fred_json_to_dataframe(json_data, release_name, series_name):
    if 'observations' not in json_data:
        print(f"Warning: Could not retrieve data for series: {series_name} (Release: {release_name})")
        return pd.DataFrame(columns=['date', 'value', 'release', 'series'])

    observations = json_data['observations']
    data = [{'date': obs['date'], 'value': obs['value']} for obs in observations]

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['release'] = release_name
    df['series'] = series_name
    return df

release_folder = os.getcwd()

all_data = pd.DataFrame({'date': [], 'value': [], 'release': [], 'series': []})
# Retrieve a list of releases from FRED
releases = get_fred_releases()
#print(type(releases), "\n", releases)
releases_list = releases['releases']

# Loop through all the releases
for release in releases_list:
    print(f"Processing release: {release['name']} (ID: {release['id']})")

    # Get the series within the release
    series_list = get_fred_series(release['id'])

    # Loop through series in the release
    for series in series_list:
        print(f"Processing series: {series['title']} (ID: {series['id']})")

        # Check if data already exists for this release and series
        series_filename = f"{release['name']}_{series['title']}.parquet"
        series_path = os.path.join(release_folder, series_filename)
        if os.path.exists(series_path):
            print(f"Data already exists for release {release['name']}, series {series['title']}")
            continue

        # Get the data points for the series
        series_data = get_fred_series_data(series['id'])
        # Add a delay between API requests to avoid rate limits
        time.sleep(1)

        # Process the data
        data_df = fred_json_to_dataframe(series_data, release['name'], series['title'])

        if not data_df.empty:
            # Append the data to the main DataFrame
            all_data = all_data.append(data_df, ignore_index=True)
            print("Data retrieved for this series:")
            print(data_df.head())

            # Save the data to a file
            data_filename = f"{series['title']}.parquet"
            data_path = os.path.join(release_folder, data_filename)
            data_df.to_parquet(data_path, index=False)
        else:
            print("No data retrieved for this series.")

        # Add a delay between API requests to avoid rate limits
        time.sleep(1)

