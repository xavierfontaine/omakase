"""
Abstract classes for the observer pattern
"""
from abc import ABC, abstractmethod
from typing import Optional, Union

from beartype import beartype
from nicegui.observables import ObservableDict as NgObservableDict
from nicegui.observables import ObservableList as NgObservableList

# ============================
# Observer pattern - observers
# ============================
# TODO: generic tests


class Observer(ABC):
    """An observer class

    Method `update` dictates the behaviour of the observer upon class change.
    """

    @abstractmethod
    def update(self, observable: "Observable") -> None:
        """Handle notifications from the observable"""
        pass


# ===========================
# Observer pattern - subjects
# ===========================
class Observable:
    """Observable

    In the current library, `notify` is assumed to be called from within the self.
    """

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
            observer.update(self)


@beartype
class ObservableList(Observable):
    """Store a list-like object with notification including changes from nested elements

    Use `self.data` to access that object.

    Caution: propagation of notification
    - works for changes performed on nested list, dict, set through the usual
    manipulation methods.
    - does not work if the user modifies the properties of an element, without replacing
      that element.
    """

    def __init__(self, data: Optional[list] = None) -> None:
        data = data if data is not None else list()
        self._data = NgObservableList(data=data, on_change=self.notify)

    @property
    def data(self) -> NgObservableList:
        return self._data

    @data.setter
    def data(self, value: list) -> None:
        self._data = NgObservableList(data=value, on_change=self.notify)
        self.notify()


@beartype
class ObservableDict(Observable):
    """Store a dict-like object with notification including changes from nested elements

    Use `self.data` to access that object.

    Caution: propagation of notification
    - works for changes performed on nested list, dict, set through the usual
    manipulation methods.
    - does not work if the user modifies the properties of an element, without replacing
      that element.
    """

    def __init__(self, data: Optional[dict] = None) -> None:
        data = data if data is not None else dict()
        self._data = NgObservableDict(data=data, on_change=self.notify)

    @property
    def data(self) -> NgObservableDict:
        return self._data

    @data.setter
    def data(self, value: dict) -> None:
        self._data = NgObservableDict(data=value, on_change=self.notify)
        self.notify()


_PRIMITIVE_TYPES = Union[str, int, float, bool, None]


@beartype
class ObservablePrimitive(Observable):
    """Store a primitive object

    Use `self.data` to access that object. `self.notify` is triggered upon assignment.
    """

    def __init__(self, data: _PRIMITIVE_TYPES) -> None:
        self._data = data

    @property
    def data(self) -> _PRIMITIVE_TYPES:
        return self._data

    @data.setter
    def data(self, value: _PRIMITIVE_TYPES) -> None:
        self._data = value
        self.notify()
