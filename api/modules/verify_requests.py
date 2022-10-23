from flask import jsonify

from statics.constants import *


def verify_request_keys(keys_in: dict, keys: list):
    """Check if request has all necessary keys"""
    return set(keys_in.keys()).issubset(keys)


def verify_code_create_request(json_request):
    if not verify_request_keys(json_request, COJI_CREATE_REQUEST_KEYS):
        print('STATUS: Missing required keys')
        return jsonify(error=422, text='Missing required keys', notify_user=False), 422

    if json_request['data-type'] not in COJI_DATA_TYPES:
        print('STATUS: Unsupported type')
        return jsonify(error=415, text='Unsupported type', notify_user=False), 415

    if json_request['style-info']['name'] not in COJI_STYLE_NAMES:
        print('STATUS: Wrong style name')
        return jsonify(error=415, text='Unsupported style', notify_user=False), 415

    return True


def verify_code_update_request(json_request):
    if not verify_request_keys(json_request, COJI_UPDATE_REQUEST_KEYS):
        print('STATUS: Missing required keys')
        return jsonify(error=422, text='Missing required keys', notify_user=False), 422

    if len(json_request['code-id']) != 16:
        print('STATUS: Wrong code id')
        return jsonify(error=415, text='Wrong code id', notify_user=False), 422

    if json_request['style-info']['name'] not in COJI_STYLE_NAMES:
        print('STATUS: Wrong style name')
        return jsonify(error=415, text='Unsupported style', notify_user=False), 415

    return True


def verify_code_decode_request(json_request):
    if not verify_request_keys(json_request, COJI_DECODE_REQUEST_KEYS):
        print('STATUS: Missing required keys')
        return jsonify(error=422, text='Missing required keys', notify_user=False), 422

    if json_request['decode-type'] not in COJI_DECODE_TYPES:
        print('STATUS: Unsupported type')
        return jsonify(error=415, text='Unsupported type', notify_user=False), 415

    if json_request['decode-type'] == 'keyboard' and json_request['style-info']['name'] not in COJI_STYLE_NAMES:
        print('STATUS: Wrong style name')
        return jsonify(error=415, text='Unsupported style', notify_user=False), 415

    return True
