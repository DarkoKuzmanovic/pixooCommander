#!/usr/bin/env python3
"""
Simple test to verify NiceGUI installation and basic functionality
"""

def main():
    try:
        from nicegui import app, ui

        @ui.page('/')
        def main_page():
            ui.label('Hello NiceGUI!').classes('text-2xl')
            ui.button('Click me!', on_click=lambda: ui.notify('Button clicked!'))

        ui.run(
            title="NiceGUI Test",
            host="0.0.0.0",
            port=8080,
            reload=False,
            show=True
        )

    except ImportError as e:
        print(f"NiceGUI is not installed or not available: {e}")
        print("Please install it with: pip install nicegui")
        return 1
    except Exception as e:
        print(f"Error running NiceGUI test: {e}")
        return 1

if __name__ == "__main__":
    main()