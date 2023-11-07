from flask import Flask, render_template, jsonify, request, send_file
from controllers.player_controllers import handle_player_sprites, insert_observation_data
from PIL import Image
import time
import controllers.llm_controls
from controllers import llm_controls,db_utils
import webbrowser
import importlib.util
import os
import sys
from pathlib import Path

# Calculate the path to the src directory from the perspective of a.py
src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(src_path))

# Now you can import p
import phaser_env_bridge


def create_instance_from_path(module_path, class_name, *args, **kwargs):
    """
    Creates an instance of the specified class from the given module path.

    :param module_path: The file system path to the Python module file.
    :param class_name: The name of the class to instantiate.
    :param args: Any positional arguments to pass to the class constructor.
    :param kwargs: Any keyword arguments to pass to the class constructor.
    :return: An instance of the specified class.
    """
    module_name = os.path.basename(module_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, class_name)
    instance = cls(*args, **kwargs)
    return instance




app = Flask(__name__)
direction = "none"

url = 'localhost:8000'

req_ctr = 0
prev_state,prev_action,prev_score,curr_policy = None, None, None, None

custom_env = None
'''
def register_env(env_path,env_class):
    global env
    instance = create_instance_from_path(env_path,env_class)
    custom_env = instance
'''
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
    global req_ctr,prev_state,prev_action,prev_score,curr_policy,custom_env
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
    sprite_state = request.json['player_data']
    events = request.json['event_data']
    if len(events) > 0:
        f=1
    print('received state information',req_ctr)
    
    phaser_env_bridge.phaser_to_env_queue.put({req_ctr:{'sprite_state':sprite_state,'events':events}})
    resp_json = phaser_env_bridge.env_to_phaser_queue.get()
    resp_json = resp_json[req_ctr]
    resp_json = jsonify(resp_json)
    req_ctr += 1
    
    return resp_json

#if __name__ == '__main__':
    #register_env('env/AltarEnv.py','AltarMARLEnv')
def start_app():
    app.run(debug=False,port=8000)
    
