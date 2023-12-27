"""User-related constants & utils"""
from nicegui import app

LOG_STATUS_KEY = "is_logged"


def init_user_storage() -> None:
    """Init user storage with default values"""
    if LOG_STATUS_KEY not in app.storage.user:
        app.storage.user[LOG_STATUS_KEY] = False
