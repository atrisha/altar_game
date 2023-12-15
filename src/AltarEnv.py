import functools
import gymnasium
from gymnasium.spaces import Discrete, Box
from pettingzoo import ParallelEnv
from pettingzoo.utils import parallel_to_aec, wrappers
import threading
import sys
from pathlib import Path
from controllers.player_controllers import handle_player_sprites, insert_observation_data,\
    state_to_vec
import controllers.llm_controls
from controllers import llm_controls,db_utils
from multiprocessing import Process
src_path = Path(__file__).resolve().parent.parent
sys.path.append(str(src_path))

import numpy as np
# Now you can import p

# Now you can import p
import phaser_env_bridge
src_path = Path(__file__).resolve().parent.parent
sys.path.append(str(src_path))
import phaser_bridge






NUM_ITERS = 1000


req_ctr = 0
prev_state,prev_state_vec,prev_action,prev_score,curr_policy = None, None, None, None, None
app_thread = None

def env(render_mode=None):
    internal_render_mode = render_mode if render_mode != "ansi" else "human"
    env = raw_env(render_mode=internal_render_mode)
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env

def raw_env(render_mode=None):
    env = AltarMARLEnv(render_mode=render_mode)
    env = parallel_to_aec(env)
    return env

def int_to_binary_array(number):
    # Convert to binary string and remove '0b' prefix
    binary_str = [bin(x)[2:] for x in number]
    padded_binary_str = [x.zfill(4) for x in binary_str]
    # Convert each binary digit to an integer and store in a list
    binary_array = [[int(digit) for digit in x] for x in padded_binary_str]

    return binary_array

class AltarMARLEnv(ParallelEnv):
    metadata = {"render_modes": ["human"], "name": "rps_v2"}

    def __init__(self, render_mode=None):
        global app_thread
        super(AltarMARLEnv, self).__init__()
        self.action_space = Box(low=-1, high=32, shape=(1,), dtype=np.float32)
        self.observation_space  = Box(low=-1, high=10, shape=(4,), dtype=np.float32)
        self.possible_agents = ["player_" + str(r) for r in np.arange(1,4)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        self.render_mode = render_mode
        self.reset_flag = False
        if app_thread is None:
            app_thread = threading.Thread(target=phaser_bridge.start_app)
            app_thread.start()
        
        

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Box(low=-1, high=10, shape=(4,), dtype=np.float32)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Box(low=-1, high=32, shape=(1,), dtype=np.float32)

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return
        if len(self.agents) == 2:
            pass
        else:
            string = "Game over"
        print(string)

    def close(self):
        pass

    def reset(self, seed=None, options=None):
        global app_thread
        self.num_moves = 0
        if app_thread is None:
            app_thread = threading.Thread(target=phaser_bridge.start_app)
            app_thread.start()
        
            
        self.agents = self.possible_agents[:]
        self.num_moves = 0
        observations = {agent: np.asarray([0,0,0,0]) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        self.state = np.asarray([[0,0,0,0]]*len(self.agents))
        self.reset_flag = True
        return self.state, infos

    def step(self, actions):
        actions = int_to_binary_array(actions)
        global prev_state,prev_state_vec,prev_action,prev_score,curr_policy
        if not self.reset_flag:
            request = list(phaser_env_bridge.phaser_to_env_queue.get().values())[-1]
        else:
            request = list(phaser_env_bridge.phaser_to_env_queue.get().values())[0]
        sprite_state = request['sprite_state']
        events = request['events']
        state_vector = np.asarray(state_to_vec(sprite_state), dtype=np.float32)
        '''
        if self.num_moves==0:
            last_obs_time = 0 if self.num_moves == 0 else db_utils.get_last_update_time()
            player_policy = llm_controls.get_policy_function(self.num_moves, last_obs_time, curr_policy)
            curr_policy = player_policy
        '''
        player_actions = handle_player_sprites(sprite_state,actions)
        
        if prev_score is not None:
            reward = [x[0]-x[1] for x in zip([x['score'] for x in sprite_state], prev_score)]
        else:
            reward = [0]*len(self.agents)
        '''
        for act in actions:
            reward = 0
            reward = reward + 10 if act[0] == 1 else reward
            reward = reward - 5 if act[1] == 1 else reward
            reward = reward + 10 if act[2] == 1 else reward
            reward = reward + 5 if act[3] == 1 else reward
        reward = [reward]*len(self.agents)
        ''' 
        '''
        if self.num_moves >= 1:
            print('---',self.num_moves,'---')
            print('state',prev_state_vec[0])
            print('action',actions)
            print('reward',reward[0])
            print('reward0',prev_score[0])
            print('reward1',[x['score'] for x in sprite_state][0])
        '''
        '''    
        if self.num_moves > 1:
            sa = insert_observation_data(prev_state,prev_action,reward,events,self.num_moves-1)
        '''
        prev_state = sprite_state
        if self.num_moves == 0:
            prev_state_vec = self.state
        else:
            prev_state_vec = state_vector
        observations = {agent: prev_state_vec for idx,agent in enumerate(self.agents)}
        
            
        
        prev_score = [x['score'] for x in sprite_state]
        prev_action = list(player_actions['action'])
        #print('sent actions',player_actions)
        #print('sent attributes',[x[1]['action_attribute']['locations'] if x[0] in ['eat','avoid'] else None for x in player_actions])
        #player_actions_list = [{"Xv": xv, "Yv": yv} for xv, yv in player_actions]
        # Process the sprite state
        # For example, you might check conditions or store data
        player_actions_list = player_actions
        resp_dict = {
            'status': 'success',
            'resp_id': self.num_moves,
            'player_actions': {'action':player_actions['action'],
                               'info':{
                                   'visit':player_actions['visit_locations'],
                                   'reset':self.reset_flag
                                   }
                               }
            
        }
        self.reset_flag = False
        #print('received state',resp)
        phaser_env_bridge.env_to_phaser_queue.put({self.num_moves:resp_dict})
        self.num_moves += 1
        
        if not actions:
            self.agents = []
            return {}, {}, {}, {}, {}
        rewards = {agent: reward[idx] for idx,agent in enumerate(self.agents)}
        '''
        rewards[self.agents[0]], rewards[self.agents[1]] = REWARD_MAP[
            (actions[self.agents[0]], actions[self.agents[1]])
        ]
        '''
        terminations = {agent: False for agent in self.agents}
        
        env_truncation = self.num_moves >= NUM_ITERS
        truncations = {agent: env_truncation for agent in self.agents}
        '''
        observations = {
            self.agents[i]: int(actions[self.agents[1 - i]])
            for i in range(len(self.agents))
        }
        '''
        
        self.state = observations
        infos = {agent: {} for agent in self.agents}
        if env_truncation:
            self.agents = []
        if self.render_mode == "human":
            self.render()
        
        return observations, rewards, False, truncations, infos
        



