import csv
import datetime
import logging
import os
from typing import List, Dict

import requests

# Constants
API_BASE_URL = "https://api.weather.gc.ca/collections/climate-daily/items"
CSV_FILENAME = "/Users/simon/Desktop/Areas/TKS/Focus 1 - RL/IRL-RL Application/Script/Data Management/toronto_weather_2024.csv"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_weather_csv(filename: str) -> None:
    logging.info('Updating weather')
    try:
        existing_data = read_csv(filename)
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return
    except csv.Error as e:
        logging.error(f"Error reading CSV: {e}")
        return

    if not existing_data:
        logging.info("No existing data found.")
        return

    try:
        latest_valid_date = get_latest_valid_date(existing_data)
    except ValueError as e:
        logging.error(f"Error getting latest valid date: {e}")
        return

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    fetch_start_date = latest_valid_date + datetime.timedelta(days=1)

    if fetch_start_date > yesterday:
        logging.info(f"Data is up to date. Latest valid date: {latest_valid_date}")
        return

    new_data = fetch_new_data(fetch_start_date, existing_data[0]['Climate ID'])

    if not new_data:
        logging.info("No new data to add.")
        return

    updated_data = [row for row in existing_data if parse_date(row['Date/Time']) < fetch_start_date] + new_data
    if input(f'Add {len(new_data)} new records? (Type "no" to cancel): ').lower() == "no":
        return

    write_csv(filename, updated_data)
    logging.info(f"Updated {filename} with {len(new_data)} new records.")

def read_csv(filename: str) -> List[Dict]:
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def parse_date(date_str: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return datetime.date.max

def get_latest_valid_date(data: List[Dict]) -> datetime.date:
    if not data:
        raise ValueError("Data is empty, cannot find latest date.")
    
    valid_dates = [parse_date(row['Date/Time']) for row in data if any(row[key].strip() for key in row if key != 'Date/Time')]
    
    if not valid_dates:
        raise ValueError("No valid dates found in the data.")
    
    return max(valid_dates)

def format_api_data(item: Dict) -> Dict:
    props = item['properties']
    return {
        "Longitude (x)": item['geometry']['coordinates'][0],
        "Latitude (y)": item['geometry']['coordinates'][1],
        "Station Name": props['station_name'],
        "Climate ID": props['climate_identifier'],
        "Date/Time": props['date'],
        "Year": props['date'].split('-')[0],
        "Month": props['date'].split('-')[1],
        "Day": props['date'].split('-')[2],
        "Data Quality": props.get('quality', ''),
        "Max Temp (°C)": props.get('max_temperature', ''),
        "Max Temp Flag": props.get('max_temperature_flag', ''),
        "Min Temp (°C)": props.get('min_temperature', ''),
        "Min Temp Flag": props.get('min_temperature_flag', ''),
        "Mean Temp (°C)": props.get('mean_temperature', ''),
        "Mean Temp Flag": props.get('mean_temperature_flag', ''),
        "Heat Deg Days (°C)": props.get('heat_degree_days', ''),
        "Heat Deg Days Flag": props.get('heat_degree_days_flag', ''),
        "Cool Deg Days (°C)": props.get('cool_degree_days', ''),
        "Cool Deg Days Flag": props.get('cool_degree_days_flag', ''),
        "Total Rain (mm)": props.get('total_rainfall', ''),
        "Total Rain Flag": props.get('total_rainfall_flag', ''),
        "Total Snow (cm)": props.get('total_snowfall', ''),
        "Total Snow Flag": props.get('total_snowfall_flag', ''),
        "Total Precip (mm)": props.get('total_precipitation', ''),
        "Total Precip Flag": props.get('total_precipitation_flag', ''),
        "Snow on Grnd (cm)": props.get('snow_on_ground', ''),
        "Snow on Grnd Flag": props.get('snow_on_ground_flag', ''),
        "Dir of Max Gust (10s deg)": props.get('direction_max_gust', ''),
        "Dir of Max Gust Flag": props.get('direction_max_gust_flag', ''),
        "Spd of Max Gust (km/h)": props.get('speed_max_gust', ''),
        "Spd of Max Gust Flag": props.get('speed_max_gust_flag', '')
    }
def fetch_new_data(start_date: datetime.date, climate_id: str) -> List[Dict]:
    today = datetime.date.today()
    end_date = today - datetime.timedelta(days=1)  # Fetch data up to yesterday
    
    if start_date > end_date:
        logging.info(f"Start date {start_date} is after yesterday. No new data to fetch.")
        return []

    logging.info(f"Fetching data from {start_date} to {end_date} for climate ID {climate_id}")
    
    params = {
        "f": "json",
        "climate_id": climate_id,
        "datetime": f"{start_date.isoformat()}/{end_date.isoformat()}",
        "limit": 1000,
        "sortby": "+date"
    }

    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        return []

    api_data = response.json().get('features', [])
    return [format_api_data(item) for item in api_data 
            if start_date <= datetime.datetime.strptime(item['properties']['date'], '%Y-%m-%d').date() <= end_date]

def write_csv(filename: str, data: List[Dict]) -> None:
    if not data:
        logging.info("No data to write.")
        return

    fieldnames = data[0].keys()

    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except IOError as e:
        logging.error(f"Error writing to CSV: {e}")

def main() -> None:
    update_weather_csv(CSV_FILENAME)

if __name__ == "__main__":
    main()
