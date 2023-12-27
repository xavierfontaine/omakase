"""
Login system
"""
from nicegui import app, ui

from omakase.frontend.user import LOG_STATUS_KEY


class Logger:
    # TODO: docstr
    # TODO: use ui.dialog https://nicegui.io/documentation/dialog
    def __init__(self) -> None:
        pass

    def make_button(self) -> None:
        # If already logged in
        ui.button(on_click=self._log_out, icon="logout").bind_visibility_from(
            target_object=app.storage.user, target_name=LOG_STATUS_KEY
        )
        # If not logged in
        ui.button(on_click=self._log_in, icon="login").bind_visibility_from(
            target_object=app.storage.user,
            target_name=LOG_STATUS_KEY,
            backward=lambda x: not x,
        )

    def _log_in(self) -> None:
        app.storage.user[LOG_STATUS_KEY] = True

    def _log_out(self) -> None:
        app.storage.user[LOG_STATUS_KEY] = False
