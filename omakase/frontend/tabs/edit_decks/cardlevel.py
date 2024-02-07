import functools as ft

from nicegui import ui

from omakase.backend.decks import DecksManipulator, ObservableCard
from omakase.observer_logic import Observable, Observer


class _CardDataMediator(Observer):
    pass


class CardEditor(Observer):
    def __init__(
        self,
        card: ObservableCard,
        deck_manipulator: DecksManipulator,
    ) -> None:
        self._card = card
        self._deck_manipulator = deck_manipulator
        # Observers
        self._field_editor = _FieldEditors(
            card=self._card, deck_manipulator=self._deck_manipulator
        )

    @ui.refreshable
    def display(self) -> None:
        self._field_editor.display()

    def update(self, observable: Observable) -> None:
        self.display.refresh()


class _FieldEditors(Observer):
    def __init__(
        self,
        card: ObservableCard,
        deck_manipulator: DecksManipulator,
    ) -> None:
        self._card = card
        self._deck_manipulator = deck_manipulator

    @ui.refreshable
    def display(self) -> None:
        """Display the card editor given a card"""
        card = self._card
        note_fields = card.note_fields
        for field_name, field_content in note_fields.items():
            ui.textarea(label=field_name).bind_value(
                target_object=note_fields, target_name=field_name
            ).props("outlined")
        # Display a save button, with a save mechanism
        ui.button(
            text="Save changes",
            on_click=ft.partial(
                self._deck_manipulator.save_note,
                note_id=card.note_id,
                note_fields=note_fields,
            ),
        )

    def update(self, observable: Observable) -> None:
        self.display.refresh()
