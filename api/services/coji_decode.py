import difflib

from flask import Blueprint
from flask import jsonify
from flask import request
from geopy.geocoders import Nominatim

from modules import recognize_code
from modules.db_operations import (
    find_code,
    get_all_keys,
    get_code,
    get_by_city
)
from modules.recognize_code_style import detect_style
from modules.verify_requests import verify_code_decode_request
from statics.commons import (
    get_style_info,
    string_img_to_cv2
)
from statics.constants import RESPONSE_DECODE_ERROR_DICTS as RDED

coji_decode_bp = Blueprint('coji-decode', __name__)


@coji_decode_bp.route('/decode', methods=['get', 'post'])
def coji_decode():
    """Decode and return if code exist"""
    json_request = request.json
    print('REQUEST| DECODE')

    request_check = verify_code_decode_request(json_request)
    if type(request_check) is not bool:
        return request_check

    print(json_request['user-data'])
    char_code = None
    decode_type = json_request['decode-type']

    if decode_type in ('image', 'scan'):
        image_str = json_request['in-data']
        if 'data:image/' in image_str:  # if image contains a tag
            image_str = image_str.split(',')[1]
        img = string_img_to_cv2(image_str)
        if type(img) is bool:
            return jsonify(error=404, text=f'Corrupted image', notify_user=False), 422

        style_name = detect_style(img)
        style_module = get_style_info(style_name)
        style_module['style-info'].update(json_request['style-info'])

        try:
            char_code = recognize_code(img, style_module)  # recognize code on image
        except Exception as e:
            print(e)
            char_code = None

    elif decode_type == 'keyboard':
        style_name = json_request['style-info']['name']
        char_code = json_request['in-data'].lower()

    if not char_code:
        print('STATUS: bad image')
        return jsonify(error=404, text='Code not found :(\nPlease try again!', notify_user=False), 422

    print('Code found:', char_code)

    all_keys = get_all_keys()
    code_guess = difflib.get_close_matches(char_code, all_keys)
    if not len(code_guess):
        print('No db matches...')
        return jsonify(error=404, text=f'{RDED[decode_type]}, please try again!', notify_user=False), 422

    code_guess = code_guess[0]
    print('Code guess:', code_guess)

    similarity = difflib.SequenceMatcher(None, char_code, code_guess).ratio()

    print('Similarity:', similarity)

    if similarity < 0.5:
        return jsonify(error=404, text=f'{RDED[decode_type]}, please try again!', notify_user=False), 422

    code_exists = find_code(code_guess)
    if code_exists is None:
        return jsonify(error=404, text=f'This code no longer exists!\nCode:{char_code}', notify_user=False), 422

    print('STATUS: success')
    print('---------------')

    resp = jsonify({
        'error': False,
        'code-id': code_guess,
    })
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp, 200


@coji_decode_bp.route('/get/<id>', methods=['get'])
def coji_get(id):
    """Get all the info about code by id"""
    print('REQUEST| GET', id)
    if len(id) > 16:
        print('STATUS: Bad id')
        return jsonify(error=415, text='Bad id', notify_user=False), 415

    code_data = get_code(id)
    if code_data is None:
        return jsonify(error=404, data={}, notify_user=False), 422
    print('STATUS: success')
    print('---------------')
    return jsonify({
        'error': False,
        'data': code_data,
    }), 200


@coji_decode_bp.route('/get-by-city/<location>', methods=['get'])
def coji_get_by_city(location):
    """Get all the codes in the city"""
    print('REQUEST| GET BY CITY', location)
    geolocator = Nominatim(user_agent="geoapiExercises")
    address = geolocator.reverse(location).raw['address']
    city = address.get('ISO3166-2-lvl4', None)
    codes = get_by_city(city)
    codes = {k: v['location'] for k, v in codes.items()}
    return jsonify({
        'error': False,
        'data': codes,
    }), 200
