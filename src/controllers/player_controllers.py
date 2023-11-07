'''
Created on 16 Oct 2023

@author: Atrisha
'''
import random
import sqlite3
import json
import os
import controllers.configs as config
from controllers import db_utils
import math
import random
import numpy as np

player_op_policy_function = {
    'when_sees_normal_player': {'punish':0, 'avoid':0, 'do_nothing':1},
    'when_sees_green_player': {'punish':1, 'avoid':0, 'do_nothing':0},
    'when_sees_apple': {'eat':1, 'avoid':0},
    'when_sees_banana': {'eat':0, 'avoid':1},
    'when_turned_green':{'explore':0, 'visit_altar':1,'visit_fountain':0,'visit_houses':0,'visit_trees':0},
    'when_normal':{'explore':1, 'visit_altar':0,'visit_fountain':0,'visit_houses':0,'visit_trees':0}
    }
player_policy_function = {'when_sees_normal_player': {'punish': 0.1, 'avoid': 0.7, 'do_nothing': 0.2}, 
 'when_sees_green_player': {'punish': 0.1, 'avoid': 0.6, 'do_nothing': 0.3}, 
 'when_sees_apple': {'eat': 0.9, 'avoid': 0.1}, 
 'when_sees_banana': {'eat': 0.9, 'avoid': 0.1}, 
 'when_turned_green': {'explore': 0.4, 'visit_fountain': 0.1, 'visit_houses': 0.15, 'visit_trees': 0.15}, 
 'when_normal': {'explore': 0.3, 'visit_fountain': 0.1, 'visit_houses': 0.2, 'visit_trees': 0.2}
 }

'''
player_policy_function = {'when_sees_normal_player': {'punish':0.1, 'avoid':0.6, 'do_nothing':0.3},
                         'when_sees_green_player': {'punish':0.1, 'avoid':0.6, 'do_nothing':0.3},
                             'when_sees_apple': {'eat':0.7, 'avoid':0.3},
                                 'when_sees_banana': {'eat':0.7, 'avoid':0.3},
                                     'when_turned_green':{'explore':0.6, 'visit_altar':0.1,'visit_fountain':0.1,'visit_houses':0.1,'visit_trees':0.1},
                                         'when_normal':{'explore':0.6, 'visit_altar':0.1,'visit_fountain':0.1,'visit_houses':0.1,'visit_trees':0.1}
                                         }

player_policy_function = {'when_sees_normal_player': {'punish':0.1, 'avoid':0.7, 'do_nothing':0.2},
                              'when_sees_green_player': {'punish':0.1, 'avoid':0.7, 'do_nothing':0.2},
                                 'when_sees_apple': {'eat':0.8, 'avoid':0.2},
                                     'when_sees_banana': {'eat':0.8, 'avoid':0.2},
                                         'when_turned_green':{'explore':0.7, 'visit_altar':0.08,'visit_fountain':0.07,'visit_houses':0.08,'visit_trees':0.07},
                                             'when_normal':{'explore':0.7, 'visit_altar':0.08,'visit_fountain':0.07,'visit_houses':0.08,'visit_trees':0.07}}
'''
state_importance = {k:1/len(player_op_policy_function) for k in player_op_policy_function.keys()}


state_evals = {
    'when_sees_normal_player': lambda player : True if 'player' in player['surroundingInfos'] and any([not x['poisoned_player'] for x in player['surroundingInfos']['player']]) else False,
    'when_sees_green_player': lambda player : True if 'player' in player['surroundingInfos'] and any([x['poisoned_player'] for x in player['surroundingInfos']['player']]) else False,
    'when_sees_apple': lambda player : True if 'apple' in player['surroundingInfos'] else False,
    'when_sees_banana': lambda player : True if 'banana' in player['surroundingInfos'] else False,
    'when_turned_green': lambda player : True if player['poisoned'] else False,
    'when_normal': lambda player : False if player['poisoned'] else True
    }

object_code = {'houses':'h','trees':'t','altar':'n','fountain':'f','immaterial':'i','banana':'b','apple':'a','green player':'g','normal player':'p','player':'p'}
action_code = {'explore':'r','avoid':'x','eat':'c','visit':'v','do_nothing':'r','punish':'s'}
def surrounding_info_to_sentence(player):
    sentence_descr = []
    play_pos = (math.floor(player['x']/config.TILE_SIZE),math.floor(player['y']/config.TILE_SIZE))
    _suffix = lambda d : object_code['immaterial']+str(d)
    postpend = None
    for k,v in player['surroundingInfos'].items():
        dist_to_obj = min([abs(x['tilePosition']['x']-play_pos[0]) + abs(x['tilePosition']['y']-play_pos[1]) for x in v ])
        if k == 'immaterial':
            postpend = _suffix(dist_to_obj)
        else:
            sentence_descr.append(object_code[k]+' '+str(dist_to_obj))
    if postpend is not None:
        sentence_descr.append(postpend)
    if player['punished']:
        sentence_descr.append('p')
    if player['poisoned']:
        sentence_descr.append('g')
    return ''.join(sentence_descr)







policy_to_description = lambda policy : '\
                                            player_policy_function = Encounter other green player: {punish probability: '+str(policy['punish_green'])+',\
                                            do not punish probability: '+str(policy['dont_punish_green'])+', \
                                            avoid probability: '+str(policy['avoid_green_player'])+'},\
                                            Encounter other non-green player: {punish probability: '+str(policy['punish_normal'])+', \
                                            do not punish probability: '+str(policy['dont_punish_normal'])+',\
                                            avoid probability: '+str(policy['avoid_normal_player'])+'},\
                                            Encounter apple: {eat probability: '+str(policy['eat_apple'])+', \
                                            avoid probability: '+str(policy['avoid_apple'])+'},\
                                            Encounter banana: {eat probability: '+str(policy['eat_banana'])+', \
                                            avoid probability: '+str(policy['avoid_banana'])+'},\
                                            If I am green: {keep exploring probability: '+str(policy['explore_when_green'])+', \
                                            go visit the altar probability: '+str(policy['visit_altar_when_green'])+'},\
                                            If I am not green: {keep exploring probability: '+str(policy['explore_when_normal'])+', \
                                            go visit the altar probability: '+str(policy['visit_altar_when_normal'])+'}\
                                            '
    
