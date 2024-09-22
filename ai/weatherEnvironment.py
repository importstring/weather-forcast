import gym
from gym import spaces
import numpy as np
import csv
from datetime import datetime, timedelta
import os

# Info JSON path
info_path = "/Users/simon/Desktop/Areas/TKS/Focus 1 - RL/IRL-RL Application/Databases/info.json"

class WeatherEnv(gym.Env):
    def __init__(self):
        super(WeatherEnv, self).__init__()
        
        # Define action and observation space
        # Actions: Predict temperature, precipitation, wind speed
        self.action_space = spaces.Box(low=np.array([-50, 0, 0]), high=np.array([50, 100, 200]), dtype=np.float32)
        
        # Observations: Current temperature, precipitation, wind speed, satellite image data, space image data
        self.observation_space = spaces.Dict({
            'weather': spaces.Box(low=np.array([-50, 0, 0]), high=np.array([50, 100, 200]), dtype=np.float32),
            'satellite': spaces.Box(low=0, high=255, shape=(64, 64, 3), dtype=np.uint8),
            'space': spaces.Box(low=0, high=255, shape=(64, 64, 3), dtype=np.uint8)
        })
        
        self.current_date = datetime(2013, 1, 1)
        self.end_date = datetime(2024, 9, 21)
        
        # Load data
        self.weather_data = self.load_historical_data('Weather Data')
        self.forecast_data = self.load_csv_data('forecast_data.csv')
        self.satellite_images = self.load_image_data('satellite_images.csv')
        self.space_images = self.load_image_data('space_images.csv')
    def load_historical_data(self, key):
        data = {}
        files = info_path[key]
        # Iterate over each file
        for file in files:
            with open(file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert the date string into a datetime object
                    date = datetime.strptime(row['Date/Time'], '%Y-%m-%d')
                    
                    # Populate the data dictionary with parsed CSV data
                    data[date] = {
                        'longitude': row['Longitude (x)'],
                        'latitude': row['Latitude (y)'],
                        'station_name': row['Station Name'],
                        'climate_id': row['Climate ID'],
                        'year': row['Year'],
                        'month': row['Month'],
                        'day': row['Day'],
                        'data_quality': row['Data Quality'],
                        'max_temp': row['Max Temp (°C)'],
                        'max_temp_flag': row['Max Temp Flag'],
                        'min_temp': row['Min Temp (°C)'],
                        'min_temp_flag': row['Min Temp Flag'],
                        'mean_temp': row['Mean Temp (°C)'],
                        'mean_temp_flag': row['Mean Temp Flag'],
                        'heat_deg_days': row['Heat Deg Days (°C)'],
                        'heat_deg_days_flag': row['Heat Deg Days Flag'],
                        'cool_deg_days': row['Cool Deg Days (°C)'],
                        'cool_deg_days_flag': row['Cool Deg Days Flag'],
                        'total_rain': row['Total Rain (mm)'],
                        'total_rain_flag': row['Total Rain Flag'],
                        'total_snow': row['Total Snow (cm)'],
                        'total_snow_flag': row['Total Snow Flag'],
                        'total_precip': row['Total Precip (mm)'],
                        'total_precip_flag': row['Total Precip Flag'],
                        'snow_on_ground': row['Snow on Grnd (cm)'],
                        'snow_on_ground_flag': row['Snow on Grnd Flag'],
                        'max_gust_dir': row['Dir of Max Gust (10s deg)'],
                        'max_gust_dir_flag': row['Dir of Max Gust Flag'],
                        'max_gust_speed': row['Spd of Max Gust (km/h)'],
                        'max_gust_speed_flag': row['Spd of Max Gust Flag']
                    }
        
        return data

    def read_csv(self, filename):
        
        with open(filename, 'r') as f:
            return f.read()
    
    def load_csv_data(self, filename):
        data = {}
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = datetime.strptime(row['date'], '%Y-%m-%d')
                data[date] = {
                    'temperature': float(row['temperature']),
                    'precipitation': float(row['precipitation']),
                    'wind_speed': float(row['wind_speed'])
                }
        return data

    def load_image_data(self, filename):
        images = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                image = np.array(list(map(int, row[1:]))).reshape(64, 64, 3)
                images.append(image)
        return np.array(images)

    def step(self, action):
        # Implement the step function
        next_date = self.current_date + timedelta(days=1)
        actual_weather = self.weather_data[next_date]
        
        # Calculate reward based on prediction accuracy
        reward = -np.sum(np.abs(np.array([actual_weather['temperature'], 
                                          actual_weather['precipitation'], 
                                          actual_weather['wind_speed']]) - action))
        
        # Update current date
        self.current_date = next_date
        
        # Check if episode is done
        done = self.current_date >= self.end_date
        
        # Get next observation
        obs = self.get_observation()
        
        return obs, reward, done, {}

    def reset(self):
        self.current_date = datetime(2013, 1, 1)
        return self.get_observation()

    def get_observation(self):
        weather = self.weather_data[self.current_date]
        day_index = (self.current_date - datetime(2013, 1, 1)).days
        return {
            'weather': np.array([weather['temperature'], weather['precipitation'], weather['wind_speed']]),
            'satellite': self.satellite_images[day_index],
            'space': self.space_images[day_index]
        }

    def render(self, mode='human'):
        # Implement visualization if needed
        pass
class weather_environment:
    def __init__(self):
        self.weather_env = WeatherEnv()

    def observe(self):
        obs = self.weather_env.get_observation()
        # Convert Dict observation to flat array for compatibility
        return np.concatenate([
            obs['weather'],
            obs['satellite'].flatten(),
            obs['space'].flatten()
        ])

    def action(self, action):
        # Convert discrete action to continuous
        action_map = {0: [-1, 0, 0], 1: [0, 0, 0], 2: [1, 0, 0]}
        self.weather_env.step(np.array(action_map[action]))

    def evaluate(self):
        # Simple evaluation based on the last reward
        return self.weather_env.last_reward

    def is_done(self):
        return self.weather_env.current_date >= self.weather_env.end_date

    def view(self):
        self.weather_env.render()