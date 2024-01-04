"""
Statistics tab
"""
import functools as ft
from typing import Optional
from unittest.mock import Mock

from nicegui import ui

from omakase.backend.decks import Card, ManipulateDecks, get_card_property_names
from omakase.backend.om_user import (
    LAST_SELECTED_DECK_DEFAULT,
    LAST_SELECTED_DECK_KEY,
    point_to_om_user_data,
)
from omakase.exceptions import display_exception
from omakase.frontend.tabs.utils import TabContent
from omakase.frontend.web_user import OM_USERNAME_KEY, point_to_web_user_data
from omakase.om_logging import logger


class EditDeckContent(TabContent):
    """UI for editing the content of the deck"""

    def __init__(self) -> None:
        # Names for assignment
        # self._SELECTED_ROW_ATTR_NAME = "_selected_row"
        # Assignment
        self.web_user_data: dict = point_to_web_user_data()
        self.om_username: str = self.web_user_data.get(OM_USERNAME_KEY)
        self.om_user_data: str = point_to_om_user_data(om_username=self.om_username)
        self._deck_manipulator = ManipulateDecks(om_username=self.om_username)
        self._aggrid_table: ui.aggrid = self._build_aggrid_mock()
        # setattr(self, self._SELECTED_ROW_ATTR_NAME, None)
        self._cards: list[Card] = []

    def _build_aggrid_mock(self):
        """Build a mock aggrid table for the first run of the interface. The deck button
        is init with a link to the table, then the table itself; hence an init issue.
        """
        aggrid_table = Mock()
        aggrid_table.options = dict()
        return aggrid_table

    def _a_deck_exists(self) -> bool:
        return self._deck_manipulator.list_decks() != []

    def _sanitize_last_used_deck_in_storage(self) -> None:
        """Handle the special cases where no deck name is stored in memory, or if that
        deck doesn't exist anymore"""
        current_last_selected_deck = self.om_user_data.get(LAST_SELECTED_DECK_KEY)
        deck_list = self._deck_manipulator.list_decks()
        if (current_last_selected_deck == LAST_SELECTED_DECK_DEFAULT) | (
            current_last_selected_deck not in deck_list
        ):
            self.om_user_data.update({LAST_SELECTED_DECK_KEY: deck_list[0]})

    def _display_if_logged(self) -> None:
        """Display depending on whether a deck exists or not"""
        # Stop if no deck available
        if not self._a_deck_exists():
            ui.label("No deck available. Have you synced them with our server?")
            return None
        else:
            self._display_all_if_deck_exists()

    def _display_all_if_deck_exists(self):
        """Display when logged in and a deck exists"""
        # Resync button
        self._display_sync_button()
        # Enforce the "last selected deck" in user storage makes sense
        self._sanitize_last_used_deck_in_storage()
        # Deck name selector. [Save/use the last] deck.
        self._display_deck_selector()
        # Display card browser
        self._init_deck_display()
        # TODO: Have a "new/not new" filter system.
        # Select the mnem style. [Save/use the last] mnem style for the card type.
        # TODO
        # Select the fields that relate to the important items for that mnem style.
        # [Save/use the last] fields for that card type > mnem style.
        # Edit pane (w. edit save functionality)
        # ui.label().bind_text_from(target_object=self, target_name="_selected_row")
        self._display_card_editor_if_possible(selected_card_index=None)

    def _init_deck_display(self) -> None:
        """Display deck as an aggrid table, assign to self._aggrid_table"""
        # Get cards
        self._assign_cards_from_deck(
            deck_name=self.om_user_data[LAST_SELECTED_DECK_KEY]
        )
        # Display cards
        card_fields = get_card_property_names()
        self._aggrid_table = ui.aggrid(
            options={
                "columnDefs": [
                    {
                        "headerName": field,
                        "field": field,
                        "filter": "agTextColumnFilter",
                        "floatingFilter": True,
                    }
                    for field in card_fields
                ],
                "rowData": self._get_agrid_rows_from_cards(),
            }
        ).on(
            type="cellClicked",
            # handler=lambda e: setattr(self, "_selected_row", e.args["rowIndex"]),
            handler=lambda e: self._display_card_editor_if_possible.refresh(
                selected_card_index=e.args["rowIndex"]
            ),
        )

    def _get_agrid_rows_from_cards(self) -> list[dict]:
        """Transfom self._cards to agrid rows

        The result can be passed to .option["rowData"] to update the aggrid table
        """
        return [card.get_card_properties() for card in self._cards]

    def _display_sync_button(self) -> None:
        ui.button(
            text="Fetch cards",
            on_click=self._update_aggrid,
        )

    def _display_deck_selector(self) -> None:
        """
        Display deck selector

        Behavior
        - update self._cards upon selection
        - save in LAST_SELECTED_DECK_KEY of om_user data
        - Refresh the aggrid table
        """
        ui.select(
            options=self._deck_manipulator.list_decks(),
            on_change=lambda e: self._update_aggrid_from_deckname(deck_name=e.value),
        ).bind_value(
            target_object=self.om_user_data, target_name=LAST_SELECTED_DECK_KEY
        )

    def _assign_cards_from_deck(self, deck_name: str) -> None:
        """Assign to self._cards attribute"""
        self._cards = self._deck_manipulator.get_cards_from_deck(
            deck_name=deck_name,
        )

    def _update_aggrid_from_deckname(self, deck_name: str) -> None:
        """Store cadre to self._cards and refresh agrid table"""
        # Get cards from deck
        self._assign_cards_from_deck(deck_name=deck_name)
        # Change the aggrid table content
        self._aggrid_table.options["rowData"] = self._get_agrid_rows_from_cards()
        # Refresh the aggrid object
        self._aggrid_table.update()

    def _update_aggrid(self) -> None:
        """Same as _update_aggrid_from_deckname, but use the stored deck name"""
        deck_name = self.om_user_data[LAST_SELECTED_DECK_KEY]
        self._update_aggrid_from_deckname(deck_name=deck_name)

    @ui.refreshable
    def _display_card_editor_if_possible(
        self, selected_card_index: Optional[int]
    ) -> None:
        """Display card editor if possible, otherwise display nothing/an exception"""
        # Display nothing if no selecfted card
        if selected_card_index is None:
            return None
        # Else, get the card and display it...
        else:
            # ... assuming there is a card to display! If not...
            try:
                card = self._cards[selected_card_index]
                self._display_card_editor_when_card_exists(card=card)
            # ... we throw an exception
            except IndexError:
                logger.exception(
                    f"User {self.om_username} pointed to a card that is not"
                    " present. WTF."
                )
                display_exception()

    @ui.refreshable
    def _display_card_editor_when_card_exists(self, card: Card) -> None:
        """Display the card editor given a card"""
        note_fields = card.note_fields
        for field_name, field_content in note_fields.items():
            ui.textarea(label=field_name).bind_value(
                target_object=note_fields, target_name=field_name
            )
        # Display a save button, with a save mechanism
        ui.button(
            text="Save note",
            on_click=ft.partial(
                self._deck_manipulator.save_note,
                note_id=card.note_id,
                note_fields=note_fields,
            ),
        )
