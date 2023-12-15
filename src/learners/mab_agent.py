import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim
from torch.distributions import Categorical, Multinomial, Dirichlet
import sys
from pathlib import Path
from AltarEnv import AltarMARLEnv
from torch.utils.tensorboard import SummaryWriter
import shutil
import matplotlib.pyplot as plt
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"



class MultiArmedBandit:
    def __init__(self, k_arms=10, true_reward=0):
        self.k = k_arms
        self.true_reward = true_reward
        self.arm_values = np.random.normal(true_reward, 1, self.k)  # Initialize each arm with a true value
        self.k_n = np.zeros(self.k)  # Count of times each arm was pulled
        self.mean_reward = np.random.normal(0, 1, self.k)  # Mean reward for each arm
        self.mean_reward_list = [[i] for i in self.mean_reward]
        self.total_reward = 0
        # For Thompson Sampling
        self.successes = np.zeros(self.k)
        self.failures = np.zeros(self.k)

    def int_to_binary_array(self,arm):
        # Convert to binary string and remove '0b' prefix
        binary_str = bin(arm)[2:]
        
        padded_binary_str = binary_str.zfill(4)
        
        # Convert each binary digit to an integer and store in a list
        binary_array = [int(digit) for digit in padded_binary_str]
        
        return binary_array

    

    def pull(self, arm, reward):
        # Simulate pulling an arm: Gaussian reward based on true arm value
        #reward = self.get_reward(self.int_to_binary_array(arm))
        self.k_n[arm] += 1
        self.mean_reward[arm] += (reward - self.mean_reward[arm]) / self.k_n[arm]
        self.mean_reward_list[arm].append(reward)
        self.total_reward += reward

        # Update successes and failures for Thompson Sampling
        if reward > 0:  # Considering a positive reward as a success
            self.successes[arm] += 1
        else:
            self.failures[arm] += 1
        return reward

    def choose_arm_ucb(self, t):
        # UCB (Upper Confidence Bound) selection strategy
        upper_bound = self.mean_reward + np.sqrt(2 * np.log(t + 1) / (self.k_n + 1e-5))
        return np.argmax(upper_bound)

    def choose_arm_thompson(self):
        # Thompson Sampling selection strategy
        sampled_beta = np.random.beta(self.successes + 1, self.failures + 1)
        return np.argmax(sampled_beta)

    def best_arm_reward(self):
        return np.max(self.arm_values)
# Memory class for storing trajectories
class Memory:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.is_terminals[:]

       
import gym

def calculate_regret(mab, rewards):
    optimal_reward = np.max(mab.arm_values) * len(rewards)
    actual_reward = np.sum(rewards)
    return optimal_reward - actual_reward

def run_simulation(mab, n_rounds=10000,  strategy='ucb'):
    history = []
    cumulative_regret = 0
    optimal_reward = mab.best_arm_reward()
    regrets = []

    for t in range(n_rounds):
        if strategy == 'ucb':
            arm = mab.choose_arm_ucb(t)
        elif strategy == 'thompson':
            arm = mab.choose_arm_thompson()
        reward = mab.pull(arm)

        # Calculate and accumulate regret
        regret = optimal_reward - reward
        cumulative_regret += regret
        regrets.append(cumulative_regret)

        history.append(reward)
    return regrets

def train_mab(env, max_episodes, max_timesteps, strategy='ucb'):
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]
    log_dir = 'runs/mab_experiment'
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    writer = SummaryWriter(log_dir)
    training_agents = [MultiArmedBandit(k_arms=16) for idx in np.arange(len(env.possible_agents))]
    # Initialize MultiArmedBandit
    

    # Logging variables
    running_reward = 0

    # Training loop
    for episode in range(1, max_episodes+1):
        state, _ = env.reset()
        episode_reward = 0
        arm_ma = []
        for tr_idx,mab_agent in enumerate(training_agents):
            
            # Select action
            if strategy == 'ucb':
                arm = mab_agent.choose_arm_ucb(episode)
            elif strategy == 'thompson':
                arm = mab_agent.choose_arm_thompson()
            
            arm_ma.append(arm)
            # Simulate the environment step
        
        for t in range(max_timesteps):
            print('episode',episode,':',t)
            
            
            print('pulling',arm_ma)
            next_state, reward, done, _, _ = env.step(arm_ma)
            reward = np.mean([training_agents[idx].pull(arm, reward[env.possible_agents[idx]]) for idx,arm in enumerate(arm_ma)])  # Pull the chosen arm)

            running_reward += reward
            episode_reward += reward
            if done:
                break

        # Logging
        avg_length = int(running_reward / episode)
        running_reward = running_reward * 0.99 + episode_reward * 0.01
        if episode % 10 == 0:
            print('Episode {} \t Avg length: {} \t Avg reward: {:.2f}'.format(episode, avg_length, running_reward))
        
        writer.add_scalar('Average Length', avg_length, episode)
        writer.add_scalar('Episode Reward', episode_reward, episode)
        writer.add_scalar('Running Reward', running_reward, episode)
        
        # Save model for every episode
        if episode % 50 == 0:
            # Saving the state of MultiArmedBandit might involve saving the state of its parameters
            # Example: torch.save(mab_agent.state_dict(), './saved_models/MAB_episode_{}.pth'.format(episode))
            pass
    mr = np.mean(np.asarray([mab_agent.mean_reward for mab_agent in training_agents]),axis=0)
    plt.figure()
    print('Optimal arms:')
    for tr_idx,mab_agent in enumerate(training_agents):
        print(tr_idx,':',mab_agent.int_to_binary_array(mab_agent.choose_arm_ucb(max_timesteps)))
        for arm in np.arange(16):
            print('\t',mab_agent.int_to_binary_array(arm),mab_agent.mean_reward_list[arm])
        for arm in np.arange(16):
            print('\t',mab_agent.int_to_binary_array(arm),mab_agent.mean_reward[arm])
        plt.plot([arm for arm in np.arange(16)],[mab_agent.mean_reward[arm] for arm in np.arange(16)],'.',label=str(tr_idx),)
    plt.plot([arm for arm in np.arange(16)],mr)   
        
    writer.close()
    env.close()
    plt.show()
    
    
# Usage example
env = AltarMARLEnv()  # Make sure this environment is compatible with the bandit setup
max_episodes = 100
max_timesteps = 200  # Adjust to the needs of your specific environment

train_mab(env, max_episodes, max_timesteps, strategy='ucb')
