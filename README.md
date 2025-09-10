# Pixoo Commander

A Python application for controlling Pixoo-64 devices with both Qt6 desktop and NiceGUI web interfaces.

## Features

- Connect to your Pixoo-64 device over Wi-Fi
- Automatic device discovery and scanning
- Send custom text messages to the device
- Display images from your computer
- Show real-time system information (CPU/RAM usage)
- Continuous system monitoring
- Dual-screen display with automatic rotation
- Custom message display with color selection
- Manual screen switching controls
- Scene management with preview thumbnails
- Theme support (light/dark mode)
- Responsive web interface

## Prerequisites

- Python 3.7 or higher
- A Pixoo 64 device connected to the same Wi-Fi network

## Installation

Optionally, create and activate a virtual environment (recommended for development):

```bash
py -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
```

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Qt6 Desktop Application (Original)

1. Run the original Qt6 application:

   ```bash
   python qt_app.py
   ```

2. The application window will open with all the traditional controls:
   - Device connection settings (IP address, screen size)
   - Device discovery and scanning
   - Text message input with color selection
   - Image browsing and display
   - System information monitoring
   - Screen rotation controls
   - Custom message creation

### NiceGUI Web Application (New)

1. Run the web application (development):

   ```bash
   python web_app.py
   ```

2. Open your browser to <http://localhost:8080>

3. What the web UI provides:
   - **Connection**: device discovery, manual IP entry, screen size, and connect/disconnect controls.
   - **Scenes**: full scene management with thumbnail previews, add/edit/delete dialogs, scene ordering and playback controls. Thumbnails are generated server-side (see [`ui/preview.py`](ui/preview.py:1)) and cached for performance.
   - **Settings**: application preferences and theme selector (light/dark).

4. Thumbnails and previews:
   - Previews are produced by [`ui/preview.py`](ui/preview.py:1); Pillow (PIL) enables richer PNG previews. Install Pillow for full preview functionality:

     ```bash
     pip install pillow
     ```

   - If Pillow is not available, a simple placeholder preview is used.
   - Previews are 64×64 PNGs encoded as data URIs and cached in memory to reduce CPU usage.

5. Scenes supported:
   - **Text scenes**: multi-line text, per-line colors, alignment, spacing, scrolling options and duration.
   - **Image scenes**: local image path with fit modes.
   - **SysInfo scenes**: theme-aware system information displays (CPU/RAM/time).

6. Developer notes:
   - Main web entry: `web_app.py` (run the server)
   - Scenes page implementation: [`ui/pages/scenes.py`](ui/pages/scenes.py:1)
   - Preview renderer: [`ui/preview.py`](ui/preview.py:1)
   - Core scene classes: `core/scenes/` (`text.py`, `image.py`, `sysinfo.py`)
   - Example scenes: call `Example()` inside the Scenes page for quick manual testing.

7. Running tests:
   - Unit and integration tests remain in `test/`. Some tests that interact with devices require `PIXOO_IP` and network access.

## Testing

Run tests from the project root using pytest (network tests require a real device and PIXOO_IP env var):

Run tests with pytest (network tests require a real device):

```bash
pip install pytest  # or python -m pip install pytest
pytest -q                 # runs non-network tests
PIXOO_IP=192.168.0.103 pytest -m network -q
```

Network tests are marked with `@pytest.mark.network` and will be skipped unless `PIXOO_IP` is set and the `network` marker is selected.

## CLI Demo

Render a minimal sample project to a device from the command line:

```bash
python tools/demo_project.py --ip 192.168.0.103 --image path/to/image.png --size 64
# or
PIXOO_IP=192.168.0.103 python tools/demo_project.py
```

## Screen Rotation

The application supports automatic rotation between different screen modes:

1. Image display
2. System information (CPU/RAM usage with time)
3. Custom message display

You can configure the rotation interval (5-60 seconds) and enable/disable rotation as needed.

## Custom Messages

To use the custom message feature:

1. Enter your desired message in the "Message" field
2. Click "Select Color" to choose a color for your message
3. Click "Send Custom Message" to display it on your device
4. The custom message screen will also be included in screen rotation when enabled

## Multi-Line Text Support

The application now supports multi-line text scenes with enhanced formatting options:

- **Multi-line Input**: Use the text editor to create messages with multiple lines
- **Text Alignment**: Align text left, center, or right
- **Line Spacing**: Control the spacing between lines
- **Per-line Colors**: Set different colors for each line
- **Backward Compatible**: Existing single-line text projects continue to work

### Usage Examples

Create a multi-line text scene with centered alignment:

```json
{
  "name": "Multi-line Example",
  "type": "text",
  "duration_s": 10,
  "config": {
    "text_options": {
      "align": "center",
      "color": [255, 255, 255]
    },
    "lines": [
      {"text": "Welcome!", "y": 0},
      {"text": "to our", "y": 12, "color": [0, 255, 0]},
      {"text": "Pixoo Display", "y": 24}
    ]
  }
}
```

Create a multi-line text scene with different alignments:

```json
{
  "name": "Mixed Alignment",
  "type": "text",
  "duration_s": 10,
  "config": {
    "text_options": {
      "align": "left",
      "color": [255, 255, 255]
    },
    "lines": [
      {"text": "Left aligned", "y": 0},
      {"text": "Centered", "y": 12, "x": "center"},
      {"text": "Right aligned", "y": 24, "x": "right"}
    ]
  }
}
```

### Configuration Options

- `text_options.align`: Text alignment (`"left"`, `"center"`, or `"right"`)
- `text_options.color`: Default RGB color for all lines (array of 3 integers 0-255)
- `lines`: Array of line objects with:
  - `text`: The text to display (required)
  - `y`: Y position in pixels (optional, defaults to line index * 12)
  - `x`: X position in pixels or alignment string (optional)
- `color`: RGB color for this line (optional, overrides default)

## Screen Sizes

Different Pixoo devices have different screen sizes:

- Pixoo-64: Screen size 64
- Pixoo32: Screen size 32
- Pixoo16: Screen size 16

The application defaults to screen size 64 for Pixoo-64 devices.

## Troubleshooting

- Make sure your Pixoo-64 is powered on and connected to Wi-Fi
- Ensure your computer is on the same Wi-Fi network
- Check that no firewall is blocking the connection
- Try different IP addresses if the default doesn't work
- Verify you're using the correct screen size for your device

## Development

For development guidelines, coding style, testing, and contribution rules, see [AGENTS.md](AGENTS.md).

## Architecture

The application is structured with a clear separation of concerns:

- **Core Modules** (`core/`): Business logic for device communication, scene management, and playback
- **UI Modules** (`ui/`): NiceGUI web interface components
- **Qt6 Application** (`qt_app.py`): Original desktop application (preserved for backward compatibility)
- **Web Application** (`web_app.py`): New NiceGUI web application entry point

### Core Components

- `core/device.py`: Device communication and discovery
- `core/player.py`: Scene playback engine
- `core/scenes/`: Scene type implementations (text, image, sysinfo)
- `core/project.py`: Project management

### Web UI Components

- `ui/app.py`: Main application structure and tab management
- `ui/pages/connection.py`: Device connection interface
- `ui/pages/scenes.py`: Scene management interface
- `ui/preview.py`: Scene preview generation
- `ui/theme.py`: Theme system and CSS generation

## Contributing

Feel free to fork this project and submit pull requests with improvements. Follow the guidelines in AGENTS.md for commits and PRs.
