from flask import Flask, render_template, jsonify, request, send_file
from controllers.player_controllers import handle_player_sprites
from PIL import Image
import time

app = Flask(__name__)
direction = "none"

req_ctr = 0

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
    global req_ctr
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
    #player_actions_list = [{"Xv": xv, "Yv": yv} for xv, yv in player_actions]
    # Process the sprite state
    # For example, you might check conditions or store data
    player_actions_list = player_actions
    resp_json = jsonify({
        'status': 'success',
        'resp_id': req_ctr,
        'player_actions': player_actions_list
    })
    return resp_json

if __name__ == '__main__':
    app.run(debug=True,port=8000)
