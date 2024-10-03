import aiohttp
import asyncio
import ssl
import certifi
import json

async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            print(f"Response status: {response.status}")
            print(f"Response headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

async def main():
    # Create a custom SSL context using certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        url = "https://api.weather.gc.ca/collections/climate-daily/items?f=json&limit=365&offset=0"
        data = await fetch_data(session, url)
        
        if data:
            print(f"\nData keys: {data.keys()}")
            print(f"Number matched: {data.get('numberMatched', 'N/A')}")
            print(f"Number returned: {data.get('numberReturned', 'N/A')}")
            
            features = data.get('features', [])
            if features:
                first_feature = features[0]
                print("\nFirst feature structure:")
                print(json.dumps(first_feature, indent=2))
                
                properties = first_feature.get('properties', {})
                print("\nFirst feature data:")
                for key, value in properties.items():
                    print(f"{key}: {value}")
                
                print(f"\nNumber of features: {len(features)}")
            else:
                print("No features found in the data.")
        else:
            print("Failed to fetch data.")

if __name__ == "__main__":
    asyncio.run(main())
