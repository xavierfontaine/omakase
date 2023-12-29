from nicegui import app

# Keys of the omakase user storage
LAST_SELECTED_DECK_KEY = "last_selected_deck"
LAST_SELECTED_DECK_DEFAULT = None


# =========================
# Storage-specific function
# =========================
def point_to_om_user_data(om_username: str) -> dict:
    """
    Point to the in-memory data dict for the omakase user

    Can be changed to handle data differently (i.e., use redis.)
    The function must point to collection. It is possible to supercharge a collection
    (i.e., dict) to write asynchronously to a database (i.e., redis) at every write.
    This is what NiceGUI does behind the scene (writes to json at every change; the data
    are, of course, persisted in memory.)
    """
    if om_username not in app.storage.general:
        app.storage.general[om_username] = dict()
    return app.storage.general[om_username]


# =============================
# Storage-independent functions
# =============================
def init_missing_om_user_storage(om_username: str) -> None:
    """Init missing keys in omakase user storage with default values"""
    om_user_data = point_to_om_user_data(om_username=om_username)
    if LAST_SELECTED_DECK_KEY not in om_user_data:
        om_user_data.update({LAST_SELECTED_DECK_KEY: LAST_SELECTED_DECK_DEFAULT})
