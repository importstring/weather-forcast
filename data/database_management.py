import requests
import pandas as pd
from datetime import datetime
import os
import csv
filename = 'logs.csv' 

def updateLogs(filename):

    if not os.path.exists(filename):
        with open(filename, 'w') as file: 
            dw = csv.DictWriter(file,  
                            fieldnames='Last Updated') 
            dw.writeheader() 
            dw.writerow({'Last Updated': datetime.now().day})
            dw.writerow('\n')
            dw.writerow({datetime.now()})

with open(filename, 'r') as f:
    lines = f.readlines()
    
    lines.next()
    for line in lines:
        if line == datetime.now():
            exit()
#TODO: update and if successful update logs
# API endpoint and parameters
base_url = "https://api.weather.gc.ca/collections/ahccd-annual/items"
params = {
    "CLIMATE_ID": "6158731",  # Climate ID for Toronto Intl A
    "start_date": datetime.today().strftime('%Y-%m-%d'),  # Today's date
    "end_date": datetime.today().strftime('%Y-%m-%d'),    # Today's date
    "f": "json"  # Format of the response, json or csv
}

#Finalize the time
current_hour = datetime.now().hour
current_day = datetime.now().day
current_month = datetime.now().month
current_year = datetime.now().year

# Existing CSV file path
#csv_file_path = f"/Users/simon/Desktop/Areas/TKS/Focus 1 - RL/IRL-RL Application/Databases/Data/Toronto Weather Data/{current_year}.csv" # get the path to update the CSV file
# For Github this is
csv_file_path = f"{current_year}.csv"
# Fetch the data from the API
response = requests.get(base_url, params=params)
if response.status_code == 200:
    data = response.json()
    
    # Extract relevant fields (adjust according to API response structure)
    new_data = []
    for item in data['features']:
        # Assuming 'properties' contains the weather data
        properties = item['properties']
        new_data.append([
            properties.get('longitude'),
            properties.get('latitude'),
            properties.get('station_name'),
            properties.get('climate_id'),
            properties.get('date_time'),
            properties.get('year'),
            properties.get('month'),
            properties.get('day'),
            properties.get('data_quality', ""),
            properties.get('max_temp', ""),
            properties.get('max_temp_flag', ""),
            properties.get('min_temp', ""),
            properties.get('min_temp_flag', ""),
            properties.get('mean_temp', ""),
            properties.get('mean_temp_flag', ""),
            properties.get('heat_deg_days', ""),
            properties.get('heat_deg_days_flag', ""),
            properties.get('cool_deg_days', ""),
            properties.get('cool_deg_days_flag', ""),
            properties.get('total_rain', ""),
            properties.get('total_rain_flag', ""),
            properties.get('total_snow', ""),
            properties.get('total_snow_flag', ""),
            properties.get('total_precip', ""),
            properties.get('total_precip_flag', ""),
            properties.get('snow_on_grnd', ""),
            properties.get('snow_on_grnd_flag', ""),
            properties.get('dir_of_max_gust', ""),
            properties.get('dir_of_max_gust_flag', ""),
            properties.get('spd_of_max_gust', ""),
            properties.get('spd_of_max_gust_flag', "")
        ])

    # Load the existing CSV file
    existing_df = pd.read_csv(csv_file_path)
    
    # Create a new DataFrame from the new data
    columns = ["Longitude (x)", "Latitude (y)", "Station Name", "Climate ID", "Date/Time", "Year", "Month", "Day",
               "Data Quality", "Max Temp (°C)", "Max Temp Flag", "Min Temp (°C)", "Min Temp Flag", "Mean Temp (°C)",
               "Mean Temp Flag", "Heat Deg Days (°C)", "Heat Deg Days Flag", "Cool Deg Days (°C)", "Cool Deg Days Flag",
               "Total Rain (mm)", "Total Rain Flag", "Total Snow (cm)", "Total Snow Flag", "Total Precip (mm)",
               "Total Precip Flag", "Snow on Grnd (cm)", "Snow on Grnd Flag", "Dir of Max Gust (10s deg)",
               "Dir of Max Gust Flag", "Spd of Max Gust (km/h)", "Spd of Max Gust Flag"]
    
    new_df = pd.DataFrame(new_data, columns=columns)
    
    # Append the new data to the existing DataFrame
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Save the updated DataFrame back to the CSV
    updated_df.to_csv(csv_file_path, index=False)
    
    print("CSV file updated successfully.")
else:
    print(f"Failed to fetch data from API. Status code: {response.status_code}")
