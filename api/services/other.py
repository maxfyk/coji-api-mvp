from flask import Blueprint
from flask import jsonify

other = Blueprint('other', __name__)


@other.route('/<code_id>/<feedback>/', methods=['POST'])
def coji_code_feedback(code_id, feedback):
    """Update feedback"""
    print('REQUEST| FEEDBACK')

    print('STATUS: success')
    return jsonify({
        'error': False,
        'feedback': feedback,
    }), 200
