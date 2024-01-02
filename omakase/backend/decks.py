"""
Query and edit decks
"""
from dataclasses import asdict, dataclass

from omakase.annotations import FieldName, FieldValue


# ===============
# SRS-independent
# ===============
@dataclass
class Card:
    card_id: int
    note_id: int
    sort_field_value: str
    due_value: int
    note_type: str
    note_fields: dict[FieldName, FieldValue]

    def get_card_properties(self) -> dict:
        """Return the card properties as a dict"""
        return asdict(self)


# ===============
# SRS-independent
# ===============
class ManipulateDecks:
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

    def get_cards_from_deck(self, deck_name: str) -> list[Card]:
        # TODO: implement core
        # TODO: raise NoSuchDeckException if no1 such deck
        # BEGIN MOCK
        if deck_name == "deck1":
            cards = [
                Card(
                    card_id=0,
                    note_id=0,
                    sort_field_value="card1",
                    due_value=0,
                    note_type="note type 1",
                    note_fields={"c1f1": "c1fv1", "c1f2": "c1f2v2"},
                ),
                Card(
                    card_id=2,
                    note_id=1,
                    sort_field_value="card2",
                    due_value=0,
                    note_type="note type 2",
                    note_fields={"c2f1": "c2fv1", "c2f2": "c2f2v2"},
                ),
            ]
            # END MOCK
        else:
            cards = []
        return cards

    def save_note_to_deck(
        self, deck_name: str, note_id: int, note_fields: dict[FieldName, FieldValue]
    ):
        """Update a note with `note_field`"""
        # TODO: implement all
        # BEGIN MOCK
        print(
            f"Faking that we are saving {note_id=} to {deck_name=} with new values"
            f" {note_fields=}."
        )
        # END MOCK
