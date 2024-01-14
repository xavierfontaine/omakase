"""
Handling of the omakase user data

All data are considered persisted.
"""
from nicegui import app

from omakase.annotations import DeckName
from omakase.backend.decks import DeckFilter, DeckFilters
from omakase.om_logging import logger

# Keys of the omakase user storage
LAST_SELECTED_DECK_KEY = "last_selected_deck"
LAST_SELECTED_DECK_DEFAULT = None
DECK_FILTER_CORR_KEY = "deck_filter_correspondance"
DECK_FILTER_CORR_DEFAULT = {}


# =========================
# Storage-specific function
# =========================
def point_to_om_user_cache(om_username: str) -> dict:
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
def init_missing_om_user_cache(om_username: str) -> None:
    """Init missing keys in omakase user storage with default values"""
    om_user_data = point_to_om_user_cache(om_username=om_username)
    if LAST_SELECTED_DECK_KEY not in om_user_data:
        om_user_data[LAST_SELECTED_DECK_KEY] = LAST_SELECTED_DECK_DEFAULT
    if DECK_FILTER_CORR_KEY not in om_user_data:
        om_user_data[DECK_FILTER_CORR_KEY] = DECK_FILTER_CORR_DEFAULT


# TODO: reuse the below for writting to SQL db
# class PersistedJourneyPreferences:
#     """Read (write) user preferences from (to) the persisted storage"""
#
#     def __init__(self, om_username: str) -> None:
#         self._om_username = om_username
#         self._available_deck_filters = DeckFilters()
#
#     def get_prefered_filter(self, deck_name: DeckName) -> DeckFilter:
#         """User decks and their prefered filters"""
#         # TODO: implement
#         # TODO: think of logic when no prefered filter yet
#         # BEGIN MOCK
#         if self._om_username == "X":
#             if deck_name == "deck1":
#                 filt = self._available_deck_filters.new_notes
#             elif deck_name == "deck2":
#                 filt = self._available_deck_filters.in_learning_notes
#         # END MOCK
#         return filt
#
#     def set_prefered_filter(self, deck_name: DeckName, new_filter: DeckFilter) -> None:
#         # TODO: implement
#         # BEGIN MOCK
#         logger.info(f"Pretend to change prefered filter to {new_filter=}")
#         # END MOCK
