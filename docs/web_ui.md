# Pixoo Commander Web UI Documentation

This document provides comprehensive documentation for the NiceGUI web interface of the Pixoo Commander application.

## Overview

The Pixoo Commander web UI is built using the NiceGUI framework, providing a modern, responsive interface for controlling Pixoo-64 devices. The interface is organized into three main tabs:

1. **Connection**: Device connection and discovery
2. **Scenes**: Scene management with preview thumbnails
3. **Settings**: Application configuration

## Architecture

The web UI follows a modular architecture with clear separation of concerns:

```
ui/
├── app.py              # Main application structure
├── theme.py            # Theme system and CSS generation
├── preview.py          # Scene preview generation
└── pages/
    ├── connection.py    # Connection tab UI
    └── scenes.py       # Scenes tab UI
```

## Main Application (`ui/app.py`)

The main application class `PixooCommanderApp` orchestrates the entire web interface:

### Key Components

- **Header**: Contains the application title and theme selector
- **Tab Navigation**: Provides access to Connection, Scenes, and Settings tabs
- **Page Components**: Manages individual tab content

### Methods

- `setup_ui()`: Initializes the main UI structure
- `create_scenes_ui()`: Creates the scenes management interface
- `create_settings_ui()`: Creates the settings interface

## Connection Page (`ui/pages/connection.py`)

The connection page provides device connection and discovery functionality.

### Features

- **Device Connection**: Manual IP address and screen size input
- **Device Discovery**: Automatic network scanning for Pixoo devices
- **Connection Status**: Visual feedback on connection state
- **Log Output**: Real-time connection and discovery logs

### UI Elements

- `ip_input`: Text input for device IP address
- `port_input`: Number input for screen size
- `status_label`: Connection status indicator
- `connect_button`: Establishes connection to device
- `scan_button`: Initiates device discovery
- `devices_select`: Dropdown of discovered devices
- `log_output`: Log display for connection events

### Methods

- `create_ui()`: Creates the connection page UI
- `_handle_connect()`: Handles device connection logic
- `_handle_scan()`: Handles device discovery logic
- `_handle_device_select()`: Populates connection fields from selected device
- `log()`: Adds messages to the log output

## Scenes Page (`ui/pages/scenes.py`)

The scenes page provides comprehensive scene management with preview thumbnails.

### Features

- **Scene Creation**: Add new text, image, or system info scenes
- **Scene Editing**: Modify existing scene properties
- **Scene Deletion**: Remove scenes with confirmation
- **Scene Preview**: Thumbnail previews for all scenes
- **Scene Playback**: Play scenes directly to connected devices
- **Theme Support**: Consistent styling with the application theme

### Scene Types

1. **Text Scenes**: Custom text messages with content editing
2. **Image Scenes**: Display images from file paths
3. **System Info Scenes**: Real-time CPU/RAM usage display

### UI Elements

- **Scene Grid**: Responsive grid layout for scene thumbnails
- **Add Scene Dialog**: Modal form for creating new scenes
- **Edit Scene Dialog**: Modal form for editing existing scenes
- **Scene Cards**: Individual scene containers with preview and controls
- **Action Buttons**: Play, Stop, Edit, and Delete controls for each scene

### Methods

- `create_ui()`: Creates the scenes management UI
- `_refresh_scenes_display()`: Updates the scene grid display
- `_create_scene_card()`: Creates individual scene card components
- `_create_preview_scene()`: Creates preview-compatible scene objects
- `_open_add_scene_dialog()`: Opens the add scene modal
- `_open_edit_scene_dialog()`: Opens the edit scene modal
- `_handle_add_scene()`: Processes new scene creation
- `_handle_edit_scene()`: Processes scene editing
- `_confirm_delete_scene()`: Shows delete confirmation dialog
- `_handle_delete_scene()`: Processes scene deletion
- `_create_player_scene()`: Converts scene dictionaries to Player-compatible objects
- `_handle_play_scene()`: Plays a scene on the connected device
- `_handle_stop_scene()`: Stops scene playback

## Theme System (`ui/theme.py`)

The theme system provides consistent styling across the application with light and dark mode support.

### Features

- **Design Tokens**: Centralized design system based on `core/ui/tokens.json`
- **CSS Generation**: Dynamic CSS variable generation for themes
- **Theme Switching**: Runtime theme switching capability
- **Responsive Design**: Mobile-friendly layouts and components

### Components

- `ThemeManager`: Core theme management class
- `inject_theme_css()`: Injects theme CSS into the application
- `create_theme_selector()`: Creates theme selection UI component

### Methods

- `generate_css_variables()`: Generates CSS variables from design tokens
- `get_theme_css()`: Creates complete themed CSS
- `set_theme()`: Updates the current theme
- `get_current_theme()`: Returns the active theme
- `load_preferences()`: Loads theme preferences
- `get_preferences()`: Returns current theme preferences

## Preview System (`ui/preview.py`)

The preview system generates thumbnail images for scene visualization.

### Features

- **Synchronous Rendering**: PIL-based image generation
- **Asynchronous Wrapper**: Non-blocking preview generation
- **Multiple Scene Types**: Support for text, image, and system info scenes
- **Error Handling**: Graceful fallback for rendering issues

### Methods

- `render_scene_preview()`: Synchronously renders scene previews
- `async_render_scene_preview()`: Asynchronously renders scene previews
- `_is_text_scene()`: Determines if a scene is text-like
- `_is_image_scene()`: Determines if a scene is image-like
- `_render_text_scene()`: Renders text scene previews
- `_render_image_scene()`: Renders image scene previews
- `_create_placeholder_image()`: Creates fallback placeholder images

## Usage Examples

### Creating a New Text Scene

1. Navigate to the Scenes tab
2. Click "Add Scene"
3. Select "Text Scene" from the type dropdown
4. Enter your desired text content
5. Click "Add" to create the scene

### Playing a Scene

1. Ensure your device is connected (Connection tab)
2. Navigate to the Scenes tab
3. Find the scene you want to play
4. Click the "Play" button on the scene card
5. The scene will be displayed on your connected device

### Switching Themes

1. Look for the theme selector in the application header
2. Choose between "Light" and "Dark" themes
3. The application will update to reflect your selection
4. Note: A page reload may be required to see all changes

## Development

### Adding New Scene Types

To add support for new scene types:

1. Update the scene creation dialog in `ui/pages/scenes.py`
2. Add handling for the new scene type in `_create_player_scene()`
3. Update the preview system in `ui/preview.py` if needed
4. Add appropriate core scene classes in `core/scenes/`

### Customizing Themes

To customize the application theme:

1. Modify `core/ui/tokens.json` to adjust design tokens
2. The changes will automatically propagate to the CSS generation
3. Test both light and dark themes to ensure consistency

### Extending UI Components

To add new UI components:

1. Create new page modules in `ui/pages/`
2. Add the new tab to the main application in `ui/app.py`
3. Implement the UI creation logic in the new module
4. Follow the existing patterns for state management and component interaction