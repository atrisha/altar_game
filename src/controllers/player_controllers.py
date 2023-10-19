'''
Created on 16 Oct 2023

@author: Atrisha
'''
import random


def control_player(player):
    action_obj = dict()
    if player['poisoned']:
        action_obj['action'] = 'visit'
        action_obj['action_attribute'] = dict()
        action_obj['action_attribute']['locations'] = [{'x':33,'y':7}]
    else:
        objects = player['surroundingInfos']
        
        if 'banana' in objects:
            action_obj['action'] = 'avoid'
            action_obj['action_attribute'] = dict()
            action_obj['action_attribute']['locations'] = [x['tilePosition'] for x in objects['banana']]
        elif 'apple' in objects:
            action_obj['action'] = 'eat'
            action_obj['action_attribute'] = dict()
            action_obj['action_attribute']['locations'] = [x['tilePosition'] for x in objects['apple']]
        else:
            action_obj['action'] = 'explore'
    return (action_obj['action'],action_obj)

def handle_player_sprites(state):
    actions = []
    for player in state:
        actions.append(control_player(player))
    return actions
    