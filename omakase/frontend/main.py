"""
Main page
"""
from nicegui import ui

from omakase.frontend.login import Logger
from omakase.frontend.tabs import (
    AddDocContent,
    AddSmallerContent,
    EditDeckTabContent,
    StatsContent,
)
from omakase.frontend.tabs.utils import TabConf
from omakase.frontend.web_user import AUTH_STATUS_KEY, point_to_web_user_data

# Configure tabs
STATS_TAB_CONF = TabConf(
    name="stats", label="Statistics", icon="auto_graph", content_generator=StatsContent
)
ADD_DOC_TAB_CONF = TabConf(
    name="add_doc",
    label="Add doc",
    icon="article",
    content_generator=AddDocContent,
)
ADD_SMALLER_TAB_CONF = TabConf(
    name="add_smaller",
    label="Add word",
    icon="record_voice_over",
    content_generator=AddSmallerContent,
)
EDIT_DECK_TAB_CONF = TabConf(
    name="edit_decks",
    label="Edit decks",
    icon="mode_edit_outline",
    content_generator=EditDeckTabContent,
)
TAB_CONF_LIST: list[TabConf] = [
    STATS_TAB_CONF,
    ADD_DOC_TAB_CONF,
    ADD_SMALLER_TAB_CONF,
    EDIT_DECK_TAB_CONF,
]


def create_main_page():
    # Getting user data (cookie-identified, stored on server)
    web_user_data = point_to_web_user_data()
    # Header
    with ui.header(elevated=True).classes("items-center justify-between"):
        # Containers for the tabs (i.e., the tab buttons, e.g. in a header)
        with ui.tabs() as tabs:
            for tab_conf in TAB_CONF_LIST:
                ui.tab(
                    name=tab_conf.name,
                    label=tab_conf.label,
                    icon=tab_conf.icon,
                ).bind_enabled_from(
                    target_object=web_user_data,
                    target_name=AUTH_STATUS_KEY,
                )
        # Login/logout
        logger = Logger()
        logger.make_button()

    # Containers for the contents
    with ui.tab_panels(tabs, value=TAB_CONF_LIST[0].name).classes("w-full"):
        for tab_conf in TAB_CONF_LIST:
            with ui.tab_panel(tab_conf.name):
                tab_conf.content_generator().display_tab_content()
