# Pixoo Commander

This project implements a Python Qt6 application for controlling Pixoo 64 devices.

## Project Overview

The application provides a graphical interface for controlling Pixoo 64 LED displays over Wi-Fi. It allows users to:

- Send custom text messages to the device
- Display images from their computer
- Show real-time system information (CPU/RAM usage)
- Enable continuous monitoring
- Rotate between multiple display screens
- Show custom messages with color selection

## Key Features

1. **Device Discovery**: Automatically finds Pixoo devices on the local network
2. **Connection Management**: Robust connection handling with status indicators
3. **Text Display**: Send custom text messages with color formatting
4. **Image Display**: Load and display images from the computer
5. **System Monitoring**: Show real-time CPU and RAM usage with time display
6. **Continuous Updates**: Automatic periodic updates of system information
7. **Multi-Screen Rotation**: Automatically rotate between image, system monitor, and custom message screens
8. **Custom Message Display**: Create and display custom messages with color selection
9. **Manual Screen Control**: Switch between screens manually

## Technical Implementation

### Dependencies

- PySide6: Qt6 bindings for Python (GUI framework)
- pixoo: Python library for controlling Pixoo devices
- psutil: System and process utilities for gathering system information

### Architecture

The application follows a modular design with:

1. **Main Application Window**: Qt6-based GUI with organized sections
2. **Device Communication**: Uses the pixoo library for device interaction
3. **System Monitoring**: Uses psutil for gathering system metrics
4. **Screen Management**: Implements screen rotation and manual switching
5. **Color Selection**: Uses Qt's color dialog for custom message colors
6. **Error Handling**: Comprehensive error handling throughout

### File Structure

```bash
.
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── README.md           # User documentation
├── QWEN.md             # Development documentation
└── test/               # Test scripts and utilities
    ├── find_device.py
    ├── find_device_simple.py
    ├── test_device_endpoints.py
    ├── discover_pixoo.py
    ├── test_message.py
    ├── test_message_correct.py
    ├── test_message_correct2.py
    ├── check_methods.py
    ├── test_simple.py
    └── final_test.py
```

## Development Process

The application was developed using an iterative approach:

1. **Research Phase**: Investigated Pixoo device communication protocols
2. **Setup Phase**: Installed required dependencies (PySide6, pixoo, etc.)
3. **UI Development**: Created the Qt6 GUI with all necessary controls
4. **Device Integration**: Implemented device connection and communication
5. **Feature Implementation**: Added text, image, and system monitoring features
6. **Testing Phase**: Verified functionality with actual Pixoo64 device
7. **Troubleshooting**: Fixed connection issues and parameter problems
8. **Documentation**: Created comprehensive documentation
9. **Enhancement Phase**: Added multi-screen rotation and custom message features

## Key Challenges and Solutions

### Connection Issues

**Problem**: Initial connection attempts failed with "Invalid screen size" errors
**Solution**: Correctly identified that the second parameter is screen size, not port number

### Method Signatures

**Problem**: Incorrect method signatures caused errors when drawing text
**Solution**: Investigated available methods and used correct parameter order

### Network Discovery

**Problem**: Difficulty finding the device IP address on the network
**Solution**: Created multiple network scanning utilities to discover devices

### Screen Rotation

**Problem**: Need to alternate between different display modes
**Solution**: Implemented screen rotation system with configurable intervals

### Custom Messages

**Problem**: Need to display user-defined messages with custom colors
**Solution**: Integrated Qt color selection with Pixoo RGB text display

## Usage Instructions

1. Ensure your Pixoo64 device is connected to the same Wi-Fi network
2. Run the application: `python main.py`
3. Enter your device's IP address (default: 192.168.0.103)
4. Set screen size to 64 (for Pixoo64)
5. Click "Connect" to establish connection
6. Use the various controls to interact with your device:
   - Send text messages
   - Display images
   - Show system information
   - Enable continuous monitoring
   - Enable screen rotation
   - Create custom messages with color selection

## Testing

Comprehensive testing was performed with:

- Connection establishment
- Text message display
- Image display
- System information display
- Continuous monitoring
- Screen rotation
- Custom message display

All tests passed successfully with the actual Pixoo64 device.

## Future Enhancements

Potential improvements for future versions:

- Custom animations
- Notification alerts
- Music visualization
- Gaming features
- Support for multiple device types
- Advanced image processing
- Custom fonts and text effects
- Scheduling system for different displays
- Remote control via web interface
- Preset management for different display configurations
