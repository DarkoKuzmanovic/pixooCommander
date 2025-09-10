#!/usr/bin/env python3
"""
Pixoo Commander
A Python Qt6 application for controlling Pixoo 64 devices
"""

import sys
import traceback
import threading
import time
import datetime
from typing import Optional, Dict, Any, List, Tuple, Union
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, QTextEdit, QSpinBox, QFileDialog, QMessageBox, QTabWidget, QCheckBox, QDoubleSpinBox, QColorDialog, QComboBox, QListWidget, QListWidgetItem, QAbstractItemView
from PySide6.QtGui import QImage, QPainter, QPixmap, QColor, QFontMetrics, QShortcut, QKeySequence, QAction
from PySide6.QtCore import Qt, QTimer, QSettings, QPoint, QRect, QObject, QThread, Signal
import psutil
from pixoo import Pixoo
from core.device import Device, DeviceConfig, DeviceInfo
from core.project import Project
from core.player import Player
from core.scenes.text import TextScene
from core.scenes.image import ImageScene
from core.scenes.sysinfo import SysInfoScene
from core.ui.theme_manager import ThemeManager
from pathlib import Path


class SceneListWidget(QListWidget):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._drag_allowed: bool = False

    def mousePressEvent(self, event):
        self._drag_allowed = False
        # Determine if press is on a drag handle inside the item widget
        pos = event.position().toPoint()
        item = self.itemAt(pos)
        if item is not None:
            w = self.itemWidget(item)
            if w is not None:
                handle = w.findChild(QLabel, "dragHandle")
                if handle is not None:
                    # Map handle rect to viewport coordinates
                    top_left = handle.mapTo(self.viewport(), QPoint(0, 0))
                    rect = QRect(top_left, handle.size())
                    if rect.contains(pos):
                        self._drag_allowed = True
        super().mousePressEvent(event)

    def startDrag(self, supportedActions: Any) -> None:
        if not self._drag_allowed:
            return
        super().startDrag(supportedActions)


class DeviceDiscoveryWorker(QThread):
    """Worker thread for device discovery."""
    deviceFound = Signal(object)  # Signal to emit when a device is found
    discoveryFinished = Signal()  # Signal to emit when discovery is finished
    discoveryError = Signal(str)  # Signal to emit when an error occurs

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True

    def run(self):
        """Run the device discovery process."""
        try:
            # Import here to avoid blocking the UI thread
            from core.device import Device
            import asyncio

            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the discovery
            devices = loop.run_until_complete(Device.discover_devices())

            # Emit found devices
            for device in devices:
                if not self._is_running:
                    break
                self.deviceFound.emit(device)

            # Clean up
            loop.close()

            # Emit finished signal
            if self._is_running:
                self.discoveryFinished.emit()
        except Exception as e:
            if self._is_running:
                self.discoveryError.emit(str(e))

    def stop(self):
        """Stop the discovery process."""
        self._is_running = False

