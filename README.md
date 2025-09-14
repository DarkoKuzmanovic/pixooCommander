# Pixoo Commander

Pixoo Commander is a NeutralinoJS desktop application that controls Divoom Pixoo LED display devices. It features a plugin-based widget system similar to Android widgets, allowing users to create multiple scenes with customizable display elements.

## Features

- **Plugin-based Widget System**: Extensible architecture for creating custom widgets
- **Multi-Scene Management**: Create and switch between different display layouts
- **Device Discovery**: Automatically scans and connects to Pixoo devices on your network
- **Real-time Preview**: Built-in canvas preview showing exactly what will be displayed on the device
- **Cross-platform**: Works on Windows, macOS, and Linux

## Architecture Overview

The application uses a modular plugin architecture centered around widgets:

- **Plugin System**: Loads and registers widget plugins
- **Scene Management**: Multi-scene system for different display layouts
- **Widget System**: Three-tier widget hierarchy (Widget, AnimatedWidget, DataWidget)
- **Device Communication**: HTTP API communication to Pixoo devices with automatic port detection
- **UI Management**: Single-page application with modular UI components

## Development Commands

- **Run development**: `neu run` - Starts the application in development mode
- **Build application**: `neu build` - Creates distribution binaries
- **Update client library**: `neu update` - Updates neutralino.js client library

## Author

Darko Kuzmanovic

## GitHub Repository

[Pixoo Commander on GitHub](https://github.com/DarkoKuzmanovic/pixoocommander)

## License

[MIT](LICENSE)

## Icon credits

- `trayIcon.png` - Made by [Freepik](https://www.freepik.com) and downloaded from [Flaticon](https://www.flaticon.com)
