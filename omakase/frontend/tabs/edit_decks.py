# TODO: simplify the subscription method, expecting only an `update` method.

# TODO: first code the UI/consummer logic, then the backend logic.
# TODO: change logic to get cards instead of notes (so that I can modify card
# attributes, for instance, although most editing will be on note fields.)
# TODO: when stabilized, add docstrings
"""
Deck edition tab
"""
import functools as ft
from typing import Callable, Optional
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
from omakase.backend.mnemonics import (
    MnemConf,
    MnemonicNoteFieldMapData,
    get_str_field_names,
    tc_mnem_conf,
    tc_revision_mnem_conf,
)
from omakase.backend.om_user import DeckFilterCorrObl, LastSelectedDeckObl
from omakase.exceptions import display_exception
from omakase.frontend.tabs.utils import TabContent
from omakase.frontend.web_user import OM_USERNAME_KEY, point_to_web_user_data
from omakase.observer_logic import Observable, Observer, Subscription
from omakase.om_logging import logger

# =========
# Constants
# =========
_AVAILABLE_DECK_FILTERS = DeckFilters()
_AVAILABLE_MNEMONICS: list[MnemConf] = [tc_mnem_conf, tc_revision_mnem_conf]
_DEFAULT_MNEM_NAME = _AVAILABLE_MNEMONICS[0].ui_label


# ============
# Mock classes
# ============
PromptSettings = Mock()

# ============
# Side objects
# ============
class _CurrentCardsObl(Observable):
    """Observable list of cards"""

    def __init__(self, cards: Optional[list[Card]]) -> None:
        self.value: list[Card] = cards if cards is not None else []


class _AvailableDeckNamesObl(Observable):
    """List of available deck names"""

    def __init__(self, deck_names: Optional[list[DeckName]]) -> None:
        self.value: list[DeckName] = deck_names if deck_names is not None else []


class _CurrentCardIdxObl(Observable):
    """Observable index for the current card

    None if no card"""

    def __init__(self, card_idx: Optional[int]) -> None:
        self.value: Optional[int] = card_idx


class _DataMediator:
    def __init__(
        self,
        deck_manipulator: DecksManipulator,
        deck_names_obl: _AvailableDeckNamesObl,
        last_selected_deck_obl: LastSelectedDeckObl,
        deck_ui_filter_corr_obl: DeckFilterCorrObl,
        current_cards_obl: _CurrentCardsObl,
        current_card_idx_obl: _CurrentCardIdxObl,
    ) -> None:
        """Cascade changes in data and notify accordingly

        Used to notify a change in data layer {l}
        - Reponsible for changing layers {l+i} accordingly.
        - Responsible for sending notifications regarding  {l} and {l+i}
        For each data layer {l}, a method is responsible for the above.

        Layers are, in order (with parallelism)
        - list of deck names           |
                                       | - Association between deck names and ui filters
        - Name of last selected deck   |
        - Currently pulled set of cards
        - Current card idx

        Args: `Observables` pointing to the different data layers
        """
        self._deck_manipulator = deck_manipulator
        self._deck_names_obl = deck_names_obl
        self._last_selected_deck_obl = last_selected_deck_obl
        self._deck_ui_filter_corr_obl = deck_ui_filter_corr_obl
        self._current_cards_obl = current_cards_obl
        self._current_card_idx_obl = current_card_idx_obl

    def handle_deck_names_change(self) -> None:
        """handle change in deck_names_obl"""
        # Update next layers
        self._sanitize_current_deck()
        self._update_cards()
        self._current_card_idx_obl.value = None
        # Notify current and next layers
        self._deck_names_obl.notify()
        # TODO: make sure that nothing is displayed if that list has length 0
        self._current_cards_obl.notify()
        self._current_card_idx_obl.notify()

    def handle_last_deck_name_change(self) -> None:
        print("handle_last_deck_name_change")
        # Update folnextyers
        self._update_cards()
        self._current_card_idx_obl.value = None
        # Notify current and next layers
        self._last_selected_deck_obl.notify()
        self._current_cards_obl.notify()
        self._current_card_idx_obl.notify()

    def handle_deck_filter_corr_change(self) -> None:
        # Update next layers
        self._update_cards()
        self._current_card_idx_obl.value = None
        # Notify current and next layers
        self._deck_ui_filter_corr_obl.notify()
        self._current_cards_obl.notify()
        self._current_card_idx_obl.notify()

    def handle_current_cards_change(self) -> None:
        # Update next layers
        self._current_card_idx_obl.value = None
        # Notify current and next layers
        self._current_cards_obl.notify()
        self._current_card_idx_obl.notify()

    def handle_current_card_idx_change(self) -> None:
        # Update next layers
        # Notify current and next layers
        self._current_card_idx_obl.notify()

    def _update_cards(self) -> None:
        """Update cards to match the current deck and its filter"""
        deck_name = self._last_selected_deck_obl.deck_name_dp.value
        cards = _get_cards(
            deck_name=deck_name,
            deck_filter_corr_obl=self._deck_ui_filter_corr_obl,
            deck_manipulator=self._deck_manipulator,
        )
        self._current_cards_obl.value = cards

    def _sanitize_current_deck(self):
        """Sanitize current deck

        Handle the special cases where no deck name is stored in memory, or if that
        deck doesn't exist anymore.
        """
        deck_list = self._deck_names_obl.value
        deck_name_dp = self._last_selected_deck_obl.deck_name_dp
        if (deck_name_dp.value is None) | (deck_name_dp.value not in deck_list):
            if len(deck_list) > 0:
                deck_name_dp.value = deck_list[0]
            else:
                deck_name_dp.value = None