def control_player(player,policy_function=player_op_policy_function):
    '''
        [self_green,other_player,apple,banana,object,punished,]
    '''
    
    state_importance =  {'when_sees_normal_player': 0.033,    'when_sees_green_player': 0.033,    'when_sees_apple': 0.2,    'when_sees_banana': 0.3,    'when_turned_green': 0.4,    'when_normal': 0.034}

    all_state_evals =dict()
    for k,v in policy_function.items():
        state_eval_true = state_evals[k](player)
        all_state_evals[k] = state_eval_true
    possible_actions = dict()
    for k,v in all_state_evals.items():
        
        if v:
            action_objs = []
            
            for act, act_probs in policy_function[k].items():
                action_obj = dict()
                action_obj['action'] = act 
                if act in ['visit_fountain','visit_houses','visit_trees']:
                    action_obj['action'] = 'explore'
                action_obj['action_attribute'] = dict()
                if act in ['visit_altar']:
                    action_obj['action'] = 'visit'
                    action_obj['action_attribute']['visit_location'] = 'altar'
                    action_obj['action_attribute']['locations'] = [{'x':33,'y':7}]
                
                if k == 'when_sees_normal_player':
                    action_obj['action_attribute']['object'] = 'normal player'
                    for opl in player['surroundingInfos']['player']:
                        if not opl['poisoned_player']:
                            action_obj['action_attribute']['locations'] = [{'x':opl['tilePosition']['x'],'y':opl['tilePosition']['x']}]
                elif k == 'when_sees_green_player':
                    action_obj['action_attribute']['object'] = 'green player'
                    for opl in player['surroundingInfos']['player']:
                        if opl['poisoned_player']:
                            action_obj['action_attribute']['locations'] = [{'x':opl['tilePosition']['x'],'y':opl['tilePosition']['x']}]
                elif k == 'when_sees_apple':
                    action_obj['action_attribute']['object'] = 'apple'
                    action_obj['action_attribute']['locations'] = [x['tilePosition'] for x in player['surroundingInfos']['apple']]
                elif k ==  'when_sees_banana':
                    action_obj['action_attribute']['object'] = 'banana'
                    action_obj['action_attribute']['locations'] = [x['tilePosition'] for x in player['surroundingInfos']['banana']]
                
                    
                action_obj['action_probability'] = act_probs
                action_objs.append(action_obj)
                if action_obj['action'] == 'visit':
                    f=1
            possible_actions[k] = action_objs
    state_importances = {k:state_importance[k] for k in possible_actions}
    selected_state = np.random.choice(list(state_importances.keys()),p=[v/np.sum(list(state_importances.values())) for k,v in state_importances.items()])
    actions_to_select_from = possible_actions[selected_state]
    _prob_sum = np.sum([x['action_probability'] for x in actions_to_select_from])
    selected_action_index = np.random.choice(np.arange(len(actions_to_select_from)),p=[x['action_probability']/_prob_sum for x in actions_to_select_from])
    return (actions_to_select_from[selected_action_index]['action'],actions_to_select_from[selected_action_index])
    

def handle_player_sprites(state,player_policy):
    actions = []
    for player in state:
        actions.append(control_player(player,player_policy))
    return actions

def create_observation_for_memory(state,actions,rewards,events,time_st):
    batch_data = []
    max_id = db_utils.get_max_id()
    for idx,player in enumerate(state):
        player_data = dict()
        max_id = max_id + 1
        play_pos = (math.floor(player['x']/config.TILE_SIZE),math.floor(player['y']/config.TILE_SIZE))
        player_data['id'] = max_id
        player_data['player_id'] = player['name']
        player_data['observation_time'] = time_st
        player_data['observation'] = surrounding_info_to_sentence(player)
        player_data['action_taken'] = action_code[actions[idx]['action']] + object_code[actions[idx]['action_attribute']['object']] if 'object' in actions[idx]['action_attribute'] else action_code[actions[idx]['action']]
        player_data['events'] = ','.join(events)
        player_data['reward_received'] = rewards[idx]
        batch_data.append(player_data)
    return batch_data

def insert_observation_data(state,actions,rewards,events,time_st):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '../../data/database/episodes.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    batch_data = create_observation_for_memory(state,actions,rewards,events,time_st)
    '''
    batch_data = [
        {"player_id": 1, 
         "observation_time": "2022-10-20 14:00:00",
          "observation": json.dumps({"obs_key": "obs_value"}), 
          "action_taken": json.dumps({"action_key": "action_value"}), 
          "reward_received": 10.5},
        {"player_id": 2, 
         "observation_time": "2022-10-20 14:05:00", 
         "observation": json.dumps({"obs_key": "obs_value2"}), 
         "action_taken": json.dumps({"action_key": "action_value2"}), 
         "reward_received": 12.5},
    
    ]
    '''

    
    sql = """
    INSERT INTO player_observations (id, player_id, observation_time, observation, action_taken, events, reward_received) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    to_insert = [(data['id'],data['player_id'], data['observation_time'], data['observation'], data['action_taken'], data['events'], data['reward_received']) for data in batch_data]
    cursor.executemany(sql, to_insert)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    return batch_data