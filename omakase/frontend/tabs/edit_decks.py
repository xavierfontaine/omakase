"""
Statistics tab
"""
from dataclasses import fields

from nicegui import ui

from omakase.backend.decks import Card, ManipulateDecks
from omakase.backend.om_user import (
    LAST_SELECTED_DECK_DEFAULT,
    LAST_SELECTED_DECK_KEY,
    point_to_om_user_data,
)
from omakase.frontend.tabs.utils import TabContent
from omakase.frontend.web_user import OM_USERNAME_KEY, point_to_web_user_data


class EditDeckContent(TabContent):
    def __init__(self) -> None:
        self.web_user_data = point_to_web_user_data()
        self.om_username = self.web_user_data.get(OM_USERNAME_KEY)
        self.om_user_data = point_to_om_user_data(om_username=self.om_username)
        self.deck_manipulator = ManipulateDecks(om_username=self.om_username)

    def _a_deck_exists(self) -> bool:
        return self.deck_manipulator.list_decks() != []

    def _sanitize_last_used_deck_in_storage(self) -> None:
        """Handle the special cases where no deck name is stored in memory, or if that
        deck doesn't exist anymore"""
        current_last_selected_deck = self.om_user_data.get(LAST_SELECTED_DECK_KEY)
        deck_list = self.deck_manipulator.list_decks()
        if (current_last_selected_deck == LAST_SELECTED_DECK_DEFAULT) | (
            current_last_selected_deck not in deck_list
        ):
            self.om_user_data.update({LAST_SELECTED_DECK_KEY: deck_list[0]})

    def _display_if_logged(self) -> None:
        # Stop if no deck available
        if not self._a_deck_exists():
            ui.label("No deck available. Have you synced them with our server?")
            return None
        else:
            self._display_if_deck_exists()

    def _display_if_deck_exists(self):
        """Display when logged in and a deck exists"""
        # Resync button
        self._display_sync_button()
        # TODO
        # Enforce the "last selected deck" in user storage makes sense
        self._sanitize_last_used_deck_in_storage()
        # Deck name selector. [Save/use the last] deck.
        self._display_deck_selector()
        # Get cards
        # TODO: factorize from here
        cards = self.deck_manipulator.get_cards_from_deck(
            deck_name=self.om_user_data[LAST_SELECTED_DECK_KEY]
        )
        # Display cards
        card_fields = [field.name for field in fields(Card)]
        ui.aggrid(
            options={
                "columnDefs": [
                    {"headerName": field, "field": field} for field in card_fields
                ],
                "rowData": [card.to_dict() for card in cards],
            }
        )
        # TODO: Have a single selecton system. (https://nicegui.io/documentation/aggrid#respond_to_an_ag_grid_event)
        # TODO: Have a "new/not new" filter system.
        # TODO Have filter systems by content
        # Select the mnem style. [Save/use the last] mnem style for the card type.
        # TODO
        # Select the fields that relate to the important items for that mnem style.
        # [Save/use the last] fields for that card type > mnem style.
        # Edit pane (w. edit save functionality)
        # TODO

    def _display_sync_button(self) -> None:
        pass

    def _display_deck_selector(self) -> None:
        """Display deck selector, save in LAST_SELECTED_DECK_KEY of om_user data"""
        ui.select(options=self.deck_manipulator.list_decks()).bind_value(
            target_object=self.om_user_data, target_name=LAST_SELECTED_DECK_KEY
        )
