"""User-related constants & utils"""
from nicegui import app

# Keys of app.storage.user
AUTH_STATUS_KEY = "is_logged"
USERNAME_KEY = "username"
TARGETED_PAGE_KEY = "target_page"


def init_user_storage() -> None:
    """Init user storage with default values"""
    if AUTH_STATUS_KEY not in app.storage.user:
        app.storage.user.update({AUTH_STATUS_KEY: False})
    if USERNAME_KEY not in app.storage.user:
        app.storage.user.update({USERNAME_KEY: None})
