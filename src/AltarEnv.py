import functools
import gymnasium
from gymnasium.spaces import Discrete
from pettingzoo import ParallelEnv
from pettingzoo.utils import parallel_to_aec, wrappers
import threading
import sys
from pathlib import Path
from controllers.player_controllers import handle_player_sprites, insert_observation_data
import controllers.llm_controls
from controllers import llm_controls,db_utils
src_path = Path(__file__).resolve().parent.parent
sys.path.append(str(src_path))

# Now you can import p
import phaser_bridge

# Calculate the path to the src directory from the perspective of a.py
src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(src_path))

# Now you can import p
import phaser_env_bridge





ROCK = 0
PAPER = 1
SCISSORS = 2
NONE = 3
MOVES = ["ROCK", "PAPER", "SCISSORS", "None"]
NUM_ITERS = 1000
REWARD_MAP = {
    (ROCK, ROCK): (0, 0),
    (ROCK, PAPER): (-1, 1),
    (ROCK, SCISSORS): (1, -1),
    (PAPER, ROCK): (1, -1),
    (PAPER, PAPER): (0, 0),
    (PAPER, SCISSORS): (-1, 1),
    (SCISSORS, ROCK): (-1, 1),
    (SCISSORS, PAPER): (1, -1),
    (SCISSORS, SCISSORS): (0, 0),
}

req_ctr = 0
prev_state,prev_action,prev_score,curr_policy = None, None, None, None

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

class AltarMARLEnv(ParallelEnv):
    metadata = {"render_modes": ["human"], "name": "rps_v2"}

    def __init__(self, render_mode=None):
        self.possible_agents = ["player_" + str(r) for r in range(2)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        self.render_mode = render_mode
        self.num_moves = 0
        app_thread = threading.Thread(target=phaser_bridge.start_app)
        app_thread.start()

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Discrete(4)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(3)

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return
        if len(self.agents) == 2:
            string = "Current state: Agent1: {} , Agent2: {}".format(
                MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]
            )
        else:
            string = "Game over"
        print(string)

    def close(self):
        pass

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.num_moves = 0
        observations = {agent: NONE for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        self.state = observations
        return observations, infos

    def step(self, actions):
        global prev_state,prev_action,prev_score,curr_policy
        request = phaser_env_bridge.phaser_to_env_queue.get()[self.num_moves]
        sprite_state = request['sprite_state']
        events = request['events']
        if self.num_moves==0:
            last_obs_time = 0 if self.num_moves == 0 else db_utils.get_last_update_time()
            player_policy = llm_controls.get_policy_function(self.num_moves, last_obs_time, curr_policy)
            curr_policy = player_policy
        player_actions = handle_player_sprites(sprite_state,curr_policy)
        if prev_score is not None:
            reward = [x[0]-x[1] for x in zip([x['score'] for x in sprite_state], prev_score)]
        else:
            reward = [0,0]
        if self.num_moves > 1:
            sa = insert_observation_data(prev_state,prev_action,reward,events,self.num_moves-1)
        prev_state = sprite_state
        
        prev_score = [x['score'] for x in sprite_state]
        prev_action = [x[1] for x in player_actions]
        print('sent actions',[x[0] for x in player_actions])
        print('sent attributes',[x[1]['action_attribute']['locations'] if x[0] in ['eat','avoid'] else None for x in player_actions])
        #player_actions_list = [{"Xv": xv, "Yv": yv} for xv, yv in player_actions]
        # Process the sprite state
        # For example, you might check conditions or store data
        player_actions_list = player_actions
        resp_dict = {
            'status': 'success',
            'resp_id': self.num_moves,
            'player_actions': [x[1] for x in player_actions_list]
            
        }
        print(player_actions_list)
        #print('received state',resp)
        phaser_env_bridge.env_to_phaser_queue.put({self.num_moves:resp_dict})
        self.num_moves += 1
        '''
        if not actions:
            self.agents = []
            return {}, {}, {}, {}, {}
        rewards = {}
        rewards[self.agents[0]], rewards[self.agents[1]] = REWARD_MAP[
            (actions[self.agents[0]], actions[self.agents[1]])
        ]
        terminations = {agent: False for agent in self.agents}
        
        env_truncation = self.num_moves >= NUM_ITERS
        truncations = {agent: env_truncation for agent in self.agents}
        observations = {
            self.agents[i]: int(actions[self.agents[1 - i]])
            for i in range(len(self.agents))
        }
        self.state = observations
        infos = {agent: {} for agent in self.agents}
        if env_truncation:
            self.agents = []
        if self.render_mode == "human":
            self.render()
        
        return observations, rewards, terminations, truncations, infos
        '''
        return None

cenv = AltarMARLEnv()
while(True):
    cenv.step(None)

