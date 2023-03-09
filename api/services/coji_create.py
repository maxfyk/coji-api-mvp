import os
import base64

from datetime import datetime

from flask import Blueprint
from flask import jsonify
from flask import request
from geopy.geocoders import Nominatim

from modules import (
    generate_code_id,
    generate_visual_code,
)
from modules.db_operations import add_new_code, get_last_code, update_code
from modules.formator import prepare_code_info
from modules.verify_requests import (
    verify_code_create_request,
    verify_code_update_request,
)
from statics.commons import get_style_info
from statics.constants import STYLES_PATH_FULL

coji_create_bp = Blueprint('coji-create', __name__)


@coji_create_bp.route('/create', methods=['POST'])
def coji_create():
    """Create a new code and return it as a jpeg image"""
    json_request = request.json
    print('REQUEST| CREATE')

    request_check = verify_code_create_request(json_request)
    if type(request_check) is not bool:
        return request_check

    json_request['location-city'] = None
    location = json_request.get('location')
    if location:
        geolocator = Nominatim(user_agent="geoapiExercises")
        address = geolocator.reverse(location).raw['address']
        json_request['location-city'] = address['ISO3166-2-lvl4']
        json_request['location'] = location

    json_request['time-created'] = json_request['time-updated'] = str(datetime.now())

    style_name = json_request['style-info']['name']
    style_module = get_style_info(style_name)
    style_module['style-info'].update(json_request['style-info'])

    _, index = get_last_code().popitem()
    index = index['index'] + 1
    char_code = generate_code_id(index, style_module['keys'], style_module['style-info'])  # generate random id
    img = generate_visual_code(style_module, char_code,
                               STYLES_PATH_FULL.format(style_name))  # create image
    json_request['index'] = index
    if json_request['data-type'] == '3d-object':
        obj = base64.b64decode(json_request['in-data'])
        with open(os.path.join(f'/app/assets/models/', f'{char_code}.{json_request["other"]}'), 'w', encoding="utf-8") as output_file:
            output_file.write(obj.decode('utf-8'))

        json_request[char_code]['in-data'] = os.path.join(char_code, f'.{json_request["other"]}')
    new_code = prepare_code_info(json_request, char_code)

    add_new_code(new_code)
    print(new_code)
    print('STATUS: success')
    return jsonify({
        'error': False,
        'code': char_code,
        'image': img,
    }), 200


@coji_create_bp.route('/update', methods=['POST'])
def coji_update():
    """Update old code's information"""
    json_request = request.json
    print('REQUEST| UPDATE')

    request_check = verify_code_update_request(json_request)
    if type(request_check) is not bool:
        return request_check

    json_request['time-updated'] = str(datetime.now())

    style_name = json_request['style-info']['name']
    style_module = get_style_info(style_name)
    style_module['style-info'].update(json_request['style-info'])

    code_id = json_request['code-id']
    del json_request['code-id']
    update_code(code_id, json_request)
    print('STATUS: success')
    return jsonify({
        'error': False,
    }), 200
