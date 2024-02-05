"""
Abstract classes for the observer pattern
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

# ============================
# Observer pattern - observers
# ============================
# TODO: generic tests


class Observer:
    """An observer class

    Method `update` handles notifications from Observable classes.
    For each `Observable` class the Observer subscribes to, Child[Observer] must
    implment a handling method with name dictated by
    `self._expected_subject_handler_name`.
    """

    @abstractmethod
    def update(self) -> None:
        """Handle notifications from the observable"""
        pass


# ===========================
# Observer pattern - subjects
# ===========================
class Observable:
    def attach(self, observer: Observer) -> None:
        """Attach a new observer"""
        try:
            self._observers
        except AttributeError:
            self._observers = []
        self._observers.append(observer)

    def notify(self) -> None:
        """Notifies the observers of a change in state"""
        try:
            observers = self._observers
        except AttributeError:
            self._observers = []
        observers = self._observers
        for observer in observers:
            observer.update()
