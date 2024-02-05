"""
Abstract classes for the observer pattern
"""
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

    pass


# ===========================
# Observer pattern - subjects
# ===========================
@dataclass
class Subscription:
    """Subscription contract of an Observer with an Observable

    Args:
        method: method to call upon notification by the Observable. Should take the
        observable as an argument.
    """

    method: Callable


class Observable:


    def attach(self, subscription: Subscription) -> None:
        """Attach a new observer"""
        try:
            self._subscriptions
            print("self._subscriptions.append(subscription)")
        except AttributeError:
            self._subscriptions = []
        self._subscriptions.append(subscription)


    def notify(self) -> None:
        """Notifies the observers of a change in state"""
        try:
            subscriptions = self._subscriptions
        except AttributeError:
            self._subscriptions = []
        subscriptions = self._subscriptions
        for subscription in subscriptions:
            subscription.method()
