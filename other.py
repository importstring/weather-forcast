import aiohttp
import asyncio
import ssl
import certifi
import json
from datetime import datetime, timedelta

async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

async def get_climate_data_for_date(date):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        # Convert date to string format YYYY-MM-DD
        date_str = date.strftime("%Y-%m-%d")
        
        # Construct the URL with the date parameter
        url = f"https://api.weather.gc.ca/collections/climate-daily/items?f=json&datetime={date_str}&limit=1000"
        
        data = await fetch_data(session, url)
        
        if data and 'features' in data:
            features = data['features']
            if features:
                return features
            else:
                print(f"No data found for date: {date_str}")
                return None
        else:
            print(f"Failed to fetch data for date: {date_str}")
            return None

def print_climate_data(features):
    for feature in features:
        properties = feature.get('properties', {})
        print("\nClimate Data:")
        for key, value in properties.items():
            print(f"{key}: {value}")

async def main():
    # Example usage
    target_date = datetime(2023, 1, 1)  # January 1, 2023
    climate_data = await get_climate_data_for_date(target_date)
    
    if climate_data:
        print_climate_data(climate_data)
    else:
        print("No data available for the specified date.")

if __name__ == "__main__":
    asyncio.run(main())

async def get_new_data(day):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        # Ensure day is in the correct format (YYYY-MM-DD)
        if isinstance(day, datetime):
            date_str = day.strftime("%Y-%m-%d")
        elif isinstance(day, str):
            date_str = day
        else:
            raise ValueError("day must be a datetime object or a string in YYYY-MM-DD format")

        url = f"https://api.weather.gc.ca/collections/climate-daily/items?f=json&datetime={date_str}&limit=1000"
        
        data = await fetch_data(session, url)
        
        if data and 'features' in data:
            return data['features']
        else:
            print(f"No data found for date: {date_str}")
            return None

# Example usage
async def main():
    # You can use either a datetime object or a string for the day
    day = datetime(2023, 1, 1)  # or "2023-01-01"
    data = await get_new_data(day)
    
    if data:
        print(f"Data retrieved for {day}:")
        for feature in data:
            print(json.dumps(feature, indent=2))
    else:
        print("No data available for the specified date.")

if __name__ == "__main__":
    asyncio.run(main())

def get_new_data_sync(day):
    return asyncio.run(get_new_data(day))

# Now you can use it like this:
day = datetime(2023, 1, 1)
data = get_new_data_sync(day)
print(data)
