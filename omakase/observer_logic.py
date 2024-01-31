"""
Abstract classes for the observer pattern
"""
from abc import ABC

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

    pass

    @property
    def _SUBJECT_HANDLER_ROOT(self) -> str:
        """Return the root of the method names for handling new classes"""
        return "_handle_"

    def _expected_subject_handler_name(self, subject: "Observable") -> str:
        """Return the expected name for the self method that will handle notifications
        from `subject`"""
        return self._SUBJECT_HANDLER_ROOT + subject.__class__.__name__

    def update(self, subject: "Observable") -> None:
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
class Observable(ABC):
    @property
    def _observers(self) -> set[Observer]:
        if not hasattr(self, "_observers"):
            return set()
        else:
            self._observers

    def attach(self, observer: Observer) -> None:
        """Attach a new observer"""
        self._observers.add(observer)

    def notify(self):
        """Notifies the observers of a change in state"""
        for observer in self._observers:
            observer.update(subject=self)
