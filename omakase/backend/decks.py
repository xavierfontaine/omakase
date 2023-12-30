"""
Query and edit decks
"""
from dataclasses import asdict, dataclass

from omakase.exceptions import NoSuchDeckException


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

    def to_dict(self):
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
                ),
                Card(
                    card_id=2,
                    note_id=1,
                    sort_field_value="card2",
                    due_value=0,
                    note_type="note type 2",
                ),
            ]
            # END MOCK
        else:
            cards = []
        return cards
