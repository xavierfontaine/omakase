"""UI at the card level

Called by the UI module at the level of the decks
"""

import functools as ft
from typing import Type

from nicegui import ui

from omakase.annotations import MnemonicUiLabel
from omakase.backend.decks import DecksManipulator, ObservableCard
from omakase.backend.mnemonics import MockPromptData, SoundTargetComponentsData
from omakase.backend.mnemonics.base import MnemonicNoteFieldMapData, PromptFieldsData
from omakase.frontend.tabs.edit_decks.data import CurrentMnemTypeObl
from omakase.frontend.web_user import OM_USERNAME_KEY, point_to_web_user_data
from omakase.observer_logic import Observable, Observer

# ==========
# Parameters
# ==========
# Define the available mnemonics
_AVAILABLE_MNEMONICS: list[Type[PromptFieldsData]] = [
    SoundTargetComponentsData,
    MockPromptData,
]

# ====
# Core
# ====
_AVAILABLE_MNEMN_BY_NAME: dict[MnemonicUiLabel, Type[PromptFieldsData]] = {
    mnem().ui_name: mnem for mnem in _AVAILABLE_MNEMONICS
}
_DEFAULT_MNEM_NAME = _AVAILABLE_MNEMONICS[0]().ui_name


class _DataMediator(Observer):
    def __init__(self, card_obl: ObservableCard) -> None:
        self._card_obl = card_obl


class CardEditor(Observer):
    def __init__(
        self,
        card_obl: ObservableCard,
        deck_manipulator: DecksManipulator,
    ) -> None:
        """Card editor

        Dev note:
            Assume that the card and om user does not change during the lifetime of the
            class
        """
        # Assignement
        self._deck_manipulator = deck_manipulator
        self._om_username: str = point_to_web_user_data().get(OM_USERNAME_KEY)
        # Observables
        self._card_obl = card_obl
        self._current_mnem_type_obl = CurrentMnemTypeObl(data=_DEFAULT_MNEM_NAME)
        # Observers
        self._field_editor_obr = _FieldEditors(
            card_obl=self._card_obl, deck_manipulator=self._deck_manipulator
        )
        self._mnem_type_selector_obr = _MnemTypeSelector(
            current_mnem_type=self._current_mnem_type_obl
        )
        # Non-observer UI
        self._prompt_note_field_button = _PromptNoteFieldButton(
            current_mnem_type_obl=self._current_mnem_type_obl, card_obl=self._card_obl
        )
        # Mediator
        # Subscriptions
        self._current_mnem_type_obl.attach(self._mnem_type_selector_obr)

    @ui.refreshable
    def display(self) -> None:
        ui.separator()
        ui.markdown("## Edit note")
        with ui.row():
            self._mnem_type_selector_obr.display()
            self._prompt_note_field_button.display()
        self._field_editor_obr.display()

    def update(self, observable: Observable) -> None:
        self.display.refresh()


class _FieldEditors(Observer):
    def __init__(
        self,
        card_obl: ObservableCard,
        deck_manipulator: DecksManipulator,
    ) -> None:
        self._card_obl = card_obl
        self._deck_manipulator = deck_manipulator

    @ui.refreshable
    def display(self) -> None:
        """Display the card editor given a card"""
        card_obl = self._card_obl
        note_fields = card_obl.note_fields
        with ui.row():
            for field_name, field_content in note_fields.items():
                ui.textarea(label=field_name).bind_value(
                    target_object=note_fields, target_name=field_name
                ).props("outlined")
        # Display a save button, with a save mechanism
        ui.button(
            text="Save changes",
            on_click=ft.partial(
                self._deck_manipulator.save_note,
                note_id=card_obl.note_id,
                note_fields=note_fields,
            ),
        )

    def update(self, observable: Observable) -> None:
        self.display.refresh()


