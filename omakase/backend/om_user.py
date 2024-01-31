"""
Handling of the omakase user data

All data are considered persisted.
"""
from abc import abstractmethod
from types import MappingProxyType
from typing import Any

from nicegui import app

from omakase.annotations import DeckName, OmDeckFilterUiLabel
from omakase.backend.decks import DeckFilters
from omakase.observer_logic import Observable

# from omakase.annotations import DeckName
# from omakase.backend.decks import DeckFilter, DeckFilters
# from omakase.om_logging import logger

# Keys of the omakase user storage
USER_CACHES_KEY = "user_caches"
LAST_SELECTED_DECK_KEY = "last_selected_deck"
LAST_SELECTED_DECK_DEFAULT = None
DECK_UI_FILTER_CORR_KEY = "deck_filter_correspondance"
MNEM_NOTE_ASSOCS_KEY = "mnemn_note_assocs"
PROMPT_NOTE_ASSOCS_KEY = "prompt_note_assocs"
GENOUT_NOTE_ASSOCS_KEY = "genout_note_assocs"


# =========================
# Storage-specific function
# =========================
def _point_to_om_user_caches() -> dict:
    if USER_CACHES_KEY not in app.storage.general:
        app.storage.general[USER_CACHES_KEY] = dict()
    return app.storage.general[USER_CACHES_KEY]


def point_to_om_user_cache(om_username: str) -> dict:
    """
    Point to the in-memory data dict for the omakase user

    Can be changed to handle data differently (i.e., use redis.)
    The function must point to collection. It is possible to supercharge a collection
    (i.e., dict) to write asynchronously to a database (i.e., redis) at every write.
    This is what NiceGUI does behind the scene (writes to json at every change; the data
    are, of course, persisted in memory.)
    """
    user_caches = _point_to_om_user_caches()
    if om_username not in user_caches:
        user_caches[om_username] = dict()
    return user_caches[om_username]


# =============================
# Storage-independent functions
# =============================
# TODO: eliminate the remainder
def init_missing_om_user_cache(om_username: str) -> None:
    """Init missing keys in omakase user storage with default values"""
    om_user_data = point_to_om_user_cache(om_username=om_username)
    if LAST_SELECTED_DECK_KEY not in om_user_data:
        om_user_data[LAST_SELECTED_DECK_KEY] = LAST_SELECTED_DECK_DEFAULT


# ======================
# NiceGui-based subjects
# ======================
# TODO: attempting to makes this more general:
# 1/ Should be able to pass more kw arguments to __init__ (feasible through kwargs)
# 2/ The configuration of the state can be done through those kwargs
# In the end, this will reduce the level of factorization (less DRY), but make it more
# flexible (more AHA.)
class CachedOmUserData(Observable):
    """Subject pointing to user data in app.storage.general

    The data is accessed/edited through the `state` attribute.
    """

    def __init__(self, om_username: str, default_value: Any = None):
        # Initialization
        self.default_value = default_value
        # Pointer to user cache
        self._user_cache = point_to_om_user_cache(om_username=om_username)
        # Sanitization
        self._handle_missing_subject_key()

    @property
    @abstractmethod
    def _root_dict(self) -> dict:
        """Dict to which `self.subject_key` belongs.

        Usually relies on self._user_cache."""
        pass

    @property
    @abstractmethod
    def _subject_key(self) -> str:
        """Key identifying the state in self._root_dict"""
        pass

    @property
    def state(self) -> Any:
        """State variable"""
        return self._root_dict[self._subject_key]

    @state.setter
    def state(self, value: Any) -> None:
        self._root_dict[self._subject_key] = value

    def _handle_missing_subject_key(self) -> None:
        if self._subject_key not in self._root_dict:
            self._root_dict[self._subject_key] = self.default_value


# ========================
# Subject - implementation
# ========================
# TODO: add default here, since LAST_SELECTED_DECK_DEFAULT exists
class LastSelectedDeck(CachedOmUserData):
    def __init__(self, *args, **kwargs):
        # Override to specify expected type
        self.state: DeckName
        super().__init__(*args, **kwargs)

    @property
    def _subject_key(self) -> str:
        return LAST_SELECTED_DECK_KEY

    @property
    def _root_dict(self) -> dict:
        return self._user_cache


# TODO: maybe for DeckFilterCorr, and certainly for MnemonicNoteFieldMapData, create a
# specific Subject Child. The OmUserNgCachedSubject works only in the simplest case.
# TODO: for MnemonicNoteFieldMapData, get closer to what I did for DeckFilterCorr


class DeckFilterCorr(Observable):
    def __init__(self, om_username: str):
        # Pointer to user cache
        self._user_cache = point_to_om_user_cache(om_username=om_username)
        # Hidden state
        self._state: dict[DeckName, OmDeckFilterUiLabel] = self._initialize_state()

    @property
    def state(self) -> MappingProxyType[dict[DeckName, OmDeckFilterUiLabel]]:
        return MappingProxyType(self._state)

    def _initialize_state(self) -> dict[DeckName, OmDeckFilterUiLabel]:
        if DECK_UI_FILTER_CORR_KEY not in self._user_cache:
            self._user_cache[DECK_UI_FILTER_CORR_KEY] = {}
        return self._user_cache[DECK_UI_FILTER_CORR_KEY]

    def set_filter_for_deck(
        self, deck_name: DeckName, ui_filter_name: OmDeckFilterUiLabel
    ) -> None:
        self._state[deck_name] = ui_filter_name

    def get_filter_for_deck(self, deck_name: DeckName) -> OmDeckFilterUiLabel:
        """Default to the ui label for all_notes"""
        if deck_name not in self._state:
            self._state[deck_name] = DeckFilters().all_notes.ui_label
        return self._state[deck_name]


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
#     def set_prefered_filter(
#       self, deck_name: DeckName, new_filter: DeckFilter
#     ) -> None:
#         # TODO: implement
#         # BEGIN MOCK
#         logger.info(f"Pretend to change prefered filter to {new_filter=}")
#         # END MOCK
