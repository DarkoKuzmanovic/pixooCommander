#!/usr/bin/env python3
"""
Pixoo Commander - NiceGUI Web Application
A Python web application for controlling Pixoo 64 devices
"""

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the web application"""
    try:
        # Import NiceGUI first
        from nicegui import app, ui

        # Import the application and theme system
        from ui.app import PixooCommanderApp
        from ui.theme import theme_manager, inject_theme_css

        # Inject theme CSS into the application
        inject_theme_css()

        # Create and set up the app
        app_instance = PixooCommanderApp()
        app_instance.setup_ui()

        # Run the NiceGUI app
        ui.run(
            title="Pixoo Commander",
            host="0.0.0.0",
            port=8080,
            reload=False,
            show=True,
            uvicorn_logging_level="info"
        )

    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Please install the required dependencies:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error starting the application: {e}")
        return 1

if __name__ == "__main__":
    main()