"""
Custom annotated types
"""
from typing import Annotated, Literal

# Deck/card/notes-related
NoteFieldName = Annotated[str, "Field of a note"]
NoteFieldValue = Annotated[str, "Value of a note"]
NoteFieldIdx = Annotated[str, "Index of a field in a note"]
DeckName = Annotated[str, "Name of a deck"]
OmDeckFilterUiLabel = Annotated[str, "UI label of an deck filter"]
AnkiTypeCode = Annotated[int, "Anki type code (0=new, 1=learning, 2=due)"]
OmDeckFilterCode = Annotated[
    Literal[0, 1, 2], "Code of a deck filter (0 is all, 1 new, 2 in study)"
]
DeckId = Annotated[int, "ID of a deck"]
CardId = Annotated[int, "ID of a card"]
NoteId = Annotated[int, "ID of a note"]
NoteType = Annotated[int, "Name of a note type"]

# Mnemonic-related
ComponentConcept = Annotated[str, "Concept used to recall the target concept"]
TargetConcept = Annotated[str, "Concept to recall"]
GeneratedText = Annotated[str, "Generated text"]
PromptParamName = Annotated[str, "Field name in a prompt"]
Prompt = Annotated[str, "Prompt"]
MnemonicUiLabel = Annotated[str, "UI label of a mnemonic"]
