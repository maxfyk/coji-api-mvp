from statics.constants import COJI_DB_CODE_FIELDS


def prepare_code_info(code_request, char_code):
    """Prepare dict to be pushed into firebase db"""
    new_code = {char_code: {}}
    for field in COJI_DB_CODE_FIELDS:
        new_code[char_code][field] = code_request[field]
    return new_code
