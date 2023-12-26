from nicegui import ui

from omakase.backend import main as back_main


@ui.page("/")
def entry_point() -> None:
    """Attach main page to /"""
    back_main.create_main_page()


# TODO : add storage secret
# TODO : Put in toml files the arguments
ui.run(
    storage_secret="bla",
    title="omakase!",
    favicon="🍣",
)
