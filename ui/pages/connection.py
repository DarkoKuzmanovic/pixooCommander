#!/usr/bin/env python3
"""
Connection page for Pixoo Commander NiceGUI web app
"""

from typing import Optional, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.device import Device, DeviceConfig, DeviceInfo
    from core.player import Player

class ConnectionPage:
    def __init__(self):
        self.device_wrapper: Optional['Device'] = None
        self.player: Optional['Player'] = None
        self.connected: bool = False
        self.selected_device: Optional['DeviceInfo'] = None
        self.discovered_devices: Dict[str, 'DeviceInfo'] = {}

        # UI element references
        self.ip_input = None
        self.port_input = None
        self.status_label = None
        self.connect_button = None
        self.scan_button = None
        self.devices_select = None
        self.log_output = None

    def create_ui(self):
        """Create the connection page UI"""
        # Import NiceGUI components here to avoid import issues
        from nicegui import ui

        with ui.column().classes('w-full gap-4'):
            ui.label('Device Connection').classes('text-2xl font-bold')

            with ui.card().classes('w-full'):
                with ui.grid(columns=2).classes('w-full gap-4'):
                    self.ip_input = ui.input(label='Device IP', placeholder='192.168.1.100').classes('w-full')
                    self.port_input = ui.number(label='Screen Size', value=64, min=1, max=65535).classes('w-full')

                    self.status_label = ui.label('Not connected').classes('text-red')

                    with ui.row().classes('w-full justify-between col-span-2'):
                        self.connect_button = ui.button('Connect', on_click=self._handle_connect)
                        self.scan_button = ui.button('Scan for Devices', on_click=self._handle_scan)

                # Device list
                self.devices_select = ui.select([], label='Discovered Devices', on_change=self._handle_device_select).classes('w-full')

                # Log output
                with ui.card().classes('w-full mt-4'):
                    ui.label('Log Output').classes('font-bold')
                    self.log_output = ui.log().classes('w-full h-32')

    async def _handle_connect(self):
        """Handle connect button click - establishes connection to the device"""
        try:
            # Get IP and port from input fields
            ip = self.ip_input.value
            screen_size = int(self.port_input.value) if self.port_input.value else 64

            if not ip:
                self.log("Error: Please enter a device IP address")
                return

            self.log(f"Connecting to device at {ip}:{screen_size}...")
            self.connect_button.disable()
            self.connect_button.text = "Connecting..."

            # Import core modules here to avoid circular imports
            from core.device import Device, DeviceConfig
            from core.player import Player

            # Create device configuration and connect
            config = DeviceConfig(ip=ip, screen_size=screen_size)
            self.device_wrapper = Device(config)
            self.device_wrapper.connect()

            # Create player instance for this device
            self.player = Player(device=self.device_wrapper)

            # Update connection state
            self.connected = True
            self.status_label.text = f"Connected to {ip}:{screen_size}"
            self.status_label.classes(replace='text-green')

            self.log(f"Successfully connected to device at {ip}:{screen_size}")
        except Exception as e:
            # Log any connection errors
            self.log(f"Connection failed: {str(e)}")
            self.status_label.text = "Connection failed"
            self.status_label.classes(replace='text-red')
        finally:
            # Reset button state
            self.connect_button.enable()
            self.connect_button.text = "Connect"

    async def _handle_scan(self):
        """Handle scan button click - discovers devices on the network"""
        try:
            self.log("Scanning for devices...")
            self.scan_button.disable()
            self.scan_button.text = "Scanning..."

            # Import core modules here to avoid circular imports
            from core.device import Device

            # Discover devices on the network
            devices = await Device.discover_devices()

            if not devices:
                self.log("No devices found")
                self.devices_select.options = {}
                self.discovered_devices = {}
                return

            # Store discovered devices and populate the devices select
            # Format: {device_id: "Device Name (IP:port)"}
            self.discovered_devices = {}
            options = {}
            for device in devices:
                device_id = device.id or device.ip
                self.discovered_devices[device_id] = device
                label = f"{device.name or 'Pixoo Device'} ({device.ip}:{device.port})"
                options[device_id] = label

            self.devices_select.options = options
            self.devices_select.update()

            self.log(f"Found {len(devices)} device(s)")
        except Exception as e:
            # Log any discovery errors
            self.log(f"Discovery failed: {str(e)}")
        finally:
            # Reset button state
            self.scan_button.enable()
            self.scan_button.text = "Scan for Devices"

    def _handle_device_select(self):
        """Handle device selection from dropdown - populates IP and port fields"""
        try:
            # Get the selected device ID
            selected_id = self.devices_select.value
            if not selected_id:
                return

            # Get the device info from our stored devices
            if selected_id in self.discovered_devices:
                device = self.discovered_devices[selected_id]

                # Update input fields
                self.ip_input.value = device.ip
                self.port_input.value = device.port

                # Store selected device info
                self.selected_device = device

                self.log(f"Selected device: {device.name or 'Pixoo Device'} ({device.ip}:{device.port})")
        except Exception as e:
            # Log any selection errors
            self.log(f"Device selection error: {str(e)}")

    def log(self, message: str):
        """Add a message to the log output"""
        if self.log_output:
            self.log_output.push(message)