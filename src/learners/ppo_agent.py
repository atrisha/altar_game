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
import os

# Define the policy network
class PolicyNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.fc(x)


# Define the value network
class ValueNetwork(nn.Module):
    def __init__(self, input_dim):
        super(ValueNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.fc(x)

# PPO Agent
class PPOAgent:
    def __init__(self, input_dim, output_dim, lr=3e-4, gamma=0.99, eps_clip=0.2, K_epochs=4):
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs

        self.policy = PolicyNetwork(input_dim, output_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.policy_old = PolicyNetwork(input_dim, output_dim)
        self.policy_old.load_state_dict(self.policy.state_dict())

        self.value_network = ValueNetwork(input_dim)
        self.value_optimizer = optim.Adam(self.value_network.parameters(), lr=lr)
        
        self.MseLoss = nn.MSELoss()
        
    def normalize_state(self, state):
        self.state_max = 10
        self.state_min = -1
        # Apply min-max normalization
        normalized_state = (state - self.state_min) / (self.state_max - self.state_min)
        # Replace NaNs with 0 (for features with no variation)
        normalized_state = np.nan_to_num(normalized_state)
        return normalized_state

    def select_action(self, state_ma):
        actions,log_probs = [],[]
        for idx in np.arange(self.num_agents):
            state = state_ma[idx]
            state = self.normalize_state(state)
            state = torch.FloatTensor(state.reshape(1, -1))
            probs = self.policy_old(state)
            #policy_vec = (probs>0.5).float()
            dist = Categorical(probs)
            action = dist.sample()
            actions.append(action)
            log_probs.append(dist.log_prob(action))
        return actions, log_probs
        #return policy_vec.tolist(), probs

    def update(self, memory):
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(memory.rewards), reversed(memory.is_terminals)):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)

        rewards = torch.tensor(rewards, dtype=torch.float32)
        old_states = torch.stack(memory.states).detach()
        old_actions = torch.stack(memory.actions).detach()
        old_logprobs = torch.stack(memory.logprobs).detach()

        # Normalizing the rewards:
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-7)

        # Optimize policy for K epochs:
        for _ in range(self.K_epochs):
            # Evaluating old actions and values:
            logprobs, state_values, dist_entropy = self.evaluate(old_states, old_actions)

            # Finding the ratio (pi_theta / pi_theta__old):
            ratios = torch.exp(logprobs - old_logprobs.detach())

            # Finding Surrogate Loss:
            advantages = rewards - state_values.detach()
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * advantages
            policy_loss = -torch.min(surr1, surr2) - 0.01*dist_entropy
            value_loss = 0.5*self.MseLoss(state_values, rewards)
    
            # Combine the policy and value losses for a single backward pass
            loss = policy_loss + value_loss
    
            # take gradient step
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step()
    
            # Fit value network
            self.value_optimizer.zero_grad()
            self.value_optimizer.step()
            
            # Copy new weights into old policy:
            self.policy_old.load_state_dict(self.policy.state_dict())

    def evaluate(self, states, actions):
        action_probs = self.policy(states)
        dist = Categorical(action_probs)

        action_logprobs = dist.log_prob(actions)
        dist_entropy = dist.entropy()
        state_values = self.value_network(states)

        return action_logprobs, torch.squeeze(state_values), dist_entropy

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

# Assuming PPOAgent and Memory classes are defined as in the previous snippet
# and the necessary libraries are imported.

def train_ppo(env, max_episodes, max_timesteps, update_timestep):
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]
    log_dir = 'runs/ppo_experiment'
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

    writer = SummaryWriter(log_dir)

    # Initialize PPO agent and memory
    ppo_agent = PPOAgent(input_dim=state_dim, output_dim=16)
    ppo_agent.num_agents = len(env.possible_agents)
    memory = Memory()

    # Logging variables
    running_reward = 0
    timestep = 0
    next_state = None
    # Training loop
    for episode in range(1, max_episodes+1):
        state, _ = env.reset()
        episode_reward = 0

        for t in range(max_timesteps):
            timestep += 1

            # Select action
            if timestep == 1:
                actions_ma, log_prob_ma = ppo_agent.select_action(state)
            if timestep > 1:
                state = next_state
                actions_ma, log_prob_ma = ppo_agent.select_action(state)
            print('running',episode,t)
            next_state, reward, done, _, _ = env.step(actions_ma)
            next_state = next_state['player_1']
            reward = [reward[p] for p in env.possible_agents]
            
            # Save in memory
            for idx in np.arange(ppo_agent.num_agents):
                action = actions_ma[idx]
                memory.states.append(torch.tensor(state[idx]))
                memory.actions.append(torch.tensor(action))
                memory.logprobs.append(log_prob_ma[idx])
                memory.rewards.append(reward[idx])
                memory.is_terminals.append(done)

            # Update if its time
            if timestep % update_timestep == 0:
                ppo_agent.update(memory)
                memory.clear_memory()
                timestep = 0
                print('-----update Done!')

            running_reward += np.mean(reward)
            episode_reward += np.mean(reward)
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
            torch.save(ppo_agent.policy.state_dict(), './saved_models/PPO_policy_episode_{}.pth'.format(episode))
        
        
    writer.close()
    env.close()

# Train the agent
env = AltarMARLEnv()  # Use an environment that matches your observation and action space
max_episodes = 1000
max_timesteps = 200  # Adjust to the needs of your specific environment
update_timestep = 200  # Update the policy every 2000 timesteps

train_ppo(env, max_episodes, max_timesteps, update_timestep)