class PixooCommander(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pixoo Commander")
        self.setGeometry(100, 100, 800, 700)

        # Device connection
        self.pixoo: Optional[Pixoo] = None
        self.connected: bool = False
        self.monitoring: bool = False
        self.screen_rotation: bool = False
        self.current_screen: int = 0  # 0 = image, 1 = system info, 2 = custom message
        self.last_image_path: str = ""
        self.last_text: str = "Hello, Pixoo!"
        self.custom_message: str = "Custom Message"
        self.custom_message_color: Tuple[int, int, int] = (255, 255, 255)  # White
        # Scenes/Project
        self.project: Project = Project()
        self.device_wrapper: Optional[Device] = None
        self.player: Optional[Player] = None
        self.project_path: Optional[str] = None  # path to saved project file
        self.settings: QSettings = QSettings("PixooCommander", "Controller")
        self.dirty: bool = False
        # Discovered device
        self.selected_device: Optional[DeviceInfo] = None

        # Theme manager
        self.theme_manager: ThemeManager = ThemeManager()
        self.theme_manager.themeChanged.connect(self.on_theme_changed)

        # Timers
        self.monitoring_timer: QTimer = QTimer()
        # self.monitoring_timer.timeout.connect(self.update_system_info)
        self.rotation_timer: QTimer = QTimer()
        # self.rotation_timer.timeout.connect(self.rotate_screens)
        # Scenes playback timer
        self.scene_play_timer: QTimer = QTimer()
        self.scene_play_timer.timeout.connect(self.play_next_scene)
        # Preview refresh timer (for live SysInfo and text scroll)
        self.preview_timer: QTimer = QTimer()
        self.preview_timer.timeout.connect(self.on_preview_tick)
        self.preview_timer.start(100)
        # Scene animation timer (device-side during playback)
        self.scene_anim_timer: QTimer = QTimer()
        self.scene_anim_timer.timeout.connect(self.on_scene_anim_tick)

        # Create central widget and layout
        central_widget: QWidget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout: QVBoxLayout = QVBoxLayout(central_widget)
        self.update_window_title()

        # Create tab widget for better organization
        tab_widget: QTabWidget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Menu bar
        file_menu = self.menuBar().addMenu("&File")
        act_new: QAction = QAction("&New", self)
        act_open: QAction = QAction("&Open...", self)
        act_save: QAction = QAction("&Save", self)
        act_save_as: QAction = QAction("Save &As...", self)
        act_relink: QAction = QAction("&Relink Missing Assets", self)
        act_exit: QAction = QAction("E&xit", self)
        file_menu.addAction(act_new)
        file_menu.addAction(act_open)
        file_menu.addAction(act_save)
        file_menu.addAction(act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(act_relink)
        file_menu.addSeparator()
        file_menu.addAction(act_exit)

        # Theme menu
        theme_menu = self.menuBar().addMenu("&Theme")
        act_light: QAction = QAction("&Light", self)
        act_dark: QAction = QAction("&Dark", self)
        act_light.triggered.connect(self.switch_to_light_theme)
        act_dark.triggered.connect(self.switch_to_dark_theme)
        theme_menu.addAction(act_light)
        theme_menu.addAction(act_dark)

        # Create connection tab
        connection_tab = QWidget()
        connection_layout = QVBoxLayout(connection_tab)

        # Create connection group
        connection_group: QGroupBox = QGroupBox("Device Connection")
        connection_form: QFormLayout = QFormLayout()

        self.ip_input: QLineEdit = QLineEdit("")
        self.port_input: QSpinBox = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(64)
        self.connect_button: QPushButton = QPushButton("Connect")
        self.status_label: QLabel = QLabel("Not connected")
        self.status_label.setStyleSheet("color: red;")

        # Create scan button and device list
        self.scan_button: QPushButton = QPushButton("Scan for Devices")
        self.devices_list: QListWidget = QListWidget()
        self.devices_list.setMaximumHeight(150)

        # Connect scan button signal
        self.scan_button.clicked.connect(self.start_device_scan)
        self.devices_list.itemDoubleClicked.connect(self.select_device_from_list)

        connection_form.addRow("Device IP:", self.ip_input)
        connection_form.addRow("Screen Size:", self.port_input)
        connection_form.addRow("Status:", self.status_label)
        connection_form.addRow(self.scan_button)
        connection_form.addRow(self.devices_list)
        connection_form.addRow(self.connect_button)

        connection_group.setLayout(connection_form)
        connection_layout.addWidget(connection_group)

        # Create log output
        log_group: QGroupBox = QGroupBox("Log Output")
        log_layout: QVBoxLayout = QVBoxLayout()
        self.log_output: QTextEdit = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Add tabs
        tab_widget.addTab(connection_tab, "Connection")
        # tab_widget.addTab(controls_tab, "Controls")  # Controls tab removed

        # Create Scenes tab (basic)
        scenes_tab: QWidget = QWidget()
        scenes_layout: QVBoxLayout = QVBoxLayout(scenes_tab)

        # Scene list and actions
        scenes_actions_layout: QHBoxLayout = QHBoxLayout()
        self.add_text_scene_btn: QPushButton = QPushButton("Add Text")
        self.add_image_scene_btn: QPushButton = QPushButton("Add Image")
        self.add_sysinfo_scene_btn: QPushButton = QPushButton("Add SysInfo")
        self.delete_scene_btn: QPushButton = QPushButton("Delete")
        self.save_project_btn: QPushButton = QPushButton("Save")
        self.save_as_project_btn: QPushButton = QPushButton("Save As")
        self.open_project_btn: QPushButton = QPushButton("Open")
        self.recent_label: QLabel = QLabel("Recent:")
        self.recent_combo: QComboBox = QComboBox()
        scenes_actions_layout.addWidget(self.add_text_scene_btn)
        scenes_actions_layout.addWidget(self.add_image_scene_btn)
        scenes_actions_layout.addWidget(self.add_sysinfo_scene_btn)
        scenes_actions_layout.addWidget(self.delete_scene_btn)
        scenes_actions_layout.addStretch(1)
        scenes_actions_layout.addWidget(self.open_project_btn)
        scenes_actions_layout.addWidget(self.save_project_btn)
        scenes_actions_layout.addWidget(self.save_as_project_btn)
        scenes_actions_layout.addSpacing(12)
        scenes_actions_layout.addWidget(self.recent_label)
        scenes_actions_layout.addWidget(self.recent_combo)

        self.scenes_list: SceneListWidget = SceneListWidget()

        # Simple editors
        editor_group: QGroupBox = QGroupBox("Editor")
        editor_form: QFormLayout = QFormLayout()
        self.scene_name_input: QLineEdit = QLineEdit()
        self.scene_duration_input: QSpinBox = QSpinBox()
        self.scene_duration_input.setRange(1, 600)
        self.scene_text_input: QTextEdit = QTextEdit()
        self.scene_text_input.setMaximumHeight(100)
        self.scene_text_x_input: QSpinBox = QSpinBox()
        self.scene_text_x_input.setRange(-128, 128)
        self.scene_text_y_input: QSpinBox = QSpinBox()
        self.scene_text_y_input.setRange(-128, 128)
        # Line spacing control
        self.scene_line_spacing_input: QSpinBox = QSpinBox()
        self.scene_line_spacing_input.setRange(0, 20)
        self.scene_line_spacing_input.setValue(2)
        # Text alignment control
        self.scene_text_align_combo: QComboBox = QComboBox()
        self.scene_text_align_combo.addItem("Left", userData="left")
        self.scene_text_align_combo.addItem("Center", userData="center")
        self.scene_text_align_combo.addItem("Right", userData="right")
        self.scene_image_input: QLineEdit = QLineEdit()
        self.scene_image_browse: QPushButton = QPushButton("Browse...")
        self.scene_color_button: QPushButton = QPushButton("Pick Text Color")
        self.scene_color_button.setEnabled(False)
        self.text_scroll_checkbox: QCheckBox = QCheckBox("Scroll horizontally")
        self.text_scroll_checkbox.setEnabled(False)
        self.text_speed_spin: QSpinBox = QSpinBox()
        self.text_speed_spin.setRange(1, 200)
        self.text_speed_spin.setSuffix(" px/s")
        self.text_speed_spin.setEnabled(False)
        self.text_direction_combo: QComboBox = QComboBox()
        self.text_direction_combo.addItem("Left", userData="left")
        self.text_direction_combo.addItem("Right", userData="right")
        self.text_direction_combo.setEnabled(False)
        self.image_fit_combo: QComboBox = QComboBox()
        self.image_fit_combo.addItem("Contain", userData="contain")
        self.image_fit_combo.addItem("Cover", userData="cover")
        self.image_fit_combo.addItem("Stretch", userData="stretch")
        self.image_fit_combo.setEnabled(False)
        self.sysinfo_theme_combo: QComboBox = QComboBox()
        self.sysinfo_theme_combo.addItem("Light", userData="light")
        self.sysinfo_theme_combo.addItem("Accent", userData="accent")
        self.sysinfo_theme_combo.addItem("Mono", userData="mono")
        self.sysinfo_theme_combo.setEnabled(False)
        editor_form.addRow("Name:", self.scene_name_input)
        editor_form.addRow("Duration (s):", self.scene_duration_input)
        editor_form.addRow("Text:", self.scene_text_input)
        editor_form.addRow("Text X:", self.scene_text_x_input)
        editor_form.addRow("Text Y:", self.scene_text_y_input)
        editor_form.addRow("Line Spacing:", self.scene_line_spacing_input)
        editor_form.addRow("Text Alignment:", self.scene_text_align_combo)
        editor_form.addRow("Text Color:", self.scene_color_button)
        row_scroll: QHBoxLayout = QHBoxLayout()
        row_scroll.addWidget(self.text_scroll_checkbox)
        row_scroll.addWidget(self.text_speed_spin)
        roww2: QWidget = QWidget()
        roww2.setLayout(row_scroll)
        editor_form.addRow("Text Scroll:", roww2)
        editor_form.addRow("Scroll Direction:", self.text_direction_combo)
        editor_form.addRow("SysInfo Theme:", self.sysinfo_theme_combo)
        editor_form.addRow("Image Fit:", self.image_fit_combo)
        row: QHBoxLayout = QHBoxLayout()
        row.addWidget(self.scene_image_input)
        row.addWidget(self.scene_image_browse)
        roww: QWidget = QWidget()
        roww.setLayout(row)
        editor_form.addRow("Image Path:", roww)
        editor_group.setLayout(editor_form)

        # Playback controls
        playback_layout: QHBoxLayout = QHBoxLayout()
        self.scenes_play_btn: QPushButton = QPushButton("Play")
        self.scenes_pause_btn: QPushButton = QPushButton("Pause")
        self.scenes_prev_btn: QPushButton = QPushButton("Prev")
        self.scenes_next_btn: QPushButton = QPushButton("Next")
        playback_layout.addWidget(self.scenes_play_btn)
        playback_layout.addWidget(self.scenes_pause_btn)
        playback_layout.addWidget(self.scenes_prev_btn)
        playback_layout.addWidget(self.scenes_next_btn)

        # Arrange list+editor+preview vertically for simplicity
        scenes_layout.addLayout(scenes_actions_layout)
        scenes_layout.addWidget(self.scenes_list)
        scenes_layout.addWidget(editor_group)

        # Preview pane
        preview_group: QGroupBox = QGroupBox("Preview (64x64)")
        preview_layout: QVBoxLayout = QVBoxLayout()
        self.preview_label: QLabel = QLabel()
        self.preview_label.setFixedSize(256, 256)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)

        scenes_layout.addWidget(preview_group)
        scenes_layout.addLayout(playback_layout)

        tab_widget.addTab(scenes_tab, "Scenes")

        # Connect signals
        self.connect_button.clicked.connect(self.connect_to_device)

        # Scenes signals
        self.add_text_scene_btn.clicked.connect(self.add_text_scene)
        self.add_image_scene_btn.clicked.connect(self.add_image_scene)
        self.add_sysinfo_scene_btn.clicked.connect(self.add_sysinfo_scene)
        self.delete_scene_btn.clicked.connect(self.delete_selected_scene)
        self.scenes_list.currentRowChanged.connect(self.on_scene_selected)
        self.scene_name_input.textChanged.connect(self.on_scene_name_changed)
        self.scene_duration_input.valueChanged.connect(self.on_scene_duration_changed)
        self.scene_text_input.textChanged.connect(self.on_scene_text_changed)
        self.scene_line_spacing_input.valueChanged.connect(self.on_scene_line_spacing_changed)
        self.scene_text_align_combo.currentIndexChanged.connect(self.on_scene_text_align_changed)
        self.scene_image_browse.clicked.connect(self.browse_scene_image)
        self.scene_image_input.textChanged.connect(self.on_scene_image_changed)
        self.scene_color_button.clicked.connect(self.pick_scene_text_color)
        self.scenes_play_btn.clicked.connect(self.play_scenes)
        self.scenes_pause_btn.clicked.connect(self.pause_scenes)
        self.scenes_prev_btn.clicked.connect(self.prev_scene)
        self.scenes_next_btn.clicked.connect(self.next_scene)
        self.save_project_btn.clicked.connect(self.save_project)
        self.open_project_btn.clicked.connect(self.open_project)
        act_new.triggered.connect(self.new_project)
        act_open.triggered.connect(self.open_project)
        act_save.triggered.connect(self.save_project)
        act_save_as.triggered.connect(self.save_project_as)
        act_relink.triggered.connect(self.relink_missing_assets)
        act_exit.triggered.connect(self.close)
        self.scene_text_x_input.valueChanged.connect(self.on_scene_text_x_changed)
        self.scene_text_y_input.valueChanged.connect(self.on_scene_text_y_changed)
        self.save_as_project_btn.clicked.connect(self.save_project_as)
        self.recent_combo.activated.connect(self.open_recent_selected)
        self.sysinfo_theme_combo.currentIndexChanged.connect(self.on_sysinfo_theme_changed)
        self.text_scroll_checkbox.toggled.connect(self.on_text_scroll_toggled)
        self.text_speed_spin.valueChanged.connect(self.on_text_speed_changed)
        self.text_direction_combo.currentIndexChanged.connect(self.on_text_direction_changed)
        self.image_fit_combo.currentIndexChanged.connect(self.on_image_fit_changed)

        # Drag-and-drop reordering for scenes list
        self.scenes_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)  # type: ignore
        self.scenes_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)  # type: ignore
        self.scenes_list.setDefaultDropAction(Qt.DropAction.MoveAction)  # type: ignore
        self.scenes_list.setDragEnabled(True)
        self.scenes_list.setAcceptDrops(True)
        try:
            self.scenes_list.model().rowsMoved.connect(self.on_scenes_rows_moved)
        except Exception:
            pass

        # Keyboard shortcuts
        self.shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        self.shortcut_delete.activated.connect(self.delete_selected_scene)
        self.shortcut_play = QShortcut(QKeySequence("Return"), self)
        self.shortcut_play.activated.connect(self.play_scenes)
        self.shortcut_play2 = QShortcut(QKeySequence("Enter"), self)
        self.shortcut_play2.activated.connect(self.play_scenes)
        self.shortcut_toggle = QShortcut(QKeySequence("Space"), self)
        self.shortcut_toggle.activated.connect(self.toggle_play_pause)
        self.shortcut_move_up = QShortcut(QKeySequence("Alt+Up"), self)
        self.shortcut_move_up.activated.connect(lambda: self.move_selected_scene(-1))
        self.shortcut_move_down = QShortcut(QKeySequence("Alt+Down"), self)
        self.shortcut_move_down.activated.connect(lambda: self.move_selected_scene(1))

        # Load recent projects list
        self.load_recent_projects()

        # Apply theme
        preferred_theme = self.theme_manager.load_preference()
        self.theme_manager.switch_theme(preferred_theme)

    def connect_to_device(self):
        """Connect to the Pixoo device"""
        if self.connected:
            # Disconnect if already connected
            self.pixoo = None
            self.connected = False
            self.connect_button.setText("Connect")
            self.status_label.setText("Not connected")
            self.status_label.setStyleSheet("color: red;")
            self.log_output.append("Disconnected from device")
            return

        # Determine connection parameters
        if self.selected_device:
            # Use selected discovered device
            ip = self.selected_device.ip
            port = self.selected_device.port
            self.log_output.append(f"Connecting to discovered device {ip}:{port}...")
        else:
            # Fall back to manual IP input
            ip = self.ip_input.text()
            port = self.port_input.value()
            self.log_output.append(f"Connecting to manually entered device {ip}:{port}...")

        self.status_label.setText("Connecting...")
        self.status_label.setStyleSheet("color: orange;")

        try:
            # Try to connect to the device
            screen_size = port  # Port input is actually the screen size
            self.pixoo = Pixoo(ip, screen_size)
            # Test connection by getting device time
            device_time = self.pixoo.get_device_time()
            # Also initialize core Device wrapper
            try:
                if self.selected_device:
                    # Use DeviceConfig from selected DeviceInfo
                    device_config = DeviceConfig(ip=self.selected_device.ip, screen_size=self.selected_device.port)
                else:
                    # Use manual input
                    device_config = DeviceConfig(ip=ip, screen_size=screen_size)
                self.device_wrapper = Device(device_config)
                self.device_wrapper.connect()
                self.player = Player(self.device_wrapper)
            except Exception as de:
                self.log_output.append(f"Device wrapper init failed (non-fatal): {de}")
            self.connected = True
            self.connect_button.setText("Disconnect")
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green;")
            self.log_output.append(f"Successfully connected to device. Time: {device_time}")
        except Exception as e:
            self.log_output.append(f"Connection failed: {str(e)}")
            self.status_label.setText("Connection failed")
            self.status_label.setStyleSheet("color: red;")
            self.pixoo = None
            self.connected = False

    def start_device_scan(self):
        """Start the device discovery process."""
        # Disable the scan button to prevent multiple scans
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        self.devices_list.clear()
        self.selected_device = None  # Clear previously selected device
        self.log_output.append("Starting device scan...")

        # Create and start the discovery worker
        self.discovery_worker = DeviceDiscoveryWorker()
        self.discovery_worker.deviceFound.connect(self.on_device_found)
        self.discovery_worker.discoveryFinished.connect(self.on_discovery_finished)
        self.discovery_worker.discoveryError.connect(self.on_discovery_error)
        self.discovery_worker.start()

    def on_device_found(self, device_info):
        """Handle when a device is found during discovery."""
        # Add device to the list
        item_text = f"{device_info.name or 'Pixoo Device'} ({device_info.ip}:{device_info.port})"
        if device_info.model:
            item_text += f" - {device_info.model}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, device_info)
        self.devices_list.addItem(item)
        self.log_output.append(f"Found device: {item_text}")

        # Automatically select the first device found
        if self.devices_list.count() == 1:
            self.devices_list.setCurrentItem(item)
            self.selected_device = device_info
            self.ip_input.setText(device_info.ip)
            self.port_input.setValue(device_info.port)
            self.log_output.append(f"Automatically selected device: {device_info.ip}:{device_info.port}")

    def on_discovery_finished(self):
        """Handle when the discovery process is finished."""
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Scan for Devices")
        self.log_output.append("Device scan completed.")
        if self.devices_list.count() == 0:
            self.log_output.append("No devices found. Please check your network or enter IP manually.")
            self.selected_device = None
        else:
            self.log_output.append(f"Found {self.devices_list.count()} device(s). First device automatically selected.")

    def on_discovery_error(self, error_message):
        """Handle when an error occurs during discovery."""
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Scan for Devices")
        self.log_output.append(f"Device scan error: {error_message}")

    def select_device_from_list(self, item):
        """Select a device from the list and fill the IP input."""
        device_info = item.data(Qt.ItemDataRole.UserRole)
        if device_info:
            self.selected_device = device_info
            self.ip_input.setText(device_info.ip)
            self.port_input.setValue(device_info.port)
            self.log_output.append(f"Selected device: {device_info.ip}:{device_info.port}")

    # ===== Scenes Editor (basic) =====
    def refresh_scenes_list(self):
        current = self.scenes_list.currentRow()
        self.scenes_list.clear()
        for s in self.project.scenes:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, s.id)  # type: ignore
            widget = self.create_scene_item_widget(s)
            item.setSizeHint(widget.sizeHint())
            self.scenes_list.addItem(item)
            self.scenes_list.setItemWidget(item, widget)
        if 0 <= current < self.scenes_list.count():
            self.scenes_list.setCurrentRow(current)

    def add_text_scene(self):
        scene = TextScene(name="Text", duration_s=8, config={
            "text_options": {
                "align": "left",
                "line_spacing": 2,
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Hello", "y": 0}
            ],
            "scroll": False,
            "speed": 20,
            "direction": "left"
        })
        self.project.scenes.append(scene)
        self.refresh_scenes_list()
        self.scenes_list.setCurrentRow(len(self.project.scenes) - 1)
        self.update_preview()
        self.mark_dirty()

    def add_image_scene(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        scene = ImageScene(name="Image", duration_s=10, config={"path": path, "fit": "contain"})
        self.project.scenes.append(scene)
        self.refresh_scenes_list()
        self.scenes_list.setCurrentRow(len(self.project.scenes) - 1)
        self.update_preview()
        self.mark_dirty()

    def add_sysinfo_scene(self):
        scene = SysInfoScene(name="System Info", duration_s=8, config={})
        self.project.scenes.append(scene)
        self.refresh_scenes_list()
        self.scenes_list.setCurrentRow(len(self.project.scenes) - 1)
        self.update_preview()

    def delete_selected_scene(self):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes):
            del self.project.scenes[idx]
            self.refresh_scenes_list()
            self.on_scene_selected(self.scenes_list.currentRow())
            self.update_preview()

    def on_scene_selected(self, idx: int):
        if not (0 <= idx < len(self.project.scenes)):
            self.scene_name_input.setText("")
            self.scene_duration_input.setValue(8)
            self.scene_text_input.setText("")
            self.scene_image_input.setText("")
            return
        s = self.project.scenes[idx]
        # Avoid triggering name-change recursion when selecting
        self.scene_name_input.blockSignals(True)
        self.scene_name_input.setText(s.name)
        self.scene_name_input.blockSignals(False)
        self.scene_duration_input.blockSignals(True)
        self.scene_duration_input.setValue(s.duration_s)
        self.scene_duration_input.blockSignals(False)
        # Toggle editor fields depending on type
        if s.type.value == "text":
            self.scene_text_input.setEnabled(True)
            self.scene_text_x_input.setEnabled(True)
            self.scene_text_y_input.setEnabled(True)
            self.scene_image_input.setEnabled(False)
            self.scene_image_browse.setEnabled(False)

            # Handle both legacy and new multi-line formats
            if "lines" in s.config:
                # New multi-line format
                lines = s.config.get("lines", [])
                text_lines = [line.get("text", "") for line in lines]
                text = "\n".join(text_lines)
                self.scene_text_input.setPlainText(text)

                # Set text options
                text_options = s.config.get("text_options", {})
                self.scene_line_spacing_input.setValue(int(text_options.get("line_spacing", 2)))
                align = text_options.get("align", "left")
                align_index = max(0, self.scene_text_align_combo.findData(align))
                self.scene_text_align_combo.blockSignals(True)
                self.scene_text_align_combo.setCurrentIndex(align_index)
                self.scene_text_align_combo.blockSignals(False)

                # Set color from text_options
                color = text_options.get("color", (255, 255, 255))
                self.apply_color_button_style(color)
            else:
                # Legacy single-line format
                self.scene_text_input.setPlainText(s.config.get("text", ""))
                self.scene_text_x_input.setValue(int(s.config.get("x", 0)))
                self.scene_text_y_input.setValue(int(s.config.get("y", 0)))
                self.scene_line_spacing_input.setValue(2)
                self.scene_text_align_combo.blockSignals(True)
                self.scene_text_align_combo.setCurrentIndex(0)  # Left align
                self.scene_text_align_combo.blockSignals(False)
                color = s.config.get("color", (255, 255, 255))
                self.apply_color_button_style(color)

            self.scene_color_button.setEnabled(True)
            self.sysinfo_theme_combo.setEnabled(False)
            self.text_scroll_checkbox.setEnabled(True)
            self.text_speed_spin.setEnabled(True)
            self.text_scroll_checkbox.blockSignals(True)
            self.text_scroll_checkbox.setChecked(bool(s.config.get("scroll", False)))
            self.text_scroll_checkbox.blockSignals(False)
            self.text_speed_spin.blockSignals(True)
            self.text_speed_spin.setValue(int(s.config.get("speed", 20)))
            self.text_speed_spin.blockSignals(False)
            self.text_direction_combo.setEnabled(True)
            dirv = s.config.get("direction", "left")
            self.text_direction_combo.blockSignals(True)
            self.text_direction_combo.setCurrentIndex(max(0, self.text_direction_combo.findData(dirv)))
            self.text_direction_combo.blockSignals(False)
            self.image_fit_combo.setEnabled(False)
        elif s.type.value == "image":
            self.scene_text_input.setEnabled(False)
            self.scene_text_x_input.setEnabled(False)
            self.scene_text_y_input.setEnabled(False)
            self.scene_image_input.setEnabled(True)
            self.scene_image_browse.setEnabled(True)
            img_path = s.config.get("path", "")
            self.scene_image_input.setText(img_path)
            self.scene_color_button.setEnabled(False)
            self.sysinfo_theme_combo.setEnabled(False)
            self.text_scroll_checkbox.setEnabled(False)
            self.text_speed_spin.setEnabled(False)
            self.text_direction_combo.setEnabled(False)
            self.image_fit_combo.setEnabled(True)
            fitv = s.config.get("fit", "contain")
            self.image_fit_combo.blockSignals(True)
            self.image_fit_combo.setCurrentIndex(max(0, self.image_fit_combo.findData(fitv)))
            self.image_fit_combo.blockSignals(False)
            # Highlight missing file
            try:
                from pathlib import Path as _P
                if img_path and not _P(img_path).exists():
                    self.scene_image_input.setStyleSheet("background-color: #521; color: #fff;")
                    self.log_output.append(f"Image missing: {img_path}")
                else:
                    self.scene_image_input.setStyleSheet("")
            except Exception:
                pass
        else:  # sysinfo
            self.scene_text_input.setEnabled(False)
            self.scene_text_x_input.setEnabled(False)
            self.scene_text_y_input.setEnabled(False)
            self.scene_image_input.setEnabled(False)
            self.scene_image_browse.setEnabled(False)
            self.scene_text_input.setText("")
            self.scene_image_input.setText("")
            self.scene_color_button.setEnabled(False)
            self.sysinfo_theme_combo.setEnabled(True)
            theme = s.config.get("theme", "light")
            idx = max(0, self.sysinfo_theme_combo.findData(theme))
            self.sysinfo_theme_combo.blockSignals(True)
            self.sysinfo_theme_combo.setCurrentIndex(idx)
            self.sysinfo_theme_combo.blockSignals(False)
            self.text_scroll_checkbox.setEnabled(False)
            self.text_speed_spin.setEnabled(False)
            self.text_direction_combo.setEnabled(False)
            self.image_fit_combo.setEnabled(False)
        self.update_preview()

    def on_scene_name_changed(self, text: str):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes):
            self.project.scenes[idx].name = text
            self.update_scene_item_title(idx)
            self.update_preview()

    def on_scene_duration_changed(self, val: int):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes):
            self.project.scenes[idx].duration_s = int(val)
            # update inline spinbox too
            item = self.scenes_list.item(idx)
            w = self.scenes_list.itemWidget(item)
            if w:
                spin = w.findChild(QSpinBox, "durationSpin")
                if spin and spin.value() != val:
                    spin.blockSignals(True)
                    spin.setValue(int(val))
                    spin.blockSignals(False)
            # no full refresh to avoid recursion
            # duration does not affect preview

    def on_scene_text_changed(self):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            scene = self.project.scenes[idx]
            # Get text from QTextEdit (multi-line)
            text = self.scene_text_input.toPlainText()

            # Handle both legacy and new multi-line formats
            if "lines" in scene.config:
                # New multi-line format
                lines = text.split('\n')
                scene_lines = []
                line_spacing = int(self.scene_line_spacing_input.value())

                # Preserve existing line configurations where possible
                existing_lines = scene.config.get("lines", [])

                for i, line_text in enumerate(lines):
                    line_config = {"text": line_text}
                    # Use existing Y position if available, otherwise calculate
                    if i < len(existing_lines) and "y" in existing_lines[i]:
                        line_config["y"] = existing_lines[i]["y"]
                    else:
                        line_config["y"] = int(i * (12 + line_spacing))  # type: ignore  # 12 is default line height
                    scene_lines.append(line_config)

                scene.config["lines"] = scene_lines

                # Update text_options
                if "text_options" not in scene.config:
                    scene.config["text_options"] = {}
                scene.config["text_options"]["line_spacing"] = line_spacing
                scene.config["text_options"]["align"] = self.scene_text_align_combo.currentData() or "left"
            else:
                # Legacy single-line format
                scene.config["text"] = text

            self.update_preview()
            self.mark_dirty()

    def on_scene_line_spacing_changed(self, val: int):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            scene = self.project.scenes[idx]
            # Handle both legacy and new multi-line formats
            if "lines" in scene.config:
                # New multi-line format - update text_options
                if "text_options" not in scene.config:
                    scene.config["text_options"] = {}
                scene.config["text_options"]["line_spacing"] = int(val)

                # Update line positions based on new spacing
                lines = scene.config.get("lines", [])
                for i, line_config in enumerate(lines):
                    line_config["y"] = int(i * (12 + int(val)))  # type: ignore
                scene.config["lines"] = lines
            # For legacy format, we don't need to do anything special
            self.update_preview()
            self.mark_dirty()

    def on_scene_text_align_changed(self):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            scene = self.project.scenes[idx]
            # Handle both legacy and new multi-line formats
            if "lines" in scene.config:
                # New multi-line format - update text_options
                if "text_options" not in scene.config:
                    scene.config["text_options"] = {}
                scene.config["text_options"]["align"] = self.scene_text_align_combo.currentData() or "left"
            # For legacy format, we don't need to do anything special
            self.update_preview()
            self.mark_dirty()

    def browse_scene_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.scene_image_input.setText(path)

    def on_scene_image_changed(self, text: str):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "image":
            self.project.scenes[idx].config["path"] = text
            self.update_preview()
            try:
                from pathlib import Path as _P
                if text and not _P(text).exists():
                    self.scene_image_input.setStyleSheet("background-color: #521; color: #fff;")
                else:
                    self.scene_image_input.setStyleSheet("")
            except Exception:
                pass
            self.mark_dirty()

    def on_text_direction_changed(self):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            self.project.scenes[idx].config["direction"] = self.text_direction_combo.currentData() or "left"
            self.update_preview()
            self.mark_dirty()

    def on_image_fit_changed(self):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "image":
            self.project.scenes[idx].config["fit"] = self.image_fit_combo.currentData() or "contain"
            self.update_preview()
            self.mark_dirty()

    def on_text_scroll_toggled(self, checked: bool):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            self.project.scenes[idx].config["scroll"] = bool(checked)
            # Reset X when enabling scroll to start from right edge
            if checked and int(self.project.scenes[idx].config.get("x", 0)) <= -64:
                self.project.scenes[idx].config["x"] = 64
            self.update_preview()

    def on_text_speed_changed(self, val: int):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            self.project.scenes[idx].config["speed"] = int(val)
            self.mark_dirty()

    def on_scene_text_x_changed(self, val: int):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            self.project.scenes[idx].config["x"] = int(val)
            self.update_preview()
            self.mark_dirty()

    def on_scene_text_y_changed(self, val: int):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "text":
            self.project.scenes[idx].config["y"] = int(val)
            self.update_preview()
            self.mark_dirty()

    def pick_scene_text_color(self):
        idx = self.scenes_list.currentRow()
        if not (0 <= idx < len(self.project.scenes)):
            return
        s = self.project.scenes[idx]
        if s.type.value != "text":
            return
        current = s.config.get("color", (255, 255, 255))
        color = QColorDialog.getColor(QColor(int(current[0]), int(current[1]), int(current[2])), self, "Select Text Color")
        if color.isValid():
            s.config["color"] = (color.red(), color.green(), color.blue())
            self.apply_color_button_style(s.config["color"])
            self.update_preview()
            self.mark_dirty()

    def apply_color_button_style(self, rgb):
        try:
            r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        except Exception:
            r, g, b = 255, 255, 255
        self.scene_color_button.setStyleSheet(f"background-color: rgb({r},{g},{b}); color: black;")

    def on_sysinfo_theme_changed(self):
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes) and self.project.scenes[idx].type.value == "sysinfo":
            theme = self.sysinfo_theme_combo.currentData() or "light"
            self.project.scenes[idx].config["theme"] = theme
            self.update_preview()
            self.mark_dirty()

    # --- Drag-and-drop helpers ---
    def on_scenes_rows_moved(self, *args, **kwargs):
        # Sync underlying project.scenes to match visual order
        self.sync_scenes_order_from_list()
        self.refresh_scenes_list()

    def sync_scenes_order_from_list(self):
        id_to_scene = {s.id: s for s in self.project.scenes}
        new_order = []
        for i in range(self.scenes_list.count()):
            item = self.scenes_list.item(i)
            sid = item.data(Qt.ItemDataRole.UserRole)  # type: ignore
            if sid in id_to_scene:
                new_order.append(id_to_scene[sid])
        if len(new_order) == len(self.project.scenes):
            self.project.scenes = new_order

    def move_selected_scene(self, delta: int):
        idx = self.scenes_list.currentRow()
        if idx < 0:
            return
        new_idx = idx + int(delta)
        if new_idx < 0 or new_idx >= len(self.project.scenes):
            return
        self.project.scenes[idx], self.project.scenes[new_idx] = self.project.scenes[new_idx], self.project.scenes[idx]
        self.refresh_scenes_list()
        self.scenes_list.setCurrentRow(new_idx)
        self.mark_dirty()

    def create_scene_item_widget(self, scene):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 2, 6, 2)
        # Drag handle visual
        handle = QLabel("≡")
        handle.setObjectName("dragHandle")
        handle.setToolTip("Drag to reorder")
        handle.setFixedWidth(16)
        handle.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore
        handle.setCursor(Qt.CursorShape.OpenHandCursor)  # type: ignore
        font = handle.font()
        font.setPointSize(max(10, font.pointSize()))
        handle.setFont(font)
        layout.addWidget(handle)

        title = QLabel(f"{scene.name} ({scene.type.value})")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addStretch(1)
        dur_label = QLabel("Duration:")
        layout.addWidget(dur_label)
        spin = QSpinBox()
        spin.setObjectName("durationSpin")
        spin.setRange(1, 600)
        spin.setSuffix(" s")
        spin.setValue(int(scene.duration_s))
        spin.setProperty("scene_id", scene.id)
        spin.valueChanged.connect(self.on_inline_duration_changed)
        layout.addWidget(spin)
        return container

    def update_scene_item_title(self, idx: int):
        if not (0 <= idx < self.scenes_list.count()):
            return
        item = self.scenes_list.item(idx)
        w = self.scenes_list.itemWidget(item)
        if not w:
            return
        lbl = w.findChild(QLabel, "titleLabel")
        if not lbl:
            return
        s = self.project.scenes[idx]
        lbl.setText(f"{s.name} ({s.type.value})")

    def on_inline_duration_changed(self, val: int):
        spin = self.sender()
        try:
            sid = spin.property("scene_id")
        except Exception:
            sid = None
        if not sid:
            return
        for i, s in enumerate(self.project.scenes):
            if s.id == sid:
                s.duration_s = int(val)
                # sync editor spin if current selection matches
                if i == self.scenes_list.currentRow():
                    if self.scene_duration_input.value() != int(val):
                        self.scene_duration_input.blockSignals(True)
                        self.scene_duration_input.setValue(int(val))
                        self.scene_duration_input.blockSignals(False)
                break

    def ensure_player_ready(self) -> bool:
        if not self.connected or self.device_wrapper is None:
            self.log_output.append("Error: Connect to device before playing scenes")
            return False
        if self.player is None:
            self.player = Player(self.device_wrapper)
        self.player.set_scenes(self.project.scenes)
        return True

    def play_scenes(self):
        if not self.ensure_player_ready() or self.player is None:
            return
        # Set current index from selection
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes):
            self.player.index = idx
        # Render first and start timer
        try:
            self.player.render_current()
        except Exception as e:
            self.log_output.append(f"Failed to render scene: {e}")
            return
        current_scene = self.player.current()
        dur = max(1, current_scene.duration_s if current_scene else 5)
        self.scene_play_timer.start(int(dur * 1000))
        self.log_output.append("Scenes playback started")
        # Start animation if needed
        self.update_scene_animation_timer()

    def pause_scenes(self):
        self.scene_play_timer.stop()
        self.log_output.append("Scenes playback paused")
        try:
            self.scene_anim_timer.stop()
        except Exception:
            pass
        self.scene_anim_timer.stop()

    def play_next_scene(self):
        if not self.player or not self.project.scenes:
            return
        self.player.next()
        try:
            self.player.render_current()
        except Exception as e:
            self.log_output.append(f"Failed to render scene: {e}")
            return
        current_scene = self.player.current()
        dur = max(1, current_scene.duration_s if current_scene else 5)
        self.scene_play_timer.start(int(dur * 1000))
        self.update_scene_animation_timer()

    def next_scene(self):
        if not self.player:
            if not self.ensure_player_ready():
                return
        if self.player is None:
            return
        self.player.next()
        self.on_scene_selected(self.player.index)
        self.refresh_scenes_list()
        self.scenes_list.setCurrentRow(self.player.index)
        self.play_scenes()

    def prev_scene(self):
        if not self.player:
            if not self.ensure_player_ready():
                return
        if self.player is None:
            return
        self.player.previous()
        self.on_scene_selected(self.player.index)
        self.refresh_scenes_list()
        self.scenes_list.setCurrentRow(self.player.index)
        self.play_scenes()

    def update_scene_animation_timer(self):
        if not self.player:
            self.scene_anim_timer.stop()
            return
        scene = self.player.current()
        if scene and scene.type.value == "text" and bool(scene.config.get("scroll", False)):
            self.scene_anim_timer.start(100)
        else:
            self.scene_anim_timer.stop()

    def on_scene_anim_tick(self):
        if not self.player:
            return
        scene = self.player.current()
        if not scene or scene.type.value != "text" or not bool(scene.config.get("scroll", False)):
            return
        speed = int(scene.config.get("speed", 20))
        step = max(1, speed // 10)
        direction = scene.config.get("direction", "left")
        x = int(scene.config.get("x", 0))
        if direction == "right":
            x += step
            if x > 64:
                x = -64
        else:
            x -= step
            if x < -64:
                x = 64
        scene.config["x"] = x
        try:
            self.player.render_current()
        except Exception as e:
            self.log_output.append(f"Animation render failed: {e}")

    # --- Preview helpers ---
    def update_preview(self):
        idx = self.scenes_list.currentRow()
        if not (0 <= idx < len(self.project.scenes)):
            self.preview_label.clear()
            return
        scene = self.project.scenes[idx]
        img = self.build_preview_image(scene)
        pix = QPixmap.fromImage(img).scaled(self.preview_label.width(), self.preview_label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)  # type: ignore
        self.preview_label.setPixmap(pix)

    def build_preview_image(self, scene, size: int = 64) -> QImage:
        img = QImage(size, size, QImage.Format.Format_RGB88)  # type: ignore
        img.fill(QColor(0, 0, 0))
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)  # type: ignore
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        try:
            stype = scene.type.value
            if stype == "text":
                # Handle both legacy and new multi-line formats
                if "lines" in scene.config:
                    # New multi-line format
                    text_options = scene.config.get("text_options", {})
                    r, g, b = text_options.get("color", (255, 255, 255))
                    painter.setPen(QColor(int(r), int(g), int(b)))
                    lines = scene.config.get("lines", [])
                    for line_config in lines:
                        line_text = line_config.get("text", "")
                        x = int(line_config.get("x", 0)) if "x" in line_config else 0
                        y = int(line_config.get("y", 0))
                        painter.drawText(x, y + 10, line_text)
                else:
                    # Legacy single-line format
                    text = scene.config.get("text", "")
                    r, g, b = scene.config.get("color", (255, 255, 255))
                    painter.setPen(QColor(int(r), int(g), int(b)))
                    x = int(scene.config.get("x", 0))
                    y = int(scene.config.get("y", 0))
                    painter.drawText(x, y + 10, text)
            elif stype == "image":
                path = scene.config.get("path")
                if path:
                    qimg = QImage(path)
                    if not qimg.isNull():
                        fit = scene.config.get("fit", "contain")
                        if fit == "cover":
                            pix = QPixmap.fromImage(qimg).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)  # type: ignore
                        elif fit == "stretch":
                            pix = QPixmap.fromImage(qimg).scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)  # type: ignore
                        else:  # contain
                            pix = QPixmap.fromImage(qimg).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) # type: ignore
                        x = (size - pix.width()) // 2
                        y = (size - pix.height()) // 2
                        painter.drawPixmap(x, y, pix)
                    else:
                        painter.drawText(2, size // 2, "Image load failed")
                else:
                    painter.drawText(2, size // 2, "No image")
            else:  # sysinfo
                try:
                    cpu = psutil.cpu_percent(interval=0) if psutil else 0.0
                    mem = psutil.virtual_memory().percent if psutil else 0.0
                    theme = scene.config.get("theme", "light")
                    if theme == "accent":
                        painter.setPen(QColor(255, 255, 0))
                        painter.drawText(0, 10, f"CPU: {cpu:.1f}%")
                        painter.setPen(QColor(0, 255, 255))
                        painter.drawText(0, 22, f"RAM: {mem:.1f}%")
                    elif theme == "mono":
                        painter.setPen(QColor(220, 220, 220))
                        painter.drawText(0, 10, f"CPU: {cpu:.1f}%")
                        painter.drawText(0, 22, f"RAM: {mem:.1f}%")
                    else:
                        painter.setPen(QColor(255, 255, 255))
                        painter.drawText(0, 10, f"CPU: {cpu:.1f}%")
                        painter.drawText(0, 22, f"RAM: {mem:.1f}%")
                except Exception:
                    painter.drawText(0, 10, "SysInfo")
        finally:
            painter.end()
        return img

    def on_preview_tick(self):
        # Update preview periodically for live SysInfo and Text scroll
        idx = self.scenes_list.currentRow()
        if 0 <= idx < len(self.project.scenes):
            s = self.project.scenes[idx]
            updated = False
            if s.type.value == "sysinfo":
                updated = True
            elif s.type.value == "text" and bool(s.config.get("scroll", False)):
                speed = int(s.config.get("speed", 20))
                step = max(1, speed // 10)  # 100ms tick
                direction = s.config.get("direction", "left")

                # Handle both legacy and new multi-line formats
                if "lines" in s.config:
                    # New multi-line format - scroll all lines together
                    lines = s.config.get("lines", [])
                    if lines:
                        # Use the first line for scrolling calculations
                        first_line = lines[0]
                        text = first_line.get("text", "")
                        x = int(first_line.get("x", 0)) if "x" in first_line else 0

                        # Compute text width for wrapping
                        font = QFont()
                        font.setPointSize(8)
                        fm = QFontMetrics(font)
                        w = fm.horizontalAdvance(text) or 0

                        if direction == "right":
                            x += step
                            if x > 64:
                                x = -w
                        else:  # left
                            x -= step
                            if x < -w:
                                x = 64

                        # Update x position for all lines
                        for line_config in lines:
                            line_config["x"] = x

                        updated = True
                else:
                    # Legacy single-line format
                    # Compute text width for wrapping
                    font = QFont()
                    font.setPointSize(8)
                    fm = QFontMetrics(font)
                    text = s.config.get("text", "")
                    w = fm.horizontalAdvance(text) or 0
                    x = int(s.config.get("x", 0))
                    if direction == "right":
                        x += step
                        if x > 64:
                            x = -w
                    else:  # left
                        x -= step
                        if x < -w:
                            x = 64
                    s.config["x"] = x
                    updated = True
            if updated:
                self.update_preview()

    # --- Project save/load ---
    def save_project(self):
        try:
            if not self.project_path:
                path, _ = QFileDialog.getSaveFileName(self, "Save Project", "projects/project.json", "Project Files (*.json)")
                if not path:
                    return
                self.project_path = path
            self.project.save(Path(self.project_path))
            self.log_output.append(f"Project saved: {self.project_path}")
            self.update_recent_projects(self.project_path)
            self.dirty = False
            self.update_window_title()
        except Exception as e:
            self.log_output.append(f"Failed to save project: {e}")

    def open_project(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Open Project", "projects", "Project Files (*.json)")
            if not path:
                return
            proj = Project.load(Path(path))
            self.project = proj
            self.project_path = path
            self.refresh_scenes_list()
            if self.project.scenes:
                self.scenes_list.setCurrentRow(0)
                self.on_scene_selected(0)
            self.update_preview()
            self.log_output.append(f"Project loaded: {path}")
            self.update_recent_projects(path)
            self.dirty = False
            self.update_window_title()
        except Exception as e:
            self.log_output.append(f"Failed to load project: {e}")

    def save_project_as(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save Project As", self.project_path or "projects/project.json", "Project Files (*.json)")
            if not path:
                return
            self.project_path = path
            self.project.save(Path(self.project_path))
            self.log_output.append(f"Project saved: {self.project_path}")
            self.update_recent_projects(self.project_path)
            self.dirty = False
            self.update_window_title()
        except Exception as e:
            self.log_output.append(f"Failed to save project: {e}")

    def new_project(self):
        if self.dirty and not self.confirm_discard_changes():
            return
        self.project = Project()
        self.project_path = None
        self.refresh_scenes_list()
        self.preview_label.clear()
        self.log_output.append("New project created")
        self.dirty = False
        self.update_window_title()

    def confirm_discard_changes(self) -> bool:
        # Minimal: no dirty tracking; always ask
        ret = QMessageBox.question(self, "Discard Changes?", "Discard current project changes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)  # type: ignore
        return ret == QMessageBox.StandardButton.Yes  # type: ignore

    def relink_missing_assets(self):
        from pathlib import Path as _P
        any_missing = False
        for i, s in enumerate(self.project.scenes):
            if getattr(s, 'type', None) and s.type.value == 'image':
                p = s.config.get('path')
                if not p or _P(p).exists():
                    continue
                any_missing = True
                newp, _ = QFileDialog.getOpenFileName(self, f"Relink image for '{s.name}'", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
                if newp:
                    s.config['path'] = newp
                    if self.scenes_list.currentRow() == i:
                        self.scene_image_input.setText(newp)
        if any_missing:
            self.update_preview()
            self.refresh_scenes_list()
            self.mark_dirty()
        else:
            self.log_output.append("No missing assets to relink")

    def update_recent_projects(self, path: str):
        try:
            recent = self.settings.value("recent_projects", [])
            if not isinstance(recent, list):
                recent = []
            # Deduplicate and trim
            path = str(Path(path))
            recent = [p for p in recent if p != path]
            recent.insert(0, path)
            recent = recent[:5]
            self.settings.setValue("recent_projects", recent)
            self.populate_recent_combo(recent)
        except Exception:
            pass

    def load_recent_projects(self):
        recent = self.settings.value("recent_projects", [])
        if not isinstance(recent, list):
            recent = []
        self.populate_recent_combo(recent)

    def populate_recent_combo(self, recent: list):
        self.recent_combo.clear()
        if not recent:
            self.recent_combo.addItem("(none)")
            self.recent_combo.setEnabled(False)
        else:
            for p in recent:
                self.recent_combo.addItem(p)
            self.recent_combo.setEnabled(True)

    def open_recent_selected(self):
        idx = self.recent_combo.currentIndex()
        if not self.recent_combo.isEnabled() or idx < 0:
            return
        path = self.recent_combo.currentText()
        if not path or path == "(none)":
            return
        try:
            proj = Project.load(Path(path))
            self.project = proj
            self.project_path = path
            self.refresh_scenes_list()
            if self.project.scenes:
                self.scenes_list.setCurrentRow(0)
                self.on_scene_selected(0)
            self.update_preview()
            self.log_output.append(f"Project loaded: {path}")
            self.update_recent_projects(path)
        except Exception as e:
            self.log_output.append(f"Failed to open recent project: {e}")

    def toggle_play_pause(self):
        if self.scene_play_timer.isActive():
            self.pause_scenes()
        else:
            self.play_scenes()

    # --- Dirty tracking helpers ---
    def update_window_title(self):
        name = str(Path(self.project_path).name) if self.project_path else "Untitled"
        star = "*" if getattr(self, 'dirty', False) else ""
        self.setWindowTitle(f"Pixoo Commander - {name}{star}")

    def mark_dirty(self):
        if not self.dirty:
            self.dirty = True
            self.update_window_title()

    def closeEvent(self, event):
        try:
            if self.dirty:
                if not self.confirm_discard_changes():
                    event.ignore()
                    return
        except Exception:
            pass
        return super().closeEvent(event)

    def on_theme_changed(self, theme_name: str):
        """Handle theme change events"""
        # Update any UI elements that need to be refreshed when theme changes
        self.update_preview()

    def switch_to_light_theme(self):
        """Switch to light theme"""
        self.theme_manager.switch_theme('light')

    def switch_to_dark_theme(self):
        """Switch to dark theme"""
        self.theme_manager.switch_theme('dark')

def main():
    def exception_hook(exctype, value, tb):
        try:
            text = ''.join(traceback.format_exception(exctype, value, tb))
            Path('traceback2.txt').write_text(text)
        except Exception:
            pass
        # Call default hook for visibility in console
        sys.__excepthook__(exctype, value, tb)

    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    window = PixooCommander()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()