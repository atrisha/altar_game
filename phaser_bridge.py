from flask import Flask, render_template, jsonify, request, send_file
from controllers.player_controllers import handle_player_sprites, insert_observation_data
from PIL import Image
import time

app = Flask(__name__)
direction = "none"

req_ctr = 0
prev_state,prev_action,prev_score = None, None, None

@app.route('/')
def index():
    path_to_html_file = "./static/index_arcade.html"
    return send_file(path_to_html_file)

@app.route('/get-direction')
def get_direction():
    print('here')
    return jsonify({'direction': direction})

@app.route('/state-dispatch', methods=['POST'])
def send_sprite_state():
    global req_ctr,prev_state,prev_action,prev_score
    '''
    file_data = request.files['image']
    if file_data:
        # Save the file temporarily
        file_data.save('./temp/output'+str(req_ctr)+'.png')
        
        # Open and show the image using PIL
        img = Image.open('./temp/output'+str(req_ctr)+'.png')
        img.show()
    '''
    sprite_state = request.json
    req_ctr += 1
    print('received state information',req_ctr)
    player_actions = handle_player_sprites(sprite_state)
    if prev_score is not None and [x['score'] for x in sprite_state][0]-prev_score < 0:
        f=1
    if req_ctr > 1:
        insert_observation_data(prev_state,prev_action,[x['score'] for x in sprite_state],req_ctr-1)
    prev_state = sprite_state
    prev_score = [x['score'] for x in sprite_state][0]
    prev_action = [x[1] for x in player_actions]
    print('sent actions',[x[0] for x in player_actions])
    print('sent attributes',[x[1]['action_attribute']['locations'] if x[0] in ['eat','avoid'] else None for x in player_actions])
    #player_actions_list = [{"Xv": xv, "Yv": yv} for xv, yv in player_actions]
    # Process the sprite state
    # For example, you might check conditions or store data
    player_actions_list = player_actions
    resp_json = jsonify({
        'status': 'success',
        'resp_id': req_ctr,
        'player_actions': [x[1] for x in player_actions_list]
        
    })
    print(player_actions_list)
    return resp_json

if __name__ == '__main__':
    app.run(debug=True,port=8000)
