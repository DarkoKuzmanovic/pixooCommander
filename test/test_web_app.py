#!/usr/bin/env python3
"""
Test script for the NiceGUI web application
"""

import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_web_app_import():
    """Test that the web application can be imported without errors"""
    try:
        # Try to import the main web application module
        from web_app import main
        print("✓ web_app module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import web_app module: {e}")
        return False

def test_ui_modules_import():
    """Test that UI modules can be imported without errors"""
    try:
        # Try to import UI modules
        from ui.app import PixooCommanderApp
        print("✓ ui.app module imported successfully")

        from ui.pages.connection import ConnectionPage
        print("✓ ui.pages.connection module imported successfully")

        from ui.pages.scenes import ScenesPage
        print("✓ ui.pages.scenes module imported successfully")

        from ui.theme import ThemeManager
        print("✓ ui.theme module imported successfully")

        from ui.preview import render_scene_preview, async_render_scene_preview
        print("✓ ui.preview module imported successfully")

        return True
    except Exception as e:
        print(f"❌ Failed to import UI modules: {e}")
        return False

def test_app_initialization():
    """Test that the application can be initialized without errors"""
    try:
        # Try to create an instance of the main application class
        from ui.app import PixooCommanderApp
        app = PixooCommanderApp()
        print("✓ PixooCommanderApp instance created successfully")

        # Try to create instances of page classes
        connection_page = app.connection_page
        print("✓ ConnectionPage instance created successfully")

        scenes_page = app.scenes_page
        print("✓ ScenesPage instance created successfully")

        return True
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return False

def test_theme_system():
    """Test that the theme system works correctly"""
    try:
        # Try to create a theme manager instance
        from ui.theme import ThemeManager
        theme_manager = ThemeManager()
        print("✓ ThemeManager instance created successfully")

        # Test CSS generation
        light_css = theme_manager.get_theme_css('light')
        assert ':root {' in light_css, "Light theme CSS should contain :root"
        print("✓ Light theme CSS generated successfully")

        dark_css = theme_manager.get_theme_css('dark')
        assert ':root {' in dark_css, "Dark theme CSS should contain :root"
        print("✓ Dark theme CSS generated successfully")

        return True
    except Exception as e:
        print(f"❌ Failed to test theme system: {e}")
        return False

def main():
    """Run all tests"""
    print("Running web application tests...\n")

    tests = [
        test_web_app_import,
        test_ui_modules_import,
        test_app_initialization,
        test_theme_system
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()  # Add a blank line between tests

    print("="*50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())