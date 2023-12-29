"""User-related constants & utils"""
from nicegui import app

# Keys of app.storage.user
AUTH_STATUS_KEY = "is_logged"
AUTH_STATUS_DEFAULT = False
USERNAME_KEY = "username"
USERNAME_DEFAULT = None
LAST_SELECTED_DECK_KEY = "last_selected_deck"
LAST_SELECTED_DECK_DEFAULT = None


def point_to_web_user_data() -> dict:
    """
    Point to the in-memory data dict for the web user (cookie level)

    Can be changed to handle data differently (i.e., use redis.)
    The function must point to collection. It is possible to supercharge a collection
    (i.e., dict) to write asynchronously to a database (i.e., redis) at every write.
    This is what NiceGUI does behind the scene (writes to json at every change; the data
    are, of course, persisted in memory.)
    """
    return app.storage.user


def init_user_storage() -> None:
    """Init user storage with default values"""
    web_user_data = point_to_web_user_data()
    if AUTH_STATUS_KEY not in web_user_data:
        web_user_data.update({AUTH_STATUS_KEY: AUTH_STATUS_DEFAULT})
    if USERNAME_KEY not in web_user_data:
        web_user_data.update({USERNAME_KEY: USERNAME_DEFAULT})
    if LAST_SELECTED_DECK_KEY not in web_user_data:
        web_user_data.update({LAST_SELECTED_DECK_KEY: LAST_SELECTED_DECK_DEFAULT})
