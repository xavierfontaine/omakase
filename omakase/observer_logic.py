"""
Abstract classes for the observer pattern

Developer note
--------------
Some Observable subclasses below rely on both beartype and TypeVar. Unfortunately,
beartype does not fully support TypeVar as of now. For that reason,
```
class MyObl(ObservablePrimitive[int]):
    pass

my_obl = MyObl(data="oops")
```
will not raise a beartype roar.
"""
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from beartype import beartype
from nicegui.observables import ObservableDict as NgObservableDict
from nicegui.observables import ObservableList as NgObservableList

# =======
# TypeVar
# =======
# Key, value, and 'primitive' types
K = TypeVar("K")
V = TypeVar("V")
P = TypeVar("P", str, int, float, bool, None)


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

    In this library, `notify` is assumed to be called from within the self.
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
class ObservableList(Observable, Generic[V]):
    """Store a list-like object with notification including changes from nested elements

    Use `self.value` to access that object.

    Caution: propagation of notification
    - works for changes performed on nested list, dict, set through the usual
    manipulation methods.
    - does not work if the user modifies the properties of an element, without replacing
      that element.
    """

    def __init__(self, data: Optional[list[V]] = None) -> None:
        value = data if data is not None else list()
        self._value = NgObservableList(data=value, on_change=self.notify)

    @property
    def value(self) -> NgObservableList[V]:
        return self._value

    @value.setter
    def value(self, value: list[V]) -> None:
        self._value = NgObservableList(data=value, on_change=self.notify)
        self.notify()


@beartype
class ObservableDict(Observable, Generic[K, V]):
    """Store a dict-like object with notification including changes from nested elements

    Use `self.value` to access that object.

    Caution: propagation of notification
    - works for changes performed on nested list, dict, set through the usual
    manipulation methods.
    - does not work if the user modifies the properties of an element, without replacing
      that element.
    """

    def __init__(self, value: Optional[dict[K, V]] = None) -> None:
        value = value if value is not None else dict()
        self._value = NgObservableDict(data=value, on_change=self.notify)

    @property
    def value(self) -> NgObservableDict[K, V]:
        return self._value

    @value.setter
    def value(self, value: dict[K, V]) -> None:
        self._value = NgObservableDict(data=value, on_change=self.notify)
        self.notify()


@beartype
class ObservablePrimitive(Observable, Generic[P]):
    """Store a primitive object

    Use `self.value` to access that object. `self.notify` is triggered upon assignment.
    """

    def __init__(self, data: P) -> None:
        self._value = data

    @property
    def value(self) -> P:
        return self._value

    @value.setter
    def value(self, value: P) -> None:
        self._value = value
        self.notify()


class ObservableDataclass(Observable):
    """NOTE: the subclass should be decorated with `@dataclass`

    Values are accessed as usual for a dataclass"""

    def __post_init__(self) -> None:
        self.__dict__ = NgObservableDict(data=self.__dict__, on_change=self.notify)

    def __setattr__(self, name, value) -> None:
        super().__setattr__(name, value)
        self.notify()
