import sys
import numpy as np
import math
import random
import gym
import gym_game
import os
from datetime import datetime
import json  # Correct import for JSON handling

# Info JSON path
info_path = "/Users/simon/Desktop/Areas/TKS/Focus 1 - RL/IRL-RL Application/Databases/info.json"

# Load JSON data from the file
with open(info_path, 'r') as file:
    info = json.load(file)  # Use json.load to read from a file

# Assuming UPDATE_INTERVAL is defined elsewhere in your code
UPDATE_INTERVAL = 1  # Example value, adjust as necessary

def verify_logs(logs_path):
    if os.path.exists(logs_path):
        with open(logs_path) as last_updated:
            last_updated_date = last_updated.readline().strip()
            last_updated_date = datetime.strptime(last_updated_date, '%Y-%m-%d').date()
            current_date = datetime.now().date()

            if last_updated_date == current_date:
                print("Success: Database was updated today.")
                sys.exit()  # Exit the program successfully
            else:
                print("Failure: Database was not updated today.")
                sys.exit(1)  # Exit with a failure code
    else:
        print("Failure: Log file does not exist.")
        sys.exit(1)  # Exit with a failure code
verify_logs(info['Logs']['Historical Weather Data Log'])

def simulate():
    global epsilon, epsilon_decay
    for episode in range(MAX_EPISODES):
        # Init environment
        state = env.reset()
        total_reward = 0

        # AI tries up to MAX_TRY times
        for t in range(MAX_TRY):
            # In the beginning, do random action to learn
            if random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()
            else:
                state_tuple = tuple(state.flatten())
                action = np.argmax(q_table[state_tuple])

            # Do action and get result
            next_state, reward, done, _ = env.step(action)
            total_reward += reward

            # Get correspond q value from state, action pair
            state_tuple = tuple(state.flatten())
            q_value = q_table[state_tuple][action]
            next_state_tuple = tuple(next_state.flatten())
            best_q = np.max(q_table[next_state_tuple])

            # Q(state, action) <- (1 - a)Q(state, action) + a(reward + rmaxQ(next state, all actions))
            q_table[state_tuple][action] = (1 - learning_rate) * q_value + learning_rate * (reward + gamma * best_q)

            # Set up for the next iteration
            state = next_state

            # Draw games
            env.render()

            # When episode is done, print reward
            if done or t >= MAX_TRY - 1:
                print(f"Episode {episode} finished after {t} time steps with total reward = {total_reward:.2f}.")
                break

        # exploring rate decay
        if epsilon >= 0.005:
            epsilon *= epsilon_decay

if __name__ == "__main__":
    env = gym.make("Weather-ai-v1")
    MAX_EPISODES = 9999
    MAX_TRY = 1000
    epsilon = 1
    epsilon_decay = 0.999
    learning_rate = 0.1
    gamma = 0.6

    # Adjust Q-table initialization for the new observation space
    obs_space = env.observation_space['weather'].shape[0] + \
                env.observation_space['satellite'].shape[0] * env.observation_space['satellite'].shape[1] * env.observation_space['satellite'].shape[2] + \
                env.observation_space['space'].shape[0] * env.observation_space['space'].shape[1] * env.observation_space['space'].shape[2]
    
    # Discretize the observation space
    num_bins = 10
    obs_high = np.concatenate([
        env.observation_space['weather'].high,
        np.full(env.observation_space['satellite'].shape, 255),
        np.full(env.observation_space['space'].shape, 255)
    ])
    obs_low = np.concatenate([
        env.observation_space['weather'].low,
        np.full(env.observation_space['satellite'].shape, 0),
        np.full(env.observation_space['space'].shape, 0)
    ])
    bin_sizes = (obs_high - obs_low) / num_bins

    q_table = {}

    simulate()
