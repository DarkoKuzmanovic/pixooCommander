"""
ThemeManager for handling dynamic theming in Pixoo Commander.
This class manages loading, applying, and switching themes using tokens from tokens.json.
Based on specifications in docs/design-system/theming.md.
"""

from PySide6.QtCore import QObject, Signal, QSettings, QTimer
from PySide6.QtWidgets import QApplication
import json
import os

class ThemeManager(QObject):
    """
    Singleton or application-wide instance that loads, applies, and manages themes.
    Supports light/dark/auto modes with token overrides.
    """
    themeChanged = Signal(str)

    def __init__(self):
        """
        Initialize ThemeManager.
        Loads default themes and sets current to 'light'.
        """
        super().__init__()
        self.themes = {}
        self.current_theme = 'light'
        self.load_themes('core/ui/tokens.json')

    def load_themes(self, path: str) -> dict:
        """
        Load themes from JSON file or directory.
        Parses theme files and maps to token overrides.

        Args:
            path (str): Path to themes directory or tokens.json.

        Returns:
            dict: Loaded themes dictionary.
        """
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)

                # Create light theme
                light_tokens = self._extract_light_tokens(data)
                self.themes['light'] = {'tokens': light_tokens}

                # Create dark theme
                dark_tokens = self._extract_dark_tokens(data)
                self.themes['dark'] = {'tokens': dark_tokens}

        return self.themes

    def _extract_light_tokens(self, data: dict) -> dict:
        """Extract light theme tokens from the data structure."""
        tokens = {}

        # Colors
        for key, value in data['colors'].items():
            if isinstance(value, dict) and 'light' in value:
                tokens[f'color-{key}'] = value['light']
            else:
                tokens[f'color-{key}'] = value

        # Typography
        for key, value in data['typography'].items():
            tokens[key] = value

        # Spacing
        for key, value in data['spacing'].items():
            tokens[f'spacing-{key}'] = value

        # Sizing
        for key, value in data['sizing'].items():
            tokens[f'size-{key}'] = value

        # Border radius
        for key, value in data['border-radius'].items():
            tokens[f'border-radius-{key}'] = value

        # Shadows
        for key, value in data['shadows'].items():
            tokens[f'shadow-{key}'] = value

        return tokens

    def _extract_dark_tokens(self, data: dict) -> dict:
        """Extract dark theme tokens from the data structure."""
        tokens = {}

        # Colors
        for key, value in data['colors'].items():
            if isinstance(value, dict) and 'dark' in value:
                tokens[f'color-{key}'] = value['dark']
            else:
                tokens[f'color-{key}'] = value

        # Typography
        for key, value in data['typography'].items():
            tokens[key] = value

        # Spacing
        for key, value in data['spacing'].items():
            tokens[f'spacing-{key}'] = value

        # Sizing
        for key, value in data['sizing'].items():
            tokens[f'size-{key}'] = value

        # Border radius
        for key, value in data['border-radius'].items():
            tokens[f'border-radius-{key}'] = value

        # Shadows
        for key, value in data['shadows'].items():
            tokens[f'shadow-{key}'] = value

        return tokens

    def switch_theme(self, theme_name: str):
        """
        Switch to a specific theme.
        Applies the theme, generates QSS, and emits signal.

        Args:
            theme_name (str): Name of theme to switch to (e.g., 'light', 'dark').
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            qss = self.generate_qss(self.themes[theme_name])
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                app.setStyleSheet(qss)
            self.themeChanged.emit(theme_name)
            self.save_preference(theme_name)

    def generate_qss(self, theme: dict) -> str:
        """
        Generate Qt stylesheet (QSS) from theme tokens.
        Uses string templating to interpolate tokens.

        Args:
            theme (dict): Theme data with tokens.

        Returns:
            str: Generated QSS string.
        """
        tokens = theme['tokens']

        # Create a comprehensive QSS template that covers all components
        qss_template = """
        /* Global styles */
        QWidget {{
            background-color: {color-background};
            color: {color-text-primary};
            font-family: {font-family-base};
            font-size: {font-size-body};
        }}

        /* MainWindow and core containers */
        QMainWindow, QDialog {{
            background-color: {color-background};
        }}

        QGroupBox {{
            border: 1px solid {color-border};
            border-radius: {border-radius-s};
            margin-top: 0.5em;
            padding-top: 0.5em;
            font-weight: {font-weight-medium};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 {spacing-s};
        }}

        /* Buttons - Primary */
        QPushButton[primary="true"] {{
            background-color: {color-primary};
            color: white;
            border: none;
            border-radius: {border-radius-s};
            padding: {spacing-xs} {spacing-s};
            font-weight: {font-weight-medium};
            min-height: {size-s};
        }}

        QPushButton[primary="true"]:hover {{
            background-color: {color-primary-variant};
            opacity: 0.9;
        }}

        QPushButton[primary="true"]:pressed {{
            background-color: {color-primary-variant};
            opacity: 1.0;
        }}

        QPushButton[primary="true"]:disabled {{
            background-color: {color-secondary};
            opacity: 0.5;
        }}

        /* Buttons - Secondary */
        QPushButton {{
            background-color: {color-background};
            color: {color-primary};
            border: 1px solid {color-primary};
            border-radius: {border-radius-s};
            padding: {spacing-xs} {spacing-s};
            font-weight: {font-weight-medium};
            min-height: {size-s};
        }}

        QPushButton:hover {{
            background-color: {color-primary};
            color: white;
        }}

        QPushButton:pressed {{
            background-color: {color-primary-variant};
            color: white;
        }}

        QPushButton:disabled {{
            background-color: {color-background};
            color: {color-text-secondary};
            border-color: {color-border};
            opacity: 0.5;
        }}

        /* Input fields */
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {color-surface};
            color: {color-text-primary};
            border: 1px solid {color-border};
            border-radius: {border-radius-s};
            padding: {spacing-xs} {spacing-s};
            selection-background-color: {color-primary};
            selection-color: white;
        }}

        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
            border-color: {color-primary};
            outline: 2px solid {color-primary};
        }}

        QLineEdit:disabled, QTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
            background-color: {color-background};
            color: {color-text-secondary};
            border-color: {color-border};
        }}

        /* Combo box */
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: {size-s};
            border-left-width: 1px;
            border-left-color: {color-border};
            border-top-right-radius: {border-radius-s};
            border-bottom-right-radius: {border-radius-s};
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {color-text-primary};
            width: 0;
            height: 0;
            margin-right: {spacing-s};
        }}

        /* Scroll bars */
        QScrollBar:vertical {{
            background: {color-background};
            width: {size-s};
            border-radius: {border-radius-s};
        }}

        QScrollBar::handle:vertical {{
            background: {color-secondary};
            border-radius: {border-radius-s};
            min-height: {size-m};
        }}

        QScrollBar::handle:vertical:hover {{
            background: {color-primary};
        }}

        /* Labels */
        QLabel {{
            color: {color-text-primary};
        }}

        QLabel:disabled {{
            color: {color-text-secondary};
        }}

        /* Tab widget */
        QTabWidget::pane {{
            border: 1px solid {color-border};
            border-radius: {border-radius-s};
        }}

        QTabBar::tab {{
            background: {color-surface};
            border: 1px solid {color-border};
            border-bottom-color: {color-background};
            border-top-left-radius: {border-radius-s};
            border-top-right-radius: {border-radius-s};
            min-width: 8ex;
            padding: {spacing-xs} {spacing-m};
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background: {color-background};
            border-bottom-color: {color-background};
        }}

        QTabBar::tab:hover {{
            background: {color-primary};
            color: white;
        }}

        /* List widgets */
        QListWidget {{
            background-color: {color-surface};
            border: 1px solid {color-border};
            border-radius: {border-radius-s};
        }}

        QListWidget::item {{
            padding: {spacing-xs} {spacing-s};
            border-bottom: 1px solid {color-border};
        }}

        QListWidget::item:selected {{
            background-color: {color-primary};
            color: white;
        }}

        QListWidget::item:hover {{
            background-color: rgba(0, 123, 255, 0.1);
        }}

        /* Check boxes */
        QCheckBox {{
            spacing: {spacing-s};
        }}

        QCheckBox::indicator {{
            width: {size-s};
            height: {size-s};
        }}

        QCheckBox::indicator:unchecked {{
            border: 1px solid {color-border};
            background-color: {color-background};
        }}

        QCheckBox::indicator:checked {{
            border: 1px solid {color-primary};
            background-color: {color-primary};
        }}

        QCheckBox::indicator:checked::after {{
            content: "";
            position: absolute;
            left: 4px;
            top: 1px;
            width: 4px;
            height: 8px;
            border: solid white;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg);
        }}

        /* Status bar */
        QStatusBar {{
            background-color: {color-surface};
            border-top: 1px solid {color-border};
            padding: {spacing-xs};
        }}

        /* Menu bar */
        QMenuBar {{
            background-color: {color-background};
            border-bottom: 1px solid {color-border};
        }}

        QMenuBar::item {{
            background: transparent;
            padding: {spacing-xs} {spacing-s};
        }}

        QMenuBar::item:selected {{
            background: {color-primary};
            color: white;
        }}

        QMenuBar::item:pressed {{
            background: {color-primary-variant};
            color: white;
        }}

        /* Menu */
        QMenu {{
            background-color: {color-surface};
            border: 1px solid {color-border};
            border-radius: {border-radius-s};
        }}

        QMenu::item {{
            padding: {spacing-xs} {spacing-m};
        }}

        QMenu::item:selected {{
            background-color: {color-primary};
            color: white;
        }}

        /* Play Controls Component */
        QPushButton#scenes_play_btn, QPushButton#scenes_pause_btn, QPushButton#scenes_prev_btn, QPushButton#scenes_next_btn {{
            background-color: {color-primary};
            color: white;
            border: none;
            border-radius: {border-radius-s};
            padding: {spacing-xs} {spacing-s};
            font-weight: {font-weight-medium};
            min-height: {size-s};
            min-width: {size-m};
        }}

        QPushButton#scenes_play_btn:hover, QPushButton#scenes_pause_btn:hover, QPushButton#scenes_prev_btn:hover, QPushButton#scenes_next_btn:hover {{
            background-color: {color-primary-variant};
            opacity: 0.9;
        }}

        QPushButton#scenes_play_btn:pressed, QPushButton#scenes_pause_btn:pressed, QPushButton#scenes_prev_btn:pressed, QPushButton#scenes_next_btn:pressed {{
            background-color: {color-primary-variant};
            opacity: 1.0;
        }}

        QPushButton#scenes_play_btn:disabled, QPushButton#scenes_pause_btn:disabled, QPushButton#scenes_prev_btn:disabled, QPushButton#scenes_next_btn:disabled {{
            background-color: {color-secondary};
            color: {color-text-secondary};
            opacity: 0.5;
        }}

        /* Preview pane (custom widget) */
        QLabel#preview_label {{
            background-color: {color-surface};
            border: 1px solid {color-border};
            border-radius: {border-radius-m};
            padding: {spacing-m};
        }}

        /* Scene list item widgets */
        QWidget#sceneItemWidget {{
            background-color: transparent;
        }}

        QLabel#titleLabel {{
            font-weight: {font-weight-medium};
        }}

        QLabel#dragHandle {{
            color: {color-text-secondary};
            cursor: move;
        }}

        QLabel#dragHandle:hover {{
            color: {color-primary};
        }}
        """.format(**tokens)

        return qss_template

    def save_preference(self, theme_name: str):
        """
        Persist user theme preference to QSettings.
        """
        settings = QSettings("PixooCommander", "Theme")
        settings.setValue("current_theme", theme_name)

    def load_preference(self) -> str:
        """
        Load user theme preference from QSettings.

        Returns:
            str: Theme name preference or 'light' as default.
        """
        settings = QSettings("PixooCommander", "Theme")
        theme = settings.value("current_theme", "light")
        return str(theme) if theme else "light"

    def apply_theme(self):
        """
        Apply current theme (deferred for UI updates).
        """
        def _apply():
            self.switch_theme(self.current_theme)
        QTimer.singleShot(0, _apply)