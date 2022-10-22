import os
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin


def init_db_app():
    """Initialize database"""
    cred = credentials.Certificate('/firebase_key.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ['FIREBASE_DB_URL']
    })
    return True


def get_db_session():
    """Return firebase db instance"""
    return db.reference()


def get_last_code(db_root=None):
    """Get data of latest code created"""
    if not db_root:
        db_root = get_db_session()
    val = None
    try:
        val = db_root.child('code').order_by_child('index').limit_to_last(1).get()
    except Exception as e:
        print(e)
        pass
    return val if val else {None: {'index': -1}}


def add_new_code(new_code, db_root=None):
    """Add new code to db"""
    if not db_root:
        db_root = get_db_session()
    code_id, data = tuple(new_code.items())[0]
    return db_root.child(f'code/{code_id}').set(data)


def update_code(code_id, in_data, db_root=None):
    """Update existing code"""
    if not db_root:
        db_root = get_db_session()
    code_exists = find_code(code_id)
    if code_exists:
        return db_root.child(f'code/{code_id}').update(in_data)
    return False


def find_code(code_id, child='index', db_root=None):
    """Check if code exists from db"""
    if not db_root:
        db_root = get_db_session()
    return db_root.child(f'code/{code_id}').child(child).get()


def get_code(code_id, db_root=None):
    """Get encoded data from db"""
    if not db_root:
        db_root = get_db_session()
    return db_root.child(f'code/{code_id}').get()


def get_all_keys(db_root=None):
    """Get list of all keys that currently exist"""
    if not db_root:
        db_root = get_db_session()
    return db_root.child('code').get(shallow=True)
