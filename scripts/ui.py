from nicegui import ui

from omakase.backend.main import create_main_page
from omakase.backend.user import init_user_storage


@ui.page("/")
def entry_point() -> None:
    """Attach main page to /"""
    init_user_storage()
    create_main_page()


# TODO : add storage secret
# TODO : Put in toml files the arguments
ui.run(
    storage_secret="bla",
    title="omakase!",
    favicon="🍣",
)