def _get_cards(
    deck_name: DeckName,
    deck_filter_corr_obl: DeckFilterCorrObl,
    deck_manipulator: DecksManipulator,
) -> list[Card]:
    filter_name = deck_filter_corr_obl.get_filter_dp(deck_name=deck_name).value
    om_filter_code = filter_label_obj_corr[filter_name].code
    cards = deck_manipulator.get_cards_from_deck(
        deck_name=deck_name, om_filter_code=om_filter_code
    )
    return cards


# ==========
# UI classes
# ==========
class EditDeckTabContent(TabContent):
    """UI for editing the content of the deck"""

    def __init__(self) -> None:
        # Assignment
        self.web_user_data: dict = point_to_web_user_data()
        self.om_username: str = self.web_user_data.get(OM_USERNAME_KEY)
        self._deck_manipulator = DecksManipulator(om_username=self.om_username)
        # Initializations
        self._dialog = ui.dialog()
        # Observables
        self._last_selected_deck_obl = LastSelectedDeckObl(
            om_username=self.om_username)
        self._deck_ui_filter_corr_obl = DeckFilterCorrObl(
            om_username=self.om_username)
        self._deck_names_obl = _AvailableDeckNamesObl(
            deck_names=self._deck_manipulator.list_decks()
        )
        self._current_cards_obl = _CurrentCardsObl(
            cards=None
        )  # will be initiated on # initial refresh of card displayer
        self._current_card_idx_obl = _CurrentCardIdxObl(card_idx=None)
        # Mediator (responsible for adjusting observables wrt each others and for
        # handling their notifications)
        self._mediator = _DataMediator(
            deck_manipulator=self._deck_manipulator,
            deck_names_obl=self._deck_names_obl,
            last_selected_deck_obl=self._last_selected_deck_obl,
            deck_ui_filter_corr_obl=self._deck_ui_filter_corr_obl,
            current_cards_obl=self._current_cards_obl,
            current_card_idx_obl=self._current_card_idx_obl,
        )
        # Observers
        self._deck_selector_obr = _DeckSelector(
            deck_names_obl=self._deck_names_obl,
            last_selected_deck_obl=self._last_selected_deck_obl,
            curr_card_idx_obl=self._current_card_idx_obl,
            mediator=self._mediator,
        )
        self._deck_displayer = _DeckDisplayer(
            current_cards_obl=self._current_cards_obl,
            curr_card_idx_obl=self._current_card_idx_obl,
            last_selected_deck_obl=self._last_selected_deck_obl,
            deck_ui_filter_corr_obl=self._deck_ui_filter_corr_obl,
            mediator=self._mediator,
        )
        # Subscriptions - _deck_names_obl
        self._deck_names_obl.attach(
            subscription=Subscription(
                method=self._deck_selector_obr.update)
        )
        # Subscriptions - _current_cards_obl
        self._current_cards_obl.attach(
            subscription=Subscription(method=self._deck_displayer.update)
        )

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
        self._deck_selector_obr.display_deck_selector()
        self._deck_displayer.display_deck()

    def __display_all_if_deck_exists(self):
        """Display when logged in and a deck exists"""
        # Get initialization parameters
        # Deck name selector. [Save/use the last] deck.
        self.display_deck_selector()
        # Display card browser
        deck_name = self._get_current_deck_name()
        filter_name = self._deck_ui_filter_corr_obl.get_filter_dp(
            deck_name=deck_name
        ).value
        self.display_deck(deck_name=deck_name, filter_name=filter_name)
        with ui.row():
            self._display_note_filter_radio(deck_name=deck_name)
            # Resync button
            self._display_sync_button()
        # Select the mnem style. [Save/use the last] mnem style for the card type.
        # TODO
        # Select the fields that relate to the important items for that mnem style.
        # [Save/use the last] fields for that card type > mnem style.
        # Edit pane (w. edit save functionality)
        self._display_field_editor(
            selected_card_index=None, deck_name=deck_name)

    def __get_current_deck_name(self) -> Optional[DeckName]:
        """Get current deck name from user data

        If corner case, change the user data with sane deck name, and return `None`.
        If not deck in the list anymore, display the no-deck warning.
        """
        deck_list = self._deck_manipulator.list_decks()
        # Handle the case there is no deck anymore
        if len(deck_list) == 0:
            self._display_if_logged.refresh()
            return None
        return deck_name_dp.value

    def _get_card(self, card_index: int) -> Card:
        """Get card, throw an error if not present"""
        try:
            card = self._current_cards_obl.value[card_index]
        # ... we throw an exception
        except IndexError:
            logger.exception(
                f"User {self.om_username} pointed to a card that is not"
                " present. WTF."
            )
            display_exception()
        return card

    def __actions_on_deck_selection(self, deck_name: str) -> None:
        """Update the displayed deck and the selected filter"""
        deck_name = self._get_current_deck_name()
        filter_name = self._deck_ui_filter_corr_obl.get_filter_dp(
            deck_name=deck_name
        ).value
        # Update the displayed deck
        self.display_deck.refresh(deck_name=deck_name, filter_name=filter_name)
        # Update the displayed filter button
        self._display_note_filter_radio.refresh(deck_name=deck_name)
        # Update note editor
        self._display_field_editor.refresh(
            selected_card_index=None, deck_name=deck_name
        )

    @ui.refreshable
    def __display_field_editor(
        self, selected_card_index: Optional[int], deck_name: DeckName
    ):
        if selected_card_index is None:
            return
        else:
            card = self._get_card(card_index=selected_card_index)
            field_editor = _FieldEditor(
                card=card,
                whole_tab=self,
            )
            field_editor.display_field_editor()

    def __display_sync_button(self) -> None:
        """Display the sync button, which refreshes the UI as a whole"""
        ui.button(
            text="Pull collection again", on_click=self._actions_on_sync_button_click
        )

    def __actions_on_sync_button_click(self) -> None:
        # Update deck selector
        self.display_deck_selector.refresh()
        # Update deck display
        deck_name = self._get_current_deck_name()
        filter_name = self._deck_ui_filter_corr_obl.get_filter_dp(
            deck_name=deck_name
        ).value
        self.display_deck.refresh(deck_name=deck_name, filter_name=filter_name)
        self._display_note_filter_radio.refresh(deck_name=deck_name)
        self._display_field_editor.refresh(
            selected_card_index=None, deck_name=deck_name
        )

    @ui.refreshable
    def __display_note_filter_radio(self, deck_name: DeckName) -> None:
        """Display radio filter determining which cards to keep (all, new, in study)"""
        # If no prefered filter for that deck in the cache, create one
        filter_name_dp = self._deck_ui_filter_corr_obl.get_filter_dp(
            deck_name=deck_name
        )
        ui.radio(
            options=list(filter_label_obj_corr.keys()),
            on_change=lambda e, deck_name=deck_name: self._actions_on_filter_selection(
                filter_name=e.value, deck_name=deck_name
            ),
        ).bind_value(target_object=filter_name_dp, target_name="value",).props("inline")

    def __actions_on_filter_selection(
        self, filter_name: str, deck_name: DeckName
    ) -> None:
        # Update displayed cards
        self.display_deck.refresh(deck_name=deck_name, filter_name=filter_name)
        self._display_field_editor.refresh(
            selected_card_index=None, deck_name=deck_name
        )


