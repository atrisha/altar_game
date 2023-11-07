'''
Created on 7 Nov 2023

@author: Atrisha
'''
from queue import Queue

env_to_phaser_queue = Queue(maxsize = 1) 
phaser_to_env_queue = Queue(maxsize = 1) 