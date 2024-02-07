"""
Data objects (observables) specific to this tab
"""
from typing import Optional

from omakase.backend.decks import ObservableCard
from omakase.observer_logic import ObservableList, ObservablePrimitive


class DeckNamesObl(ObservableList[str]):
    pass


class CurrentCardsObl(ObservableList[ObservableCard]):
    pass


class CurrentCardIdxObl(ObservablePrimitive[Optional[int]]):
    pass
