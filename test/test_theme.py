#!/usr/bin/env python3
"""
Test script for the theme system
"""

import sys
import os
import json

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.theme import ThemeManager


def test_theme_manager():
    """Test the ThemeManager class"""
    print("Testing ThemeManager...")

    # Create a theme manager instance
    manager = ThemeManager()

    # Test loading tokens
    tokens = manager.tokens
    assert 'colors' in tokens, "Colors should be in tokens"
    assert 'typography' in tokens, "Typography should be in tokens"
    print("✓ Tokens loaded successfully")

    # Test generating CSS variables for light theme
    light_css = manager.generate_css_variables('light')
    assert ':root {' in light_css, "CSS should contain :root"
    assert '--color-primary:' in light_css, "CSS should contain primary color"
    assert '--color-background: #FFFFFF;' in light_css, "Light theme should use white background"
    print("✓ Light theme CSS variables generated successfully")

    # Test generating CSS variables for dark theme
    dark_css = manager.generate_css_variables('dark')
    assert ':root {' in dark_css, "CSS should contain :root"
    assert '--color-background: #121212;' in dark_css, "Dark theme should use dark background"
    print("✓ Dark theme CSS variables generated successfully")

    # Test generating complete CSS
    complete_css = manager.get_theme_css('light')
    assert 'body {' in complete_css, "Complete CSS should contain body styles"
    assert '--color-primary:' in complete_css, "Complete CSS should contain CSS variables"
    print("✓ Complete CSS generated successfully")

    # Test theme switching
    manager.set_theme('dark')
    assert manager.get_current_theme() == 'dark', "Theme should be dark"
    manager.set_theme('light')
    assert manager.get_current_theme() == 'light', "Theme should be light"
    print("✓ Theme switching works correctly")

    # Test preferences
    prefs = manager.get_preferences()
    assert 'theme' in prefs, "Preferences should contain theme"
    assert prefs['theme'] == 'light', "Preferences should reflect current theme"
    print("✓ Preferences system works correctly")

    print("\nAll tests passed! ✓")


def test_css_output():
    """Test the actual CSS output"""
    print("\nTesting CSS output...")

    manager = ThemeManager()

    # Generate CSS for both themes
    light_css = manager.get_theme_css('light')
    dark_css = manager.get_theme_css('dark')

    # Save to files for manual inspection
    with open('test_light_theme.css', 'w') as f:
        f.write(light_css)

    with open('test_dark_theme.css', 'w') as f:
        f.write(dark_css)

    print("✓ CSS output files generated:")
    print("  - test_light_theme.css")
    print("  - test_dark_theme.css")

    # Print a sample of the CSS
    print("\nSample of light theme CSS:")
    lines = light_css.split('\n')
    for i, line in enumerate(lines[:15]):  # Print first 15 lines
        print(f"  {line}")

    print("\nSample of dark theme CSS:")
    lines = dark_css.split('\n')
    for i, line in enumerate(lines[:15]):  # Print first 15 lines
        print(f"  {line}")


if __name__ == "__main__":
    print("Running theme system tests...\n")

    try:
        test_theme_manager()
        test_css_output()

        print("\n" + "="*50)
        print("All theme system tests completed successfully! ✓")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)