class _DeckSelector(Observer):
    def __init__(
        self,
        last_selected_deck_obl: LastSelectedDeckObl,
        deck_names_obl: _AvailableDeckNamesObl,
        curr_card_idx_obl: _CurrentCardIdxObl,
        mediator: _DataMediator,
    ):
        """Deck selector

        - Updated when change in _AvailableDeckNamesObl
        - Updates DeckFilterCorrObl and _CurrentCardsObl
        """
        self._last_selected_deck_obl = last_selected_deck_obl
        self._deck_names_obl = deck_names_obl
        self._curr_card_idx_obl = curr_card_idx_obl
        self._mediator = mediator

    @ui.refreshable
    def display_deck_selector(self) -> None:
        """
        Display deck selector

        Behavior
        - update self._cards_obl.cards upon selection
        - save in LAST_SELECTED_DECK_KEY of om_user data
        - Refresh the aggrid table
        """
        # Display
        ui.select(
            options=self._deck_names_obl.value,
            on_change=self._actions_on_deck_change,
        ).bind_value(
            target_object=self._last_selected_deck_obl.deck_name_dp,
            target_name="value",
        ).props(
            "outlined"
        )

    def update(self) -> None:
        self.display_deck_selector.refresh()

    def _actions_on_deck_change(self) -> None:
        # Notify that deck has changed
        print("_actions_on_deck_change")
        self._mediator.handle_last_deck_name_change()


