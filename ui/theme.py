#!/usr/bin/env python3
"""
Theme system for Pixoo Commander NiceGUI web app

This module provides functionality to convert design tokens from core/ui/tokens.json
into CSS variables and manage theme preferences.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from nicegui import ui

# Import the tokens from the core module
TOKENS_PATH = os.path.join(os.path.dirname(__file__), '..', 'core', 'ui', 'tokens.json')

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages theme generation and preferences for the NiceGUI application."""

    def __init__(self, tokens_path: str = TOKENS_PATH):
        """Initialize the theme manager with design tokens."""
        self.tokens_path = tokens_path
        self.tokens = self._load_tokens()
        self.current_theme = 'light'  # Default theme
        self.preferences = {
            'theme': self.current_theme,
            'font_size': 'normal'
        }

    def _load_tokens(self) -> Dict[str, Any]:
        """Load design tokens from JSON file."""
        try:
            with open(self.tokens_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load tokens: {e}")
            # Return default tokens if file cannot be loaded
            return {
                "colors": {
                    "primary": "#007BFF",
                    "primary-variant": "#0056B3",
                    "secondary": "#6C757D",
                    "secondary-variant": "#495057",
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "error": "#DC3545",
                    "info": "#17A2B8",
                    "background": {
                        "light": "#FFFFFF",
                        "dark": "#121212"
                    },
                    "surface": {
                        "light": "#F8F9FA",
                        "dark": "#1E1E1E"
                    },
                    "text-primary": {
                        "light": "#212529",
                        "dark": "#FFFFFF"
                    },
                    "text-secondary": {
                        "light": "#6C757D",
                        "dark": "#ADB5BD"
                    },
                    "border": "#DEE2E6",
                    "shadow": "rgba(0, 0, 0, 0.1)"
                },
                "typography": {
                    "font-family-base": "system-ui, -apple-system, sans-serif",
                    "font-size-h1": "24px",
                    "font-size-h2": "20px",
                    "font-size-h3": "16px",
                    "font-size-body": "14px",
                    "font-size-label": "12px",
                    "font-weight-light": 300,
                    "font-weight-normal": 400,
                    "font-weight-medium": 500,
                    "font-weight-bold": 700,
                    "line-height-tight": 1.25,
                    "line-height-normal": 1.5
                },
                "spacing": {
                    "xs": "4px",
                    "s": "8px",
                    "m": "16px",
                    "l": "24px",
                    "xl": "32px"
                },
                "sizing": {
                    "xs": "8px",
                    "s": "16px",
                    "m": "24px",
                    "l": "32px",
                    "xl": "64px"
                },
                "border-radius": {
                    "s": "4px",
                    "m": "8px"
                },
                "shadows": {
                    "low": "0 1px 3px rgba(0, 0, 0, 0.1)",
                    "medium": "0 4px 6px rgba(0, 0, 0, 0.1)",
                    "high": "0 8px 16px rgba(0, 0, 0, 0.1)"
                }
            }

    def generate_css_variables(self, theme: str = 'light') -> str:
        """
        Generate CSS variables from design tokens for the specified theme.

        Args:
            theme: Theme name ('light' or 'dark')

        Returns:
            String containing CSS variable definitions
        """
        if theme not in ['light', 'dark']:
            theme = 'light'

        self.current_theme = theme
        tokens = self.tokens

        css_vars = []
        css_vars.append(":root {")

        # Colors
        colors = tokens.get('colors', {})
        for key, value in colors.items():
            if isinstance(value, dict):
                # Handle theme-specific colors (background, surface, text)
                if theme in value:
                    css_vars.append(f" --color-{key.replace('_', '-')}: {value[theme]};")
            else:
                # Handle regular colors
                css_vars.append(f"  --color-{key.replace('_', '-')}: {value};")

        # Typography
        typography = tokens.get('typography', {})
        for key, value in typography.items():
            css_vars.append(f"  --{key.replace('_', '-')}: {value};")

        # Spacing
        spacing = tokens.get('spacing', {})
        for key, value in spacing.items():
            css_vars.append(f"  --spacing-{key}: {value};")

        # Sizing
        sizing = tokens.get('sizing', {})
        for key, value in sizing.items():
            css_vars.append(f"  --sizing-{key}: {value};")

        # Border radius
        border_radius = tokens.get('border-radius', {})
        for key, value in border_radius.items():
            css_vars.append(f"  --border-radius-{key}: {value};")

        # Shadows
        shadows = tokens.get('shadows', {})
        for key, value in shadows.items():
            css_vars.append(f"  --shadow-{key}: {value};")

        css_vars.append("}")

        return "\n".join(css_vars)

    def get_theme_css(self, theme: str = 'light') -> str:
        """
        Generate complete CSS with variables and base styles.

        Args:
            theme: Theme name ('light' or 'dark')

        Returns:
            String containing complete CSS
        """
        css_vars = self.generate_css_variables(theme)

        # Base styles using CSS variables
        base_styles = """
/* Base styles using CSS variables */
body {
    background-color: var(--color-background);
    color: var(--color-text-primary);
    font-family: var(--font-family-base);
    font-size: var(--font-size-body);
    line-height: var(--line-height-normal);
}

/* Typography */
h1 {
    font-size: var(--font-size-h1);
    font-weight: var(--font-weight-bold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--spacing-m);
}

h2 {
    font-size: var(--font-size-h2);
    font-weight: var(--font-weight-medium);
    line-height: var(--line-height-tight);
    margin-bottom: var(--spacing-s);
}

h3 {
    font-size: var(--font-size-h3);
    font-weight: var(--font-weight-medium);
    margin-bottom: var(--spacing-s);
}

/* Buttons */
.nicegui-button {
    border-radius: var(--border-radius-m);
    padding: var(--spacing-s) var(--spacing-m);
    font-weight: var(--font-weight-medium);
    transition: all 0.2s ease;
}

.nicegui-button:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);
}

.nicegui-button.primary {
    background-color: var(--color-primary);
    color: white;
    border: none;
}

.nicegui-button.primary:hover {
    background-color: var(--color-primary-variant);
}

.nicegui-button.secondary {
    background-color: var(--color-secondary);
    color: white;
    border: none;
}

.nicegui-button.secondary:hover {
    background-color: var(--color-secondary-variant);
}

/* Cards */
.nicegui-card {
    background-color: var(--color-surface);
    border-radius: var(--border-radius-m);
    box-shadow: var(--shadow-low);
    padding: var(--spacing-m);
    margin-bottom: var(--spacing-m);
}

/* Inputs */
.nicegui-input {
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-s);
    padding: var(--spacing-s);
    background-color: var(--color-background);
    color: var(--color-text-primary);
}

.nicegui-input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* Labels */
.nicegui-label {
    color: var(--color-text-primary);
    font-weight: var(--font-weight-medium);
    margin-bottom: var(--spacing-xs);
}

/* Badges */
.nicegui-badge {
    border-radius: var(--border-radius-s);
    padding: var(--spacing-xs) var(--spacing-s);
    font-size: var(--font-size-label);
    font-weight: var(--font-weight-medium);
}

/* Grid and layout */
.nicegui-column {
    gap: var(--spacing-m);
}

.nicegui-row {
    gap: var(--spacing-m);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    h1 {
        font-size: calc(var(--font-size-h1) * 0.8);
    }

    h2 {
        font-size: calc(var(--font-size-h2) * 0.85);
    }

    .nicegui-card {
        padding: var(--spacing-s);
    }
}
"""

        return css_vars + base_styles

    def set_theme(self, theme: str) -> None:
        """
        Set the current theme and update preferences.

        Args:
            theme: Theme name ('light' or 'dark')
        """
        if theme in ['light', 'dark']:
            self.current_theme = theme
            self.preferences['theme'] = theme
            logger.info(f"Theme set to: {theme}")

    def get_current_theme(self) -> str:
        """Get the current theme."""
        return self.current_theme

    def load_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Load theme preferences.

        Args:
            preferences: Dictionary containing theme preferences
        """
        self.preferences.update(preferences)
        if 'theme' in preferences:
            self.current_theme = preferences['theme']

    def get_preferences(self) -> Dict[str, Any]:
        """Get current theme preferences."""
        return self.preferences.copy()


# Global theme manager instance
theme_manager = ThemeManager()


def inject_theme_css() -> None:
    """
    Inject the current theme CSS into the NiceGUI application.
    This should be called during app initialization.
    """
    css = theme_manager.get_theme_css(theme_manager.get_current_theme())
    ui.add_head_html(f"<style>{css}</style>")


def create_theme_selector() -> None:
    """
    Create a theme selector UI component.
    This adds a theme switcher to the application.
    """
    with ui.row().classes('items-center gap-2'):
        ui.label('Theme:')
        theme_select = ui.select(
            {'light': 'Light', 'dark': 'Dark'},
            value=theme_manager.get_current_theme()
        ).classes('w-32')
        theme_select.tooltip('Switch between light and dark themes')
        # Use the component's .value in the event handler and coerce to str to satisfy type checkers
        theme_select.on('update:model-value', lambda _: _on_theme_change(str(theme_select.value or 'light')))


def _on_theme_change(theme: str) -> None:
    """
    Handle theme change events.

    Args:
        theme: Selected theme ('light' or 'dark')
    """
    theme_manager.set_theme(theme)
    # In a real implementation, we would reload the page or dynamically update styles
    # For now, we'll just notify the user
    ui.notify(f"Theme changed to {theme}. Reload the page to see changes.")


# Example usage
if __name__ == "__main__":
    # Example of generating CSS for light theme
    manager = ThemeManager()
    light_css = manager.get_theme_css('light')
    print("Light theme CSS:")
    print(light_css)

    # Example of generating CSS for dark theme
    dark_css = manager.get_theme_css('dark')
    print("\nDark theme CSS:")
    print(dark_css)