# Pixoo Commander

A Python Qt6 application for controlling Pixoo-64 devices.

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

1. Run the application:

   ```bash
   python main.py
   ```

2. Enter your Pixoo-64 device's IP address (default is 192.168.0.103) and screen size (default is 64 for Pixoo-64)
3. Click "Connect" to establish a connection
4. Use the various controls to:
   - Send text messages
   - Display images from your computer
   - Show system information
   - Enable continuous monitoring
   - Enable screen rotation between different display modes
   - Create and display custom messages with color selection

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

## Contributing

Feel free to fork this project and submit pull requests with improvements. Follow the guidelines in AGENTS.md for commits and PRs.
