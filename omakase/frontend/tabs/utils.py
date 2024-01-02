"""Shared utils for NiceGUI"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from nicegui import ui

from omakase.exceptions import display_exception
from omakase.frontend.web_user import AUTH_STATUS_KEY, point_to_web_user_data
from omakase.om_logging import logger


class TabContent(ABC):
    @abstractmethod
    def __init__(self):
        """Generate the content of a tab"""

    def display_tab_content(self):
        """Display content of the tab"""
        # Normal execution
        try:
            # Get pointer to user data
            self.web_user_data = point_to_web_user_data()
            # Display, depending on whether the user is logged or not
            if self.web_user_data.get(AUTH_STATUS_KEY):
                self._display_if_logged()
            else:
                self._display_if_not_logged()
        # Handle exception
        except Exception as e:  # noqa: F841
            display_exception()
            logger.exception(
                "Exception caught at the top of the tab content interface."
            )

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
