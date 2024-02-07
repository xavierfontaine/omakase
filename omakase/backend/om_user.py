"""
Handling of the omakase user data

All data are considered persisted.
"""
from typing import Any, Callable, Optional

from nicegui import app

from omakase.annotations import DeckName
from omakase.backend.decks import DeckFilters
from omakase.observer_logic import Observable

# Keys of the omakase user storage
USER_CACHES_KEY = "user_caches"
LAST_SELECTED_DECK_KEY = "last_selected_deck"
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


# TODO: test
def point_to_om_user_subcache(om_username: str, keys: list[str]) -> dict:
    """
    Point to a subdict of the omakase user data

    Create the path if it does not exist, and initialize with an empty dictionary
    """
    om_user_data = point_to_om_user_cache(om_username=om_username)
    pointer = om_user_data
    path = []
    for k in keys:
        if k not in pointer:
            pointer[k] = {}
        elif not isinstance(pointer[k], dict):
            path_str = "[" + "][".join(path + [k]) + "]"
            raise TypeError(
                f"Path {path_str} exists in the user data, but is not a dict"
            )
        pointer = pointer[k]
        path.append(k)
    return pointer


# ================
# Cached datapoint
# ================
class CachedUserDataPoint:
    """User-related data point, synced with app.storage.general

    Data is accessible and editable through the `value` attribute.
    This construct simplifies the use of nicegui's `bind_*` methods.

    `on_change` defines a function to call upon changes.
    """

    def __init__(
        self,
        om_username: str,
        root_keys: list[str],
        subject_key: str,
        default_value: Any,
        on_change: Optional[Callable] = None,
    ) -> None:
        # Initialization
        self._default_value = default_value
        self._subject_key = subject_key
        self._on_change = on_change
        # Pointer to user cache
        self._user_cache = point_to_om_user_cache(om_username=om_username)
        # Get root dict
        self._root_dict = self._resolve_root_dict(root_keys=root_keys)
        # Sanitization
        self._handle_missing_subject_key()

    @property
    def value(self) -> Any:
        return self._root_dict[self._subject_key]

    def _resolve_root_dict(self, root_keys: str) -> dict:
        """Point to the part of the user  cache described by root_keys

        Create non-existing dict on the way"""
        pointer = self._user_cache
        for k in root_keys:
            if k not in pointer:
                pointer[k] = {}
            pointer = pointer[k]
        return pointer

    @value.setter
    def value(self, value: Any) -> None:
        self._root_dict[self._subject_key] = value
        if self._on_change is not None:
            self._on_change()

    def _handle_missing_subject_key(self) -> None:
        if self._subject_key not in self._root_dict:
            self._root_dict[self._subject_key] = self._default_value


# # ======================
# # Subject - abstractions
# # ======================
# class ObservableCachedDpPointer(Observable):
#     """Observable pointer to a CachedUserDataPoint
#
#     Get the pointer through `get_dp_pointer`. Changes in the value of the
#     CachedUserDataPoint will trigger `self.notify`
#     """
#     def __init__(self, om_username: str) -> None:
#         self._om_username = om_username
#
#     @property
#     @abstractmethod
#     def _root_keys(self) -> list[str]:
#         """As definied in CachedUserDataPoint"""
#         pass
#
#     @property
#     @abstractmethod
#     def _subject_key(self) -> str:
#         """As definied in CachedUserDataPoint"""
#         pass
#
#     @property
#     @abstractmethod
#     def _default_value(self) -> Any:
#         """As definied in CachedUserDataPoint"""
#         pass
#
#     def get_dp_pointer(self, *args, **kwargs) -> CachedUserDataPoint:
#         dp = CachedUserDataPoint(
#             om_username=self._om_username,
#             root_keys=self._root_keys,
#             subject_key=self._subject_key,
#             default_value=self._default_value,
#             on_change=self.notify,
#         )
#         return dp


# ========================
# Subject - implementation
# ========================
class LastSelectedDeckObl(Observable):
    """Observable for the last selected deck

    The deck name can be edited/accessed through `deck_name_dp`
    """

    def __init__(self, om_username: str) -> None:
        self._om_username = om_username

    @property
    def data(self) -> CachedUserDataPoint:
        return CachedUserDataPoint(
            om_username=self._om_username,
            default_value=None,
            root_keys=[],
            subject_key=LAST_SELECTED_DECK_KEY,
            on_change=self.notify,
        )


# TODO: maybe for DeckFilterCorr, and certainly for MnemonicNoteFieldMapData, create a
# specific Subject Child. The OmUserNgCachedSubject works only in the simplest case.
# TODO: for MnemonicNoteFieldMapData, get closer to what I did for DeckFilterCorr


class DeckFilterCorrObl(Observable):
    """Observable for the associations between decks and ui filter labels

    Associations are accessed/edited through `get_filter_dp`"""

    def __init__(self, om_username: str):
        self._om_username = om_username

    def get_filter_dp(self, deck_name: DeckName) -> CachedUserDataPoint:
        """Default to the ui label for all_notes"""
        default_value = DeckFilters().all_notes.ui_label
        dp = CachedUserDataPoint(
            om_username=self._om_username,
            root_keys=[DECK_UI_FILTER_CORR_KEY],
            subject_key=deck_name,
            default_value=default_value,
            on_change=self.notify,
        )
        return dp


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
