"""Shared utils for NiceGUI"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from nicegui import app, ui

from omakase.frontend.user import AUTH_STATUS_KEY


class TabContent(ABC):
    @abstractmethod
    def __init__(self):
        """Generate the content of a tab"""
        pass

    def display_tab_content(self):
        """Display content of the tab"""
        if app.storage.user.get(AUTH_STATUS_KEY):
            self._display_if_logged()
        else:
            self._display_if_not_logged()

    def _display_if_not_logged(self):
        ui.label("Please log in 🥰")

    @abstractmethod
    def _display_if_logged(self):
        """Display logic if the user is logged in"""
        pass


@dataclass
class TabConf:
    """Configure a NiceGUI tab"""

    name: str
    label: str
    icon: str
    content_generator: TabContent
