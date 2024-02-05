"""
Query and edit decks
"""
from dataclasses import asdict, dataclass, fields
from typing import Optional

from omakase.annotations import (
    DeckName,
    NoteFieldName,
    NoteFieldValue,
    OmDeckFilterCode,
)
from omakase.observer_logic import Observable


# ===============
# SRS-independent
# ===============
@dataclass
class Card(Observable):
    card_id: int
    note_id: int
    sort_field_value: str
    due_value: int
    note_type: str
    study_status: OmDeckFilterCode
    note_fields: dict[NoteFieldName, NoteFieldValue]

    def get_card_properties(self) -> dict:
        """Return the card properties (excl the card's fields) as a dict"""
        dic = asdict(self)
        dic.pop("note_fields")
        return dic


def get_card_property_names() -> list:
    """Return the property names (excl the card's fields)"""
    names = [field.name for field in fields(Card)]
    names.pop(names.index("note_fields"))
    return names


# ===============
# SRS-independent
# ===============
class DecksManipulator:
    def __init__(self, om_username: str) -> None:
        """Manipulate decks of `om_username`"""
        self._om_username = om_username

    def list_decks(self) -> list[str]:
        """List decks for a given omakase user

        Args:
            om_username: name of the omakase user

        Returns:
            List of decks
        """
        # TODO: implement
        # BEGIN MOCK
        if self._om_username == "X":
            decks = ["deck1", "deck2"]
        else:
            decks = []
        # END MOCK
        return decks

    def get_cards_from_deck(
        self, deck_name: DeckName, om_filter_code: OmDeckFilterCode
    ) -> list[Card]:
        # TODO: implement card retrieval
        # TODO: implement filter system (from the *om* filter, select the cards with the
        # right *anki* filters)
        # TODO: raise NoSuchDeckException if no1 such deck
        # BEGIN MOCK
        if deck_name == "deck1":
            cards = [
                Card(
                    card_id=0,
                    note_id=0,
                    sort_field_value="card1",
                    due_value=0,
                    study_status=0,
                    note_type="note type 1",
                    note_fields={"c1f1": "c1fv1", "c1f2": "c1f2v2"},
                ),
                Card(
                    card_id=2,
                    note_id=1,
                    sort_field_value="card2",
                    study_status=1,
                    due_value=0,
                    note_type="note type 2",
                    note_fields={"c2f1": "c2fv1", "c2f2": "c2f2v2"},
                ),
            ]
            if om_filter_code == 1:
                cards = [cards[0]]
            elif om_filter_code == 2:
                cards = [cards[1]]
        else:
            cards = []
        # END MOCK
        return cards

    def save_note(self, note_id: int, note_fields: dict[NoteFieldName, NoteFieldValue]):
        """Update a note with `note_field`"""
        # TODO: implement all
        # BEGIN MOCK
        print(
            f"Faking that we are saving {note_id=} with new values" f" {note_fields=}."
        )
        # END MOCK


@dataclass
class DeckFilter:
    """Define a filter for a deck"""

    code: OmDeckFilterCode
    ui_label: str


class DeckFilters:
    """List of available deck filters, provided as attributes"""

    def __init__(self):
        self.all_notes = DeckFilter(code=0, ui_label="All cards")
        self.new_notes = DeckFilter(code=1, ui_label="New")
        self.in_learning_notes = DeckFilter(code=2, ui_label="In learning")


filter_label_obj_corr: dict[str, DeckFilter] = {
    v.ui_label: v for v in vars(DeckFilters()).values()
}
"""Dict of all  {DeckFilter.ui_label: DeckFilter}"""
