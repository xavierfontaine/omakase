"""
Statistics tab
"""
from nicegui import ui

from omakase.frontend.tabs.utils import TabContent


class AddSmallerContent(TabContent):
    def __init__(self):
        pass

    def _display_if_logged(self):
        ui.label("Hey, you are logged!")
