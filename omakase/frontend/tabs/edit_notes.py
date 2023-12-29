"""
Statistics tab
"""
from nicegui import ui

from omakase.backend.notes import ManipulateDecks
from omakase.frontend.tabs.utils import TabContent
from omakase.frontend.web_user import (
    LAST_SELECTED_DECK_DEFAULT,
    LAST_SELECTED_DECK_KEY,
    USERNAME_DEFAULT,
    USERNAME_KEY,
    point_to_web_user_data,
)
from omakase.om_logging import logger


class EditNotesContent(TabContent):
    def __init__(self) -> None:
        self.web_user_data = point_to_web_user_data()
        self.username = self.web_user_data.get(USERNAME_KEY)
        self.deck_manipulator = ManipulateDecks(om_username=self.username)

    def _user_is_logged(self) -> bool:
        return self.username != USERNAME_DEFAULT

    def _a_deck_exists(self) -> bool:
        return self.deck_manipulator.list_decks() != []

    def _sanity_last_used_deck_in_storage(self):
        """Handle the special cases where no deck name is stored in memory, or if that
        deck doesn't exist anymore"""
        current_last_selected_deck = self.web_user_data.get(LAST_SELECTED_DECK_KEY)
        deck_list = self.deck_manipulator.list_decks()
        if (current_last_selected_deck == LAST_SELECTED_DECK_DEFAULT) | (
            current_last_selected_deck not in deck_list
        ):
            self.web_user_data.update({LAST_SELECTED_DECK_KEY: deck_list[0]})

    def _display_if_logged(self) -> None:
        # If no user name, leave page blank
        if not self._user_is_logged():
            ui.label("You are not logged in.")
            logger.critical(
                "Potential security breach: user triggered EditNotesContent without"
                " being logged."
            )
            return None
        # If no deck, leave the page blank
        if not self._a_deck_exists():
            ui.label("No deck available. Have you synced them with our server?")
            return None
        # Ensure the "last selected deck" in user storage makes sense
        self._sanity_last_used_deck_in_storage()
        # Deck name selector. [Save/use the last] deck.
        ui.select(options=self.deck_manipulator.list_decks()).bind_value(
            target_object=self.web_user_data, target_name=LAST_SELECTED_DECK_KEY
        )
        # Select the card. Have filter systems with agrid.
        # TODO
        # Select the mnem style. [Save/use the last] mnem style for the card type.
        # TODO
        # Select the fields that relate to the important items for that mnem style.
        # [Save/use the last] fields for that card type > mnem style.
        # Edit pane
        # TODO
