import csv
import json
from datetime import datetime
import os

def get_last_updated_date(csv_path):
    last_updated_date = None

    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)  # Use DictReader for easier column access
        for row in reader:
            # Extract year, month, and day
            year = int(row['Year'])
            month = int(row['Month'])
            day = int(row['Day'])
            
            # Create a datetime object
            current_date = datetime(year, month, day)

            # Update the last_updated_date if this date is more recent
            if last_updated_date is None or current_date > last_updated_date:
                last_updated_date = current_date

    return last_updated_date



def update_logs(data):
    for log_path, csv_path in data.items():
        # Open the log file in write mode to clear its contents
        with open(log_path, 'w') as log_file:
            last_updated_date = get_last_updated_date(csv_path)  # Get the last updated date
            
            if last_updated_date:
                log_file.write(last_updated_date.strftime('%Y-%m-%d'))  # Write the date to the log
            else:
                log_file.write("No valid dates found in the CSV.")  # Handle the case where no dates are found







def update_databases(json_dir, log_dir, csv_file_dir):
    #TODO: Update all the databases
    pass
    pass
    pass
