"""
Custom exceptions
"""
import traceback

from nicegui import ui


class NoSuchDeckException(Exception):
    pass


def display_exception():
    """Unified displayer for exception on the UI

    Passing an exception is unnecessary. Must be encapsulated in an Except clause
    """
    exc = traceback.format_exc()
    ui.label("Encountered the following error")
    ui.label(exc)
