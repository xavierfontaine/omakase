"""
Main page
"""
from nicegui import app, ui

from omakase.frontend.login import Logger
from omakase.frontend.tabs import StatsContent
from omakase.frontend.tabs.utils import TabConf
from omakase.frontend.user import AUTH_STATUS_KEY

# Configure tabs
STATS_TAB_CONF = TabConf(
    name="stats", label="Statistics", icon="auto_graph", content_generator=StatsContent
)
ADD_DOC_TAB_CONF = TabConf(
    name="add_doc",
    label="Add doc",
    icon="article",
    content_generator=lambda: ui.label("bla"),
)
ADD_SMALLER_TAB_CONF = TabConf(
    name="add_smaller",
    label="Add word",
    icon="record_voice_over",
    content_generator=lambda: ui.label("bla"),
)
EDIT_NOTES_TAB_CONF = TabConf(
    name="edit_notes",
    label="Edit notes",
    icon="mode_edit_outline",
    content_generator=lambda: ui.label("bla"),
)
TAB_CONF_LIST: list[TabConf] = [
    STATS_TAB_CONF,
    # ADD_DOC_TAB_CONF,
    # ADD_SMALLER_TAB_CONF,
    # EDIT_NOTES_TAB_CONF,
]
#
#
# class MainPageTemplate(ABC):
#     def __init__(self):
#         """Template for creating the main page"""
#         pass
#
#     def display_page(self):
#         with ui.header(elevated=True).classes("items-center justify-between"):
#             self._header_content()
#
#     @abstractmethod
#     def _header_content(self):
#         pass
#
#     @abstractmethod
#     def _body_content(self):
#         pass
#
#
# class MainPageLogged(MainPageTemplate):
#     def _header_content(self):
#         with ui.tabs() as self._tabs:
#             for tab_conf in TAB_CONF_LIST:
#                 ui.tab(
#                     name=tab_conf.name,
#                     label=tab_conf.label,
#                     icon=tab_conf.icon,
#                 ).bind_enabled_from(
#                     target_object=app.storage.user,
#                     target_name=AUTH_STATUS_KEY,
#                 )
#         # Login/logout
#         logger = Logger()
#         logger.make_button()
#
#     def _body_content(self):
#         with ui.tab_panels(self._tabs, value=TAB_CONF_LIST[0].name).classes("w-full"):
#             for tab_conf in TAB_CONF_LIST:
#                 with ui.tab_panel(tab_conf.name):
#                     tab_conf.content_generator().display_tab_content()


def create_main_page():
    # Getting user data (cookie-identified, stored on server)
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
                    target_object=app.storage.user,
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
