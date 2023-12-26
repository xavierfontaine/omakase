"""
Main page
"""
from nicegui import ui

from omakase.backend.nicegui_utils import TabConf

# Configure tabs
STATS_TAB_CONF = TabConf(
    name="stats",
    label="Statistics",
    icon="auto_graph",
    content_generator=lambda: ui.label("bla"),
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
    ADD_DOC_TAB_CONF,
    ADD_SMALLER_TAB_CONF,
    EDIT_NOTES_TAB_CONF,
]


def create_main_page():
    # Header
    with ui.header(elevated=True).classes("items-center justify-between"):
        # Containers for the tabs (i.e., the tab buttons, e.g. in a header)
        with ui.tabs() as tabs:
            for tab_conf in TAB_CONF_LIST:
                ui.tab(
                    name=tab_conf.name,
                    label=tab_conf.label,
                    icon=tab_conf.icon,
                )
        # Login/logout button
        # TODO: use ui.dialog https://nicegui.io/documentation/dialog
        mydict = {"bla": True}

        def up():
            mydict["bla"] = not mydict["bla"]

        ui.button(on_click=up, icon="search").bind_visibility_from(
            target_object=mydict, target_name="bla"
        )
        ui.button(on_click=up, icon="auto_graph").bind_visibility_from(
            target_object=mydict, target_name="bla", backward=lambda x: not x
        )

    # Containers for the contents
    with ui.tab_panels(tabs, value=TAB_CONF_LIST[0].name).classes("w-full"):
        for tab_conf in TAB_CONF_LIST:
            with ui.tab_panel(tab_conf.name):
                tab_conf.content_generator()

    # # Header
    # with ui.header(elevated=True).classes("items-center justify-between"):
    #     # Statistics
    #     ui.button(on_click=lambda: left_drawer.toggle(), icon="menu")
    #     # Title
    #     ui.label("OMAKASE")
    #     # Logout
    #     ui.button(
    #         icon="logout"
    #     )  # on_click=lambda: (app.storage.user.clear(), ui.open('/login')),
    # # Drawer
    # with ui.left_drawer().classes("bg-blue-100") as left_drawer:
    #     ui.label("Side menu")
    # # Displayed content
    # # TODO
