import gym
from gym import spaces
import numpy as np
from gym_game.envs.weatherEnvironment import WeatherEnv, weather_environment

class CustomEnv(gym.Env):
    def __init__(self):
        self.weather_environment = weather_environment()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(np.array([0, 0, 0, 0, 0]), np.array([10, 10, 10, 10, 10]), dtype=np.int)

    def reset(self):
        del self.weather_environment
        self.weather_environment = weather_environment()
        obs = self.weather_environment.observe()
        return obs

    def step(self, action):
        self.weather_environment.action(action)
        obs = self.weather_environment.observe()
        reward = self.weather_environment.evaluate()
        done = self.weather_environment.is_done()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        self.weather_environment.view()