"""User-related constants & utils"""
from nicegui import app

# Keys of the web user storage
AUTH_STATUS_KEY = "is_logged"
AUTH_STATUS_DEFAULT = False
OM_USERNAME_KEY = "username"
OM_USERNAME_DEFAULT = None


# =========================
# Storage-specific function
# =========================
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


# =============================
# Storage-independent functions
# =============================
def init_missing_web_user_storage() -> None:
    """Init missing web user storage with default values"""
    web_user_data = point_to_web_user_data()
    if AUTH_STATUS_KEY not in web_user_data:
        web_user_data.update({AUTH_STATUS_KEY: AUTH_STATUS_DEFAULT})
    if OM_USERNAME_KEY not in web_user_data:
        web_user_data.update({OM_USERNAME_KEY: OM_USERNAME_DEFAULT})
