from abc import ABC, abstractmethod
from typing import Any

from omakase.backend.om_user import point_to_om_user_cache

# ============================
# Observer pattern - observers
# ============================
# TODO: generic tests


class Observer:
    """An observer class

    Method `update` handles notifications from Subject classes.
    For each `Subject` class the Observer subscribes to, Child[Observer] must implment
    a handling method with name dictated by `self._expected_subject_handler_name`.
    """

    pass

    @property
    def _SUBJECT_HANDLER_ROOT(self) -> str:
        """Return the root of the method names for handling new classes"""
        return "_handle_"

    def _expected_subject_handler_name(self, subject: "Subject") -> str:
        """Return the expected name for the self method that will handle notifications
        from `subject`"""
        return self._SUBJECT_HANDLER_ROOT + subject.__class__.__name__

    def update(self, subject: "Subject") -> None:
        """Updates based on the nature of `subject`"""
        expected_handler_name = getattr(
            self, self._expected_subject_handler_name(subject=subject), None
        )
        if expected_handler_name is None:
            observer_class_name = self.__class__.__name__
            subject_class_name = subject.__class__.__name__
            raise NotImplementedError(
                f"Class {observer_class_name} observes {subject_class_name} but has"
                " no method to handle notifications from that subject. Please implement"
                f" method {expected_handler_name}"
            )
        else:
            handler = self.__getattribute__(expected_handler_name)
            handler(subject)


# ===========================
# Observer pattern - subjects
# ===========================
class Subject(ABC):
    @property
    @abstractmethod
    def state(self) -> Any:
        pass

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class OmUserNgCachedSubject(Subject):
    """Subject pointing to user data in the memory

    The data is accessed/edited through the `state` attribute.
    """

    def __init__(self, om_username: str):
        self._user_cache = point_to_om_user_cache(om_username=om_username)
        self._observers: set[Observer] = []

    @property
    @abstractmethod
    def _root_dict(self) -> dict:
        """Dict to which `self.subject_key` belongs.

        Usually relies on self._user_cache."""
        pass

    @property
    @abstractmethod
    def subject_key(self) -> str:
        """Key identifying the state in self._root_dict"""
        pass

    def attach(self, observer: Observer) -> None:
        """Attach a new observer"""
        self._observers.add(observer)

    def notify(self):
        """Notifies the observers of a change in state"""
        for observer in self._observers:
            observer.update(subject=self)

    @property
    def state(self) -> Any:
        """State variable"""
        return self._root_dict[self.subject_key]

    @state.setter
    def state(self, value: Any) -> None:
        self.state = self._root_dict[self.subject_key]
