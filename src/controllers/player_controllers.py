'''
Created on 16 Oct 2023

@author: Atrisha
'''
import random


def control_player(state):
    return random.choice([(1,1),(0,1),(1,0),(0,0),
                          (-1,-1),(0,-1),(-1,0),
                          (1,-1),(-1,1)])

def handle_player_sprites(state):
    moves = []
    for player in state:
        moves.append(control_player(player))
    return moves
    