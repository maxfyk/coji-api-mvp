from flask import Blueprint
from flask import jsonify
from modules.db_operations import (
    update_feedback
)

other = Blueprint('other', __name__)


@other.route('/feedback/<code_id>/<feedback>/', methods=['post'])
def coji_code_feedback(code_id, feedback):
    """Update feedback"""
    print('REQUEST| FEEDBACK')
    update_feedback(code_id, feedback)
    print('STATUS: success')
    return jsonify({
        'error': False,
        'feedback': feedback,
    }), 200