class _DeckDisplayer(Observer):
    def __init__(
        self,
        current_cards_obl: _CurrentCardsObl,
        curr_card_idx_obl: _CurrentCardIdxObl,
        last_selected_deck_obl: LastSelectedDeckObl,
        deck_ui_filter_corr_obl: DeckFilterCorrObl,
        mediator: _DataMediator,
    ) -> None:
        """Deck displayer and card selector

        - Updated when change in _CurrentCardsObl
        - Updates _CurrentCardIdxObl
        """
        self._aggrid_table: ui.aggrid = self._build_aggrid_mock()
        self._cards_obl = current_cards_obl
        self._curr_card_idx_obl = curr_card_idx_obl
        self._last_selected_deck_obl = last_selected_deck_obl
        self._deck_ui_filter_corr_obl = deck_ui_filter_corr_obl
        self._mediator = mediator

    @ui.refreshable
    # TODO faire de deck_name et filter_name des observeables utilisant le dp
    def display_deck(self) -> None:
        """Display deck as an aggrid table, assign to self._aggrid_table"""
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
            handler=lambda e, : self._actions_on_agrid_cell_click(
                selected_card_index=e.args["rowIndex"]
            ),
        )

    def _actions_on_agrid_cell_click(self, selected_card_index: int) -> None:
        """Display card editor, prepare generator conf dialog box for display"""
        self._curr_card_idx_obl.value = selected_card_index
        self._mediator.handle_current_card_idx_change()

    def _get_agrid_rows_from_cards(self) -> list[dict]:
        """Transfom self._cards_obl.cards to agrid rows

        The result can be passed to .option["rowData"] to update the aggrid table
        """
        return [card.get_card_properties() for card in self._cards_obl.value]

    def _build_aggrid_mock(self):
        """Build a mock aggrid table for the first run of the interface. The deck button
        is init with a link to the table, then the table itself; hence an init issue.
        """
        aggrid_table = Mock()
        aggrid_table.options = dict()
        return aggrid_table

    def update(self) -> None:
        print("_DeckDisplayer.update")
        self.display_deck.refresh()


