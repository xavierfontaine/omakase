"""
Login system
"""
from nicegui import ui

from omakase.backend.auth import check_password
from omakase.backend.om_user import init_missing_om_user_cache
from omakase.frontend.routing import ENTRY_ROUTES
from omakase.frontend.web_user import (
    AUTH_STATUS_KEY,
    OM_USERNAME_KEY,
    init_missing_web_user_storage,
    point_to_web_user_data,
)


class Logger:
    def __init__(self) -> None:
        """UI components for user authentification

        Use `self.make_button` to add the login/logout button, where the underlying
        logic is attached.
        """
        # Get pointer to user data
        self.web_user_data = point_to_web_user_data()
        # Prepare the dialog system behind the scene
        with ui.dialog() as self._dialog, ui.card().classes("absolute-center"):
            self._display_dialog_content()

    def make_button(self) -> None:
        """Make the login/logout button"""
        # If already logged in
        ui.button(on_click=self._on_logout_click, icon="logout").bind_visibility_from(
            target_object=self.web_user_data, target_name=AUTH_STATUS_KEY
        )
        # If not logged in
        ui.button(on_click=self._on_login_click, icon="login").bind_visibility_from(
            target_object=self.web_user_data,
            target_name=AUTH_STATUS_KEY,
            backward=lambda x: not x,
        )

    def _on_login_click(self) -> None:
        self._dialog.open()

    def _on_logout_click(self) -> None:
        self.web_user_data.clear()
        init_missing_web_user_storage()
        ui.open(ENTRY_ROUTES)

    def _display_dialog_content(self) -> ui.dialog:
        username_pwd = {"username": "", "password": ""}
        ui.input("Username").bind_value(
            target_object=username_pwd, target_name="username"
        ).on(
            "keydown.enter",
            lambda username_pwd=username_pwd: self._try_login(**username_pwd),
        )
        ui.input("Password", password=True, password_toggle_button=True).bind_value(
            target_object=username_pwd, target_name="password"
        ).on(
            "keydown.enter",
            lambda username_pwd=username_pwd: self._try_login(**username_pwd),
        )
        ui.button(
            text="Log in",
            on_click=lambda username_pwd=username_pwd: self._try_login(**username_pwd),
        )

    def _try_login(self, username: str, password: str) -> None:
        status = check_password(username=username, password=password)
        if status:
            self._on_successful_login(username=username)
        else:
            ui.notify("Wrong username/password", color="negative")
        pass

    def _on_successful_login(self, username: str):
        """Mark web_user as logged as om_user, init his om_user data wherever
        necessary.
        """
        self.web_user_data.update({OM_USERNAME_KEY: username, AUTH_STATUS_KEY: True})
        # ui.notify("Login successful!")
        self._dialog.close()
        init_missing_om_user_cache(om_username=username)
        ui.open(ENTRY_ROUTES)
