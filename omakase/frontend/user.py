"""User-related constants & utils"""
from nicegui import app

# Keys of app.storage.user
AUTH_STATUS_KEY = "is_logged"
AUTH_STATUS_DEFAULT = False
USERNAME_KEY = "username"
USERNAME_DEFAULT = None
LAST_SELECTED_DECK_KEY = "last_selected_deck"
LAST_SELECTED_DECK_DEFAULT = None


def init_user_storage() -> None:
    """Init user storage with default values"""
    if AUTH_STATUS_KEY not in app.storage.user:
        app.storage.user.update({AUTH_STATUS_KEY: AUTH_STATUS_DEFAULT})
    if USERNAME_KEY not in app.storage.user:
        app.storage.user.update({USERNAME_KEY: USERNAME_DEFAULT})
    if LAST_SELECTED_DECK_KEY not in app.storage.user:
        app.storage.user.update({LAST_SELECTED_DECK_KEY: LAST_SELECTED_DECK_DEFAULT})
