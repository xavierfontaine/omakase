# TODO: change logic to get cards instead of notes (so that I can modify card
# attributes, for instance, although most editing will be on note fields.)
# TODO: when stabilized, add docstrings
"""
Deck edition tab
"""
import functools as ft
from typing import Optional
from unittest.mock import Mock

from nicegui import ui

from omakase.annotations import (
    DeckName,
    MnemonicUiLabel,
    NoteFieldName,
    NoteType,
    OmDeckFilterUiLabel,
)
from omakase.backend.decks import (
    Card,
    DeckFilters,
    DecksManipulator,
    filter_label_obj_corr,
    get_card_property_names,
)
from omakase.backend.mnemonics import MnemConf, tc_mnem_conf, tc_revision_mnem_conf
from omakase.backend.om_user import (
    DECK_UI_FILTER_CORR_KEY,
    LAST_SELECTED_DECK_DEFAULT,
    LAST_SELECTED_DECK_KEY,
    point_to_om_user_cache,
)
from omakase.exceptions import display_exception
from omakase.frontend.tabs.utils import TabContent
from omakase.frontend.web_user import OM_USERNAME_KEY, point_to_web_user_data
from omakase.om_logging import logger

# =========
# Constants
# =========
_AVAILABLE_DECK_FILTERS = DeckFilters()
_AVAILABLE_MNEMONICS: list[MnemConf] = [tc_mnem_conf, tc_revision_mnem_conf]
_DEFAULT_MNEM_NAME = _AVAILABLE_MNEMONICS[0].ui_label