class _FilterSelector(Observer):
    def __init__(self) -> None:
        pass

    def update(self) -> None:
        pass


class ResyncButton:
    def __init__(self):
        pass


class _FieldEditor:
    """Display the field edition system (incl mnemonic generation)"""

    # TODO: put outside the choice of the mnemonic type, and reinstantiate all objects
    # when the mnemonic type is changed.

    def __init__(self, card: Card, whole_tab: EditDeckTabContent):
        # Assignments to self
        self._card = card
        self._whole_tab = whole_tab
        # Extract information on card
        self._note_type = self._card.note_type
        self._note_field_names = list(self._card.note_fields.keys())
        # Available and current mnemonic names
        self._available_mnemn_by_name: dict[MnemonicUiLabel, MnemConf] = {
            mnem.ui_label: mnem for mnem in _AVAILABLE_MNEMONICS
        }
        self._current_mnem_name = _DEFAULT_MNEM_NAME
        # Mnemn <> note field mapping data
        self._mnemn_note_map_data = self._get_mnem_note_field_mapper(
            mnem_name=self._current_mnem_name
        )

    @ui.refreshable
    def display_field_editor(self):
        """Display editor's header, generation controlers, field editor"""
        # Header
        self._display_editor_header()
        # Mnemn type selector
        with ui.row():
            self._display_mnem_type_selector()
            self._display_mnem_type_descriptor()
        # Generation controller
        self._display_settings_icon()
        # Generation trigger
        self._display_generation_icon()
        # Field editors
        self._display_individual_field_editors(card=self._card)

    @ui.refreshable
    def _display_editor_header(self) -> None:
        ui.markdown("## Note editor")

    def _display_mnem_type_selector(self) -> None:
        ui.select(
            options=list(self._available_mnemn_by_name.keys()),
            on_change=lambda e: self._actions_on_changing_mnem_type(
                mnem_name=e.value),
        ).bind_value(target_object=self, target_name="_current_mnem_name").tooltip(
            "select the type of mnemonic for generation"
        )

    def _get_mnem_note_field_mapper(
        self, mnem_name: MnemonicUiLabel
    ) -> MnemonicNoteFieldMapData:
        return MnemonicNoteFieldMapData(
            prompt_params_class=self._available_mnemn_by_name[
                mnem_name
            ].prompt_param_class,
            note_type=self._note_type,
            note_field_names=self._note_field_names,
            om_username=self._whole_tab.om_username,
        )

    def _actions_on_changing_mnem_type(self, mnem_name: MnemonicUiLabel) -> None:
        self._mnemn_note_map_data = self._get_mnem_note_field_mapper(
            mnem_name=mnem_name
        )

    def _display_mnem_type_descriptor(self) -> None:
        ui.label().bind_text_from(
            target_object=self,
            target_name="_current_mnem_name",
            backward=lambda s: self._available_mnemn_by_name[s].ui_descr,
        )

    def _display_settings_icon(
        self,
    ) -> None:
        note_type = self._note_type
        field_names = self._note_field_names
        ui.button(
            icon="settings",
            on_click=lambda note_type=note_type, field_names=field_names: self._actions_on_settings_icon_click(  # noqa: E501
                note_type=note_type,
                note_field_names=field_names,
            ),
        ).tooltip("configure the mnemonic genertor")

    def _actions_on_settings_icon_click(
        self, note_type: NoteType, note_field_names: list[NoteFieldName]
    ) -> None:
        # Clean up the dialog box, and prepare the new one
        self._whole_tab._dialog.clear()
        with self._whole_tab._dialog, ui.card():
            self._fill_settings_dialog(
                note_type=note_type,
                note_field_names=note_field_names,
                mnem_name=self._current_mnem_name,
            )
        # Disiplay the dialog box
        self._whole_tab._dialog.open()

    def _fill_settings_dialog(
        self,
        note_type: NoteType,
        note_field_names: list[NoteFieldName],
        mnem_name: MnemonicUiLabel,
    ) -> None:
        """Content for the generator conf dialog"""
        # Point to user preference on association btwn mnemn & note fields
        # TODO
        # Display with hook to user data
        ui.markdown("### Send output to *(mandatory)*")
        ui.select(
            options=[None] + note_field_names,
        ).bind_value(
            target_object=self._mnemn_note_map_data.point_to_genout_note_field_dp(),
            target_name="value",
        )
        ui.markdown("### Pre-fill from *(optional)*")
        prompt_param_class = self._available_mnemn_by_name[mnem_name].prompt_param_class
        str_prompt_field_names = get_str_field_names(
            prompt_params_class=prompt_param_class
        )
        for prompt_param_name in str_prompt_field_names:
            with ui.row():
                prompt_param_ui_name = (
                    self._available_mnemn_by_name[mnem_name]
                    .prompt_param_field_ui_descr[prompt_param_name]
                    .ui_name
                )
                prompt_param_ui_expl = (
                    self._available_mnemn_by_name[mnem_name]
                    .prompt_param_field_ui_descr[prompt_param_name]
                    .ui_explanation
                )
                ui.label(f"{prompt_param_ui_name}").tooltip(
                    prompt_param_ui_expl)
                ui.select(
                    options=[None] + note_field_names,
                ).bind_value(
                    target_object=self._mnemn_note_map_data.point_to_prompt_note_assoc_dp(  # noqa: E501
                        prompt_param_name=prompt_param_name
                    ),
                    target_name="value",
                )

    def _display_generation_icon(
        self,
    ) -> None:
        ui.button(
            icon="play_circle",
            on_click=self._actions_on_generation_icon_click,
        ).tooltip("Generate the mnemonic")

    def _actions_on_generation_icon_click(
        self,
    ) -> None:
        # Clean up the dialog box, and prepare the new one
        self._whole_tab._dialog.clear()
        with self._whole_tab._dialog, ui.card():
            self._fill_generation_dialog_box()
        # Disiplay the dialog box
        self._whole_tab._dialog.open()

    def _fill_generation_dialog_box(self) -> None:
        # TODO: implement through GenerationInterface
        pass

    @ui.refreshable
    def _display_individual_field_editors(self, card: Card) -> None:
        """Display the card editor given a card"""
        note_fields = card.note_fields
        for field_name, field_content in note_fields.items():
            ui.textarea(label=field_name).bind_value(
                target_object=note_fields, target_name=field_name
            ).props("outlined")
        # Display a save button, with a save mechanism
        ui.button(
            text="Save changes",
            on_click=ft.partial(
                self._whole_tab._deck_manipulator.save_note,
                note_id=card.note_id,
                note_fields=note_fields,
            ),
        )


class GenerationInterface:
    def __init__(self, mnem_name: MnemonicUiLabel) -> None:
        pass

    def display(self) -> None:
        pass