# TODO: should subscribe to current mnem type (if changed somewhere else)
class _MnemTypeSelector(Observer):
    """Select the type of mnemonics"""

    def __init__(self, current_mnem_type: CurrentMnemTypeObl) -> None:
        self._current_mnem_type = current_mnem_type

    @ui.refreshable
    def display(self) -> None:
        """Not refreshable because list of mnemonics loaded only at page
        instantiation
        """
        ui.select(
            options=list(_AVAILABLE_MNEMN_BY_NAME.keys()),
        ).bind_value(
            target_object=self._current_mnem_type, target_name="value"
        ).tooltip("select the type of mnemonic for generation")

    def update(self, observable: Observable) -> None:
        self.display.refresh()


class _PromptNoteFieldButton:
    """Button to display the Prompt/Note field associator"""

    def __init__(
        self, current_mnem_type_obl: CurrentMnemTypeObl, card_obl: ObservableCard
    ) -> None:
        self._current_mnem_type_obl = current_mnem_type_obl
        self._card_obl = card_obl

    def display(self) -> None:
        ui.button(
            icon="settings",
            on_click=self._actions_on_click,
        ).tooltip("configure the mnemonic generator")

    def _actions_on_click(self):
        """Instantiate and display the mnem/note field associator"""
        mnem_note_field_associator = _MnemNoteFieldAssociator(
            current_mnem_type_obl=self._current_mnem_type_obl, card_obl=self._card_obl
        )
        mnem_note_field_associator.display()


class _MnemNoteFieldAssociator:
    """Configure the association between prompt fields, and note fields"""

    def __init__(
        self, current_mnem_type_obl: CurrentMnemTypeObl, card_obl: ObservableCard
    ) -> None:
        # Assignment
        self._current_mnem_type_obl = current_mnem_type_obl
        self._card_obl = card_obl

    def display(self) -> None:
        """Display the card editor given a card"""
        with ui.dialog() as dialog, ui.card():
            self._generate_content_to_display()
        dialog.open()

    def _generate_content_to_display(self):
        """Factor out the content to display in the dialog box"""
        # Get relevant objects
        mnem_note_field_map = self._get_mnem_note_field_map()
        note_field_names = list(self._card_obl.note_fields.keys())
        mnem_name = self._current_mnem_type_obl.value
        prompt_param_inst = _AVAILABLE_MNEMN_BY_NAME[mnem_name]()
        # Display with hook to user data
        ui.markdown("### Send output... *(mandatory)*")
        with ui.row():
            ui.label("to ")
            ui.select(
                options=[None] + note_field_names,
            ).bind_value(
                target_object=mnem_note_field_map.point_to_genout_note_field_dp(),
                target_name="value",
            )
        ui.markdown("### Pre-fill... *(optional)*")
        one_d_prompt_field_names = prompt_param_inst.get_1d_prompt_section_names()
        for prompt_param_name in one_d_prompt_field_names:
            with ui.row():
                prompt_param_ui_name = prompt_param_inst.value[
                    prompt_param_name
                ].ui_name
                ui.markdown(f"`{prompt_param_ui_name}` from")
                ui.select(
                    options=[None] + note_field_names,
                ).bind_value(
                    target_object=mnem_note_field_map.point_to_prompt_note_assoc_dp(  # noqa: E501
                        prompt_param_name=prompt_param_name
                    ),
                    target_name="value",
                )

    def _get_mnem_note_field_map(self) -> MnemonicNoteFieldMapData:
        om_username: str = point_to_web_user_data().get(OM_USERNAME_KEY)
        nf_map = self._mnem_note_field_map_data = MnemonicNoteFieldMapData(
            prompt_params_class=_AVAILABLE_MNEMN_BY_NAME[
                self._current_mnem_type_obl.value
            ],
            note_type=self._card_obl.note_type,
            note_field_names=list(self._card_obl.note_fields.keys()),
            om_username=om_username,
        )
        return nf_map

    # TODO: remove if indeed no need to have refreshable
    # def update(self, observable: Observable) -> None:
    #     self.display.refresh()