# =======
# Classes
# =======
class EditDeckTabContent(TabContent):
    """UI for editing the content of the deck"""

    def __init__(self) -> None:
        # Names for assignment
        # self._SELECTED_ROW_ATTR_NAME = "_selected_row"
        # Assignment
        self.web_user_data: dict = point_to_web_user_data()
        self.om_username: str = self.web_user_data.get(OM_USERNAME_KEY)
        self.om_user_data: dict = point_to_om_user_cache(om_username=self.om_username)
        self._deck_manipulator = DecksManipulator(om_username=self.om_username)
        self._aggrid_table: ui.aggrid = self._build_aggrid_mock()
        # setattr(self, self._SELECTED_ROW_ATTR_NAME, None)
        self._cards: list[Card] = []
        self._dialog = ui.dialog()
        self._field_editor: _FieldEditor = _FieldEditor(whole_tab=self)

    def _build_aggrid_mock(self):
        """Build a mock aggrid table for the first run of the interface. The deck button
        is init with a link to the table, then the table itself; hence an init issue.
        """
        aggrid_table = Mock()
        aggrid_table.options = dict()
        return aggrid_table

    def _a_deck_exists(self) -> bool:
        return self._deck_manipulator.list_decks() != []

    @ui.refreshable
    def _display_if_logged(self) -> None:
        """Display depending on whether a deck exists or not"""
        # Stop if no deck available
        if not self._a_deck_exists():
            ui.label(
                "No deck available. Have you synced your collection with our server?"
            )
            return None
        else:
            self._display_all_if_deck_exists()

    def _display_all_if_deck_exists(self):
        """Display when logged in and a deck exists"""
        # Get initialization parameters
        # Deck name selector. [Save/use the last] deck.
        self._display_deck_selector()
        # Display card browser
        deck_name = self._get_current_deck_name()
        filter_name = self._get_current_filter_ui_name(deck_name=deck_name)
        self._display_deck(deck_name=deck_name, filter_name=filter_name)
        with ui.row():
            self._display_note_filter_radio(deck_name=deck_name)
            # Resync button
            self._display_sync_button()
        # Select the mnem style. [Save/use the last] mnem style for the card type.
        # TODO
        # Select the fields that relate to the important items for that mnem style.
        # [Save/use the last] fields for that card type > mnem style.
        # Edit pane (w. edit save functionality)
        self._field_editor.display_field_editor(selected_card_index=None)

    def _get_current_deck_name(self) -> Optional[DeckName]:
        """Get current deck name from user data

        If corner case, change the user data with sane deck name, and return `None`.
        If not deck in the list anymore, display the no-deck warning.
        """
        current_last_selected_deck = self.om_user_data.get(LAST_SELECTED_DECK_KEY)
        deck_list = self._deck_manipulator.list_decks()
        # Handle the case there is no deck anymore
        if len(deck_list) == 0:
            self._display_if_logged.refresh()
            return None
        # Handle the special cases where no deck name is stored in memory, or if that
        # deck doesn't exist anymore
        if (current_last_selected_deck == LAST_SELECTED_DECK_DEFAULT) | (
            current_last_selected_deck not in deck_list
        ):
            self.om_user_data.update({LAST_SELECTED_DECK_KEY: deck_list[0]})
        return self.om_user_data[LAST_SELECTED_DECK_KEY]

    def _get_current_filter_ui_name(self, deck_name: DeckName) -> OmDeckFilterUiLabel:
        """Get current filter name for deck, assigning 'all notes' if none"""
        # If no prefered filter for that deck in the cache, create one
        if deck_name not in self.om_user_data[DECK_UI_FILTER_CORR_KEY]:
            self.om_user_data[DECK_UI_FILTER_CORR_KEY][
                deck_name
            ] = _AVAILABLE_DECK_FILTERS.all_notes.ui_label
        return self.om_user_data[DECK_UI_FILTER_CORR_KEY][deck_name]

    def _get_card(self, deck_name: DeckName, card_index: int) -> Card:
        """Get card, throw an error if not present"""
        try:
            card = self._cards[card_index]
        # ... we throw an exception
        except IndexError:
            logger.exception(
                f"User {self.om_username} pointed to a card that is not"
                " present. WTF."
            )
            display_exception()
        return card

    @ui.refreshable
    def _display_deck_selector(self) -> None:
        """
        Display deck selector

        Behavior
        - update self._cards upon selection
        - save in LAST_SELECTED_DECK_KEY of om_user data
        - Refresh the aggrid table
        """
        # Display
        ui.select(
            options=self._deck_manipulator.list_decks(),
            on_change=lambda e: self._actions_on_deck_selection(deck_name=e.value),
        ).bind_value(
            target_object=self.om_user_data, target_name=LAST_SELECTED_DECK_KEY
        ).props(
            "outlined"
        )

    def _actions_on_deck_selection(self, deck_name: str) -> None:
        """Update the displayed deck and the selected filter"""
        deck_name = self._get_current_deck_name()
        filter_name = self._get_current_filter_ui_name(deck_name=deck_name)
        # Update the displayed deck
        self._display_deck.refresh(deck_name=deck_name, filter_name=filter_name)
        # Update the displayed filter button
        self._display_note_filter_radio.refresh(deck_name=deck_name)
        # Update note editor
        self._field_editor.display_field_editor.refresh(selected_card_index=None)

    @ui.refreshable
    def _display_deck(
        self, deck_name: DeckName, filter_name: OmDeckFilterUiLabel
    ) -> None:
        """Display deck as an aggrid table, assign to self._aggrid_table"""
        # Get cards
        self._assign_cards_from_deck(
            deck_name=deck_name,
            filter_name=filter_name,
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
            handler=lambda e: self._actions_on_agrid_cell_click(
                selected_card_index=e.args["rowIndex"]
            ),
        )

    def _actions_on_agrid_cell_click(self, selected_card_index: int) -> None:
        """Display card editor, prepare generator conf dialog box for display"""
        self._field_editor.display_field_editor.refresh(
            selected_card_index=selected_card_index
        )

    def _get_agrid_rows_from_cards(self) -> list[dict]:
        """Transfom self._cards to agrid rows

        The result can be passed to .option["rowData"] to update the aggrid table
        """
        return [card.get_card_properties() for card in self._cards]

    def _display_sync_button(self) -> None:
        """Display the sync button, which refreshes the UI as a whole"""
        ui.button(text="Pull deck again", on_click=self._actions_on_sync_button_click)

    def _actions_on_sync_button_click(self) -> None:
        # Update deck selector
        self._display_deck_selector.refresh()
        # Update deck display
        deck_name = self._get_current_deck_name()
        filter_name = self._get_current_filter_ui_name(deck_name=deck_name)
        self._display_deck.refresh(deck_name=deck_name, filter_name=filter_name)
        self._display_note_filter_radio.refresh(deck_name=deck_name)
        self._field_editor.display_field_editor.refresh(selected_card_index=None)

    @ui.refreshable
    def _display_note_filter_radio(self, deck_name: DeckName) -> None:
        """Display radio filter determining which cards to keep (all, new, in study)"""
        # If no prefered filter for that deck in the cache, create one
        if deck_name not in self.om_user_data[DECK_UI_FILTER_CORR_KEY]:
            self.om_user_data[DECK_UI_FILTER_CORR_KEY][
                deck_name
            ] = _AVAILABLE_DECK_FILTERS.all_notes.ui_label
        ui.radio(
            options=list(filter_label_obj_corr.keys()),
            on_change=lambda e, deck_name=deck_name: self._actions_on_filter_selection(
                filter_name=e.value, deck_name=deck_name
            ),
        ).bind_value(
            target_object=self.om_user_data[DECK_UI_FILTER_CORR_KEY],
            target_name=deck_name,
        ).props(
            "inline"
        )

    def _actions_on_filter_selection(
        self, filter_name: OmDeckFilterUiLabel, deck_name: DeckName
    ) -> None:
        # Update displayed cards
        self._display_deck.refresh(deck_name=deck_name, filter_name=filter_name)
        self._field_editor.display_field_editor.refresh(selected_card_index=None)

    def _assign_cards_from_deck(
        self, deck_name: str, filter_name: OmDeckFilterUiLabel
    ) -> None:
        """Assign to self._cards attribute"""
        om_filter_code = filter_label_obj_corr[filter_name].code
        self._cards = self._deck_manipulator.get_cards_from_deck(
            deck_name=deck_name, om_filter_code=om_filter_code
        )


