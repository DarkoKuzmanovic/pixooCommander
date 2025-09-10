#!/usr/bin/env python3
"""
Main application for Pixoo Commander NiceGUI web app
"""

from ui.pages.connection import ConnectionPage
from ui.pages.scenes import ScenesPage
from ui.theme import theme_manager, create_theme_selector, inject_theme_css

class PixooCommanderApp:
    def __init__(self):
        self.connection_page = ConnectionPage()
        # Create ScenesPage with a getter function that returns the current player
        # This allows the ScenesPage to access the player without having a direct reference
        self.scenes_page = ScenesPage(get_player=lambda: self.connection_page.player)

    def setup_ui(self):
        """Set up the main UI structure"""
        # Import here to avoid circular imports
        from nicegui import app, ui
        # Inject theme CSS early so styles are present before UI renders
        inject_theme_css()

        # Configure the app
        app.add_static_files('/assets', 'assets')

        # Create the main page
        @ui.page('/')
        def main_page():
            # Header
            with ui.header().classes('items-center justify-between'):
                ui.label('Pixoo Commander').classes('text-2xl')
                # Add theme selector to header
                create_theme_selector()

            # Main content with tabs
            with ui.column().classes('w-full p-4 gap-4 max-w-6xl mx-auto'):
                with ui.tabs().classes('w-full') as tabs:
                    connection_tab = ui.tab('Connection')
                    scenes_tab = ui.tab('Scenes')
                    settings_tab = ui.tab('Settings')

                with ui.tab_panels(tabs, value=connection_tab).classes('w-full'):
                    with ui.tab_panel(connection_tab):
                        self.connection_page.create_ui()

                    with ui.tab_panel(scenes_tab):
                        self.create_scenes_ui()

                    with ui.tab_panel(settings_tab):
                        self.create_settings_ui()

    def create_scenes_ui(self):
        """Create the scenes management interface"""
        self.scenes_page.create_ui()

    def create_settings_ui(self):
        """Create the settings interface"""
        from nicegui import ui
        with ui.column().classes('w-full gap-4'):
            ui.label('Settings').classes('text-2xl font-bold')
            ui.label('Theme settings are available in the header.').classes('text-lg')
            ui.label('More settings will be added in future updates.').classes('text-lg')

def create_app():
    """Create and configure the Pixoo Commander application"""
    # Ensure theme CSS is injected when creating app programmatically
    try:
        inject_theme_css()
    except Exception:
        # If NiceGUI isn't initialized yet, ignore and continue
        pass
    app_instance = PixooCommanderApp()
    app_instance.setup_ui()
    return app_instance