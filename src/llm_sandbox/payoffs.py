import numpy as np
import pandas as pd
from scipy.special import softmax

# Function to convert integer to 4-bit binary representation
def int_to_binary_array(arm):
    return [int(digit) for digit in format(arm, '04b')]

# Function to calculate the payoff for a pair of actions
def calculate_payoff(action1, action2):
    # Unpack actions
    eat_apple1, eat_banana1, punish_green1, punish_normal1 = tuple(char == '1' for char in action1)
    eat_apple2, eat_banana2, punish_green2, punish_normal2 = tuple(char == '1' for char in action2)
    # Initialize scores
    score1, score2 = 0, 0

    # Eating an apple or a banana gives 10 points
    if eat_apple1 or eat_banana1:
        score1 += 10
    if eat_apple2 or eat_banana2:
        score2 += 10

    # Eating a banana turns the player green
    is_green1 = eat_banana1
    is_green2 = eat_banana2
    '''
    if is_green1:
        score1 -= 10
    if is_green2:
        score2 -= 10
    '''
    '''
    if punish_green1:
      score1 -= 5
    if punish_green2:
      score2 -= 5
    
    if punish_normal1:
      score1 -= 5
    if punish_normal2:
      score2 -= 5
    '''
    # Punishing a green player gives 10 points, punishing a normal player loses 10 points
    '''
    if punish_green1:
        score1 += 10
    
    if punish_green2:
        score2 += 10
    '''
    '''
    if punish_green1 and is_green2:
        score2 -= 20
        score1 += 15
    if punish_green2 and is_green1:
        score1 -= 20
        score2 += 15
    
    if punish_normal1 and not is_green2:
        score2 -= 20
        score1 -= 5
    if punish_normal2 and not is_green1:
        score1 -= 20
        score2 -= 5
    '''
    # silly rule condition
    if punish_green1 and is_green2:
        score2 -= 20
        score1 += 5
    if punish_green2 and is_green1:
        score1 -= 20
        score2 += 5
    
    if punish_normal1 and not is_green2:
        score2 -= 20
        score1 += 5
    if punish_normal2 and not is_green1:
        score1 -= 20
        score2 += 5
    #print(action1,action2,score1,score2)
    return score1, score2

def generate_payoff_dict():
    
    # Create a 16x16 payoff matrix
    payoff_table = []
    
    for i in range(16):
        row = []
        for j in range(16):
            action1 = format(i, '04b')
            action2 = format(j, '04b')
            payoff = calculate_payoff(action1, action2)
            row.append(payoff)
        payoff_table.append(row)
    
    # Convert to pandas DataFrame for pretty display
    df_payoff_table = pd.DataFrame(payoff_table, columns=[format(i, '04b') for i in range(16)], index=[format(i, '04b') for i in range(16)])
    #print(df_payoff_table)
    payoff_table_np = np.asarray(payoff_table)[:,:,0]
    # Define a custom green-ish colormap
    #cmap = LinearSegmentedColormap.from_list('greenish', ['white', 'darkgreen'], N=256)
    
    # Create the heatmap with the custom colormap and reversed color intensity
    #plt.imshow(payoff_table_np, cmap=cmap, interpolation='nearest')
    
    # Add colorbar
    #plt.colorbar()
    k = np.sum(payoff_table_np,axis=1)
    exp_payoffs = np.sum(payoff_table_np,axis=1)
    np.set_printoptions(precision=1)
    sampling_probs = softmax(exp_payoffs)
    
    #print(payoff_table)
    
    # Convert the payoff_table to a dictionary
    payoff_dict = {}
    
    # Using the provided payoff_table, which is a list of lists, we can convert this to a dictionary
    # where each key is a tuple of action strings (binary representations) and the value is the payoff list
    #for i in np.arange(10):
    for i, row in enumerate(payoff_table):
        for j, payoff in enumerate(row):
            action1 = format(i, '04b')
            action2 = format(j, '04b')
            payoff_dict[(action1, action2)] = list(payoff)
    return payoff_dict,sampling_probs
    
