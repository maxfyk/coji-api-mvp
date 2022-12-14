import difflib
import os.path
import traceback

from flask import Blueprint
from flask import jsonify
from flask import request, send_file
from geopy.geocoders import Nominatim
from threading import Thread
from modules import recognize_code
from modules import stats_logger
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

    decode_data = json_request.get('user-data', None)
    if decode_data:
        decode_data = json_request.pop('user-data')
    char_code = None
    decode_type = json_request['decode-type']

    if decode_type in ('image', 'scan'):
        image_str = json_request['in-data']
        if 'data:image/' in image_str:  # if image contains a tag
            image_str = image_str.split(',')[1]
        img = string_img_to_cv2(image_str)
        if type(img) is bool:
            if decode_data:
                decode_data['code'] = None
                decode_data['error'] = 'Corrupted image'
                Thread(target=stats_logger.add_decode_request, args=(decode_data,)).start()
            return jsonify(error=404, text=f'Corrupted image', notify_user=False), 422

        style_name = detect_style(img)
        style_module = get_style_info(style_name)
        style_module['style-info'].update(json_request['style-info'])
        try:
            char_code = recognize_code(img, style_module)  # recognize code on image
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            char_code = None

    elif decode_type == 'keyboard':
        style_name = json_request['style-info']['name']
        char_code = json_request['in-data'].lower()

    if not char_code:
        print('STATUS: bad image')
        if decode_data:
            decode_data['code'] = None
            decode_data['error'] = 'Code not found'
            Thread(target=stats_logger.add_decode_request, args=(decode_data,)).start()
        return jsonify(error=404, text='Code not found :(\nPlease try again!', notify_user=False), 422

    print('Code found:', char_code)

    all_keys = get_all_keys()
    code_guess = difflib.get_close_matches(char_code, all_keys)
    if not len(code_guess):
        print('No db matches...')
        if decode_data:
            decode_data['code'] = None
            decode_data['error'] = RDED[decode_type]
            Thread(target=stats_logger.add_decode_request, args=(decode_data,)).start()
        return jsonify(error=404, text=f'{RDED[decode_type]}, please try again!', notify_user=False), 422

    code_guess = code_guess[0]
    print('Code guess:', code_guess)

    similarity = difflib.SequenceMatcher(None, char_code, code_guess).ratio()

    print('Similarity:', similarity)

    if similarity < 0.5:
        if decode_data:
            decode_data['code'] = None
            decode_data['error'] = RDED[decode_type]
            Thread(target=stats_logger.add_decode_request, args=(decode_data,)).start()
        return jsonify(error=404, text=f'{RDED[decode_type]}, please try again!', notify_user=False), 422

    code_exists = find_code(code_guess)
    if code_exists is None:
        if decode_data:
            decode_data['code'] = code_guess
            decode_data['error'] = 'Expired'
            Thread(target=stats_logger.add_decode_request, args=(decode_data,)).start()
        return jsonify(error=404, text=f'This code no longer exists!\nCode:{char_code}', notify_user=False), 422

    if decode_data:
        decode_data['code'] = code_guess
        decode_data['error'] = None
        Thread(target=stats_logger.add_decode_request, args=(decode_data,)).start()
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


@coji_decode_bp.route('/get-asset/<code_id>/<asset_name>', methods=['get'])
def coji_get_asset(code_id, asset_name):
    """Return ar-preview asset"""
    print(f'REQUEST| GET ASSET {code_id} / {asset_name}')
    if len(code_id) != 16 and code_id != 'model':
        print('ERROR| BAD ID')
        return jsonify(error=415, text='Bad id', notify_user=False), 415
    if code_id == 'model':
        if not os.path.isfile(f'/app/assets/models/{asset_name}'):
            print('ERROR| FILE NOT FOUND')
            return jsonify(error=404, text='File not found', notify_user=False), 404

        return send_file(f'/app/assets/models/{asset_name}')

    else:
        if '.' not in asset_name:
            print('ERROR| BAD ASSET NAME')
            return jsonify(error=404, text='Bad asset name', notify_user=False), 404

        if not os.path.isfile(f'/app/assets/{code_id}/{asset_name}'):
            print('ERROR| FILE NOT FOUND')
            return jsonify(error=404, text='File not found', notify_user=False), 404

        return send_file(f'/app/assets/{code_id}/{asset_name}')
