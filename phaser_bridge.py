from flask import Flask, render_template, jsonify, request, send_file
from controllers.player_controllers import handle_player_sprites
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
    sprite_state = request.json
    req_ctr += 1
    print('received state information',req_ctr)
    player_actions = handle_player_sprites(sprite_state)
    player_actions_list = [{"Xv": xv, "Yv": yv} for xv, yv in player_actions]
    # Process the sprite state
    # For example, you might check conditions or store data
    resp_json = jsonify({
        'status': 'success',
        'resp_id': str(req_ctr),
        'player_actions': player_actions_list
    })
    return resp_json

if __name__ == '__main__':
    app.run(debug=True,port=8000)
