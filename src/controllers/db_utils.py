'''
Created on 30 Oct 2023

@author: Atrisha
'''

import sqlite3

def get_last_update_time():
    conn = sqlite3.connect('E:\\phaser-game-dev\\altar_game\\data\database\\episodes.db')
    cursor = conn.cursor()
    
    try:
        # Execute a SELECT query
        cursor.execute("SELECT MAX(obs_time_end) FROM policy_updates")
        
        # Fetch all results from the executed SQL query
        rows = cursor.fetchall()
        
        # Create a list to store the data
        data_list = []
        
        # Loop through the rows and add each row to the list
        for row in rows:
            data_list.append(row)
            
        return 0 if data_list[0][0] is None else data_list[0][0]
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        # Close the database connection
        conn.close()
        
def get_max_id():
    conn = sqlite3.connect('E:\\phaser-game-dev\\altar_game\\data\database\\episodes.db')
    cursor = conn.cursor()
    
    try:
        # Execute a SELECT query
        cursor.execute("SELECT MAX(id) FROM player_observations")
        
        # Fetch all results from the executed SQL query
        rows = cursor.fetchall()
        
        # Create a list to store the data
        data_list = []
        
        # Loop through the rows and add each row to the list
        for row in rows:
            data_list.append(row)
            
        return 0 if data_list[0][0] is None else data_list[0][0]
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        # Close the database connection
        conn.close()