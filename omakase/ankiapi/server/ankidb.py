"""
Manipulate an Anki db
"""
from typing import Optional

from anki.collection import Collection

from omakase.annotations import CardId, DeckId, DeckName, FieldIdx, FieldValue, NoteId
from omakase.om_logging import logger


class ManipulateAnkiDb:
    def __init__(self, db_path: str) -> None:
        """Manipulate an Anki database

        Must be used as a context manager.

        Args:
            db_path: path to a 'collection.anki2' file
        """
        self._db_path = db_path

    def __enter__(self) -> "ManipulateAnkiDb":
        """Open the connexion to db"""
        self._coll = Collection(COL_PATH)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        """Close the connexion to db"""
        # CLose connexion
        self._coll.close()
        # Propagate any error
        no_exception_occured = exc_value is None
        return no_exception_occured

    def list_decks(self) -> dict[DeckId, DeckName]:
        deck_list = {deck["id"]: deck["name"] for deck in self._coll.decks.all()}
        return deck_list

    def list_cards_in_deck(self, deck_id: DeckId) -> list[CardId]:
        cids = self._coll.decks.cids(did=deck_id, children=True)
        return cids

    def _get_noteid_for_card(self, card_id: CardId) -> NoteId:
        card = self._coll.get_card(id=card_id)
        nid = card.note().id
        return nid

    def list_notes_in_deck(
        self, deck_id: DeckId, new: Optional[bool] = None
    ) -> list[NoteId]:
        # Security check
        if not str(deck_id).isdigit():
            logger.critical(
                f"A non-digit deck id {deck_id=} was passed to build an sql query"
            )
            return []
        # Building the query (incl if new/not new)
        deck_name = self.list_decks()[deck_id]
        query = f'deck:"{deck_name}"'
        if new is not None:
            if new:
                query += " is:new"
            else:
                query += " -is:new"
        # Getting the ids
        nids = self._coll.find_notes(query=query)
        return nids

    def update_fields(
        self, note_id: NoteId, updates=dict[FieldIdx, FieldValue]
    ) -> None:
        """Update the fields of a note"""
        note = self._coll.get_note(id=note_id)
        for idx, content in updates.items():
            note.fields[idx] = content
        self._coll.update_note(note=note)


# TODO: remove
if __name__ == "__main__":
    COL_PATH = "/home/xavier/.local/share/Anki2/User 1/collection.anki2"
    with ManipulateAnkiDb(db_path=COL_PATH) as anki_manipulator:
        decks = anki_manipulator.list_decks()
        print(f"{decks=}")
        deck_id = list(decks.keys())[-1]
        deck_name = decks[deck_id]
        print(f"selecting deck '{deck_name}' ({deck_id=})")
        card_list = anki_manipulator.list_cards_in_deck(deck_id=deck_id)
        print(f"{card_list=}")
        note_list = anki_manipulator.list_notes_in_deck(deck_id=deck_id)
        print(f"{note_list=}")
        print(f"{len(note_list)=} (all)")
        note_list = anki_manipulator.list_notes_in_deck(deck_id=deck_id, new=True)
        print(f"{len(note_list)=} (new)")
        note_list = anki_manipulator.list_notes_in_deck(deck_id=deck_id, new=False)
        print(f"{len(note_list)=} (not new)")
        # note_id = 1700992311745
        # anki_manipulator.update_fields(note_id=note_id, updates={1:"bla"})
