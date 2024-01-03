"""
Custom annotated types
"""
from typing import Annotated

FieldName = Annotated[str, "Field of a note"]
FieldValue = Annotated[str, "Value of a note"]
FieldIdx = Annotated[str, "Index of a field in a note"]
DeckName = Annotated[str, "Name of a deck"]
DeckId = Annotated[int, "ID of a deck"]
CardId = Annotated[int, "ID of a card"]
NoteId = Annotated[int, "ID of a note"]
