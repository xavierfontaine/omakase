from nicegui import ui

from omakase.frontend.main import create_main_page
from omakase.frontend.routing import ENTRY_ROUTES
from omakase.frontend.web_user import init_user_storage


@ui.page(ENTRY_ROUTES)
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