class _FieldEditor:
    """Display the field edition system (incl mnemonic generation)"""

    def __init__(self, whole_tab: EditDeckTabContent):
        self._whole_tab = whole_tab
        self._available_mnemn_by_name: dict[MnemonicUiLabel, MnemConf] = {
            mnem.ui_label: mnem for mnem in _AVAILABLE_MNEMONICS
        }
        self._current_mnem_name = _DEFAULT_MNEM_NAME

    @ui.refreshable
    def display_field_editor(self, selected_card_index: Optional[int]):
        """Display editor's header, generation controlers, field editor"""
        # Display nothing if not card index
        if selected_card_index is None:
            return None
        # Header
        self._display_editor_header()
        # Mnemn type selector
        with ui.row():
            self._display_mnem_type_selector()
            self._display_mnem_type_descriptor()
        # Generation controller
        deck_name = self._whole_tab._get_current_deck_name()
        card = self._whole_tab._get_card(
            deck_name=deck_name, card_index=selected_card_index
        )
        note_type = card.note_type
        field_names = list(card.note_fields.keys())
        self._display_mnemonic_configurator(
            note_type=note_type,
            field_names=field_names,
        )
        # Generation trigger
        # TODO
        # Field editors
        self._display_field_editors(card=card)

    @ui.refreshable
    def _display_editor_header(self) -> None:
        ui.markdown("## Note editor")

    def _display_mnem_type_selector(self) -> None:
        ui.select(options=list(self._available_mnemn_by_name.keys())).bind_value(
            target_object=self, target_name="_current_mnem_name"
        ).tooltip("select the type of mnemonic for generation")

    def _display_mnem_type_descriptor(self) -> None:
        ui.label().bind_text_from(
            target_object=self,
            target_name="_current_mnem_name",
            backward=lambda s: self._available_mnemn_by_name[s].ui_descr,
        )

    @ui.refreshable
    def _display_mnemonic_configurator(
        self,
        note_type: NoteType,
        field_names: list[NoteFieldName],
    ) -> None:
        ui.button(
            icon="settings",
            on_click=lambda note_type=note_type, field_names=field_names: self._actions_on_settings_icon_click(  # noqa: E501
                note_type=note_type,
                field_names=field_names,
            ),
        ).tooltip("configure the mnemonic genertor")

    def _actions_on_settings_icon_click(
        self, note_type: NoteType, field_names: list[NoteFieldName]
    ) -> None:
        deck_name = self._whole_tab._get_current_deck_name()
        self._prepare_generator_conf_dialog(
            deck_name=deck_name, note_type=note_type, field_names=field_names
        )
        self._whole_tab._dialog.open()

    def _prepare_generator_conf_dialog(
        self, deck_name: DeckName, note_type: NoteType, field_names: list[NoteFieldName]
    ) -> None:
        """Prepare the generator conf dialog for display

        Won't open the dialog. Use self._whole_tab._dialog.open().
        """
        self._whole_tab._dialog.clear()
        with self._whole_tab._dialog, ui.card():
            ui.label(f"{deck_name=}, {note_type=}, {field_names=}")

    @ui.refreshable
    def _display_field_editors(self, card: Card) -> None:
        """Display the card editor given a card"""
        note_fields = card.note_fields
        for field_name, field_content in note_fields.items():
            ui.textarea(label=field_name).bind_value(
                target_object=note_fields, target_name=field_name
            ).props("outlined")
        # Display a save button, with a save mechanism
        ui.button(
            text="Save note",
            on_click=ft.partial(
                self._whole_tab._deck_manipulator.save_note,
                note_id=card.note_id,
                note_fields=note_fields,
            ),
        )
