#!/usr/bin/env python3
"""
Scenes management page for Pixoo Commander NiceGUI web app

This module provides a UI component for managing scenes with thumbnail previews.
It uses an in-memory storage system and caches preview images to improve performance.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from nicegui import ui

from ui.preview import async_render_scene_preview

# Import core scene classes for proper scene creation
from core.scenes.base import BaseScene, SceneType
from core.scenes.text import TextScene
from core.scenes.image import ImageScene
from core.scenes.sysinfo import SysInfoScene

logger = logging.getLogger(__name__)


class ScenesPage:
    """
    A NiceGUI page component for managing scenes with thumbnail previews.

    This class provides functionality for:
    - Displaying a grid of scene thumbnails
    - Adding new scenes (text, image, or sysinfo)
    - Editing existing scenes with detailed configuration options
    - Deleting scenes with confirmation
    - Caching preview images to avoid re-rendering
    - Playing/stopping scenes on connected devices
    - Scene reordering with drag-and-drop simulation
    - Scene duration configuration

    Note: This implementation uses in-memory storage and does not persist scenes
    to the core/ persistence layer.
    """

    def __init__(self, get_player: Optional[Callable] = None):
        # In-memory storage for scenes
        self.scenes: List[Dict[str, Any]] = []

        # Cache for thumbnail previews to avoid re-rendering
        self.thumbnail_cache: Dict[int, str] = {}

        # Player getter function (returns Player instance or None)
        # This allows the ScenesPage to access the current player without
        # having a direct reference to the app instance
        self.get_player = get_player

        # UI element references
        self.scenes_container = None
        self.add_scene_dialog = None
        self.edit_scene_dialog = None
        self.scene_to_edit = None
        # Drag and drop state
        self.dragged_index = None

        # References to dialog input elements for dynamic updates
        self.add_scene_inputs = {}
        self.edit_scene_inputs = {}

    def create_ui(self):
        """Create the scenes management page UI"""
        # Add drag and drop CSS
        ui.add_head_html("""
        <style>
        .scene-card[draggable="true"] {
            cursor: grab !important;
            user-select: none;
        }
        .scene-card[draggable="true"]:active {
            cursor: grabbing !important;
        }
        .scene-card.dragging {
            opacity: 0.5;
        }
        .scene-card.drag-over {
            border: 2px dashed #007bff;
        }
        </style>
        """)

        with ui.column().classes('w-full gap-4'):
            # Header with title and add button
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Scene Management').classes('text-2xl font-bold')
                ui.button('Add Scene', icon='add', on_click=self._open_add_scene_dialog).classes('self-end')

            # Container for scene cards
            self.scenes_container = ui.column().classes('w-full gap-4')

            # Add scene dialog
            with ui.dialog() as self.add_scene_dialog, ui.card().classes('w-96'):
                ui.label('Add New Scene').classes('text-xl font-bold')

                scene_type = ui.select(
                    {'text': 'Text Scene', 'image': 'Image Scene', 'sysinfo': 'System Info Scene'},
                    label='Scene Type',
                    value='text'
                ).classes('w-full')

                # Text scene inputs
                with ui.column().classes('w-full gap-2'):
                    text_input = ui.textarea(label='Text Content', placeholder='Enter text for scene').classes('w-full')
                    text_input.visible = True

                    # Text options
                    with ui.row().classes('w-full gap-2'):
                        text_align = ui.select(
                            {'left': 'Left', 'center': 'Center', 'right': 'Right'},
                            label='Alignment',
                            value='left'
                        ).classes('flex-1')

                        line_spacing = ui.number(label='Line Spacing', value=2, min=0, max=20).classes('flex-1')

                    # Per-line editor area (rebuilds from textarea / scene lines)
                    lines_container = ui.column().classes('w-full gap-1')
                    # Buttons for line operations
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Add Line', on_click=lambda _: self.add_add_line()).classes('primary')
                        ui.button('Rebuild From Text', on_click=lambda _: self.rebuild_add_lines_ui())

                    # Helper storage for current lines (list of dicts) - stored on self so handlers can access it
                    self.add_lines_data = []

                    def sync_textarea_from_lines():
                        # Update the textarea content from self.add_lines_data
                        try:
                            text = "\n".join([ln.get('text', '') for ln in self.add_lines_data])
                            self.add_scene_inputs['text_input'].value = text
                            self.add_scene_inputs['text_input'].update()
                        except Exception:
                            pass

                    def rebuild_add_lines_ui():
                        # Clear and rebuild lines UI based on self.add_lines_data (or textarea if empty)
                        lines_container.clear()
                        # If no explicit lines_data, derive from textarea
                        if not self.add_lines_data:
                            text = self.add_scene_inputs['text_input'].value or ""
                            self.add_lines_data = [{'text': t, 'color': [255, 255, 255], 'y': i * (12 + (self.add_scene_inputs['line_spacing'].value if self.add_scene_inputs['line_spacing'].value is not None else 2))} for i, t in enumerate(text.split('\n'))]

                        for idx, line in enumerate(self.add_lines_data):
                            # create per-line row
                            with lines_container:
                                with ui.row().classes('w-full items-center gap-2'):
                                    li_text = ui.input(value=line.get('text', ''), placeholder='Line text').classes('flex-1')
                                    # color inputs
                                    cr = ui.number(value=line.get('color', [255,255,255])[0], min=0, max=255).classes('w-20')
                                    cg = ui.number(value=line.get('color', [255,255,255])[1], min=0, max=255).classes('w-20')
                                    cb = ui.number(value=line.get('color', [255,255,255])[2], min=0, max=255).classes('w-20')
                                    ui.button('↑', on_click=lambda _, i=idx: self.move_add_line_up(i)).props('flat')
                                    ui.button('↓', on_click=lambda _, i=idx: self.move_add_line_down(i)).props('flat')
                                    ui.button('Remove', on_click=lambda _, i=idx: self.remove_add_line(i)).props('flat color=red')

                                    # Wire changes back to self.add_lines_data
                                    def _on_line_text_change(_evt=None, i=idx, input_el=li_text):
                                        try:
                                            self.add_lines_data[i]['text'] = input_el.value
                                            sync_textarea_from_lines()
                                        except Exception:
                                            pass

                                    def _on_color_change(_evt=None, i=idx, r_el=cr, g_el=cg, b_el=cb):
                                        try:
                                            self.add_lines_data[i]['color'] = [int(r_el.value), int(g_el.value), int(b_el.value)]
                                        except Exception:
                                            pass

                                    li_text.on('update:model-value', lambda e, fn=_on_line_text_change: fn())
                                    cr.on('update:model-value', lambda e, fn=_on_color_change: fn())
                                    cg.on('update:model-value', lambda e, fn=_on_color_change: fn())
                                    cb.on('update:model-value', lambda e, fn=_on_color_change: fn())

                    def add_add_line(text: str = ''):
                        # Use self.add_lines_data so other methods can access the lines
                        if not self.add_lines_data:
                            self.add_lines_data = []
                        self.add_lines_data.append({'text': text, 'color': [255, 255, 255], 'y': len(self.add_lines_data) * (12 + (self.add_scene_inputs['line_spacing'].value if self.add_scene_inputs['line_spacing'].value is not None else 2))})
                        rebuild_add_lines_ui()
                        sync_textarea_from_lines()

                    def remove_line(index: int):
                        if self.add_lines_data and 0 <= index < len(self.add_lines_data):
                            self.add_lines_data.pop(index)
                            rebuild_add_lines_ui()
                            sync_textarea_from_lines()

                    def move_line_up(index: int):
                        if self.add_lines_data and 1 <= index < len(self.add_lines_data):
                            self.add_lines_data[index - 1], self.add_lines_data[index] = self.add_lines_data[index], self.add_lines_data[index - 1]
                            rebuild_add_lines_ui()
                            sync_textarea_from_lines()

                    def move_line_down(index: int):
                        if self.add_lines_data and 0 <= index < len(self.add_lines_data) - 1:
                            self.add_lines_data[index + 1], self.add_lines_data[index] = self.add_lines_data[index], self.add_lines_data[index + 1]
                            rebuild_add_lines_ui()
                            sync_textarea_from_lines()

                    # Expose helpers to the instance so other methods can trigger rebuild/sync
                    self.rebuild_add_lines_ui = rebuild_add_lines_ui
                    self.add_add_line = add_add_line
                    self.remove_add_line = remove_line
                    self.move_add_line_up = move_line_up
                    self.move_add_line_down = move_line_down
                    self.sync_textarea_from_lines = sync_textarea_from_lines

                    # X/Y position for legacy single-line scenes
                    with ui.row().classes('w-full gap-2'):
                        text_x = ui.number(label='Text X', value=0, min=-128, max=128).classes('flex-1')
                        text_y = ui.number(label='Text Y', value=0, min=-128, max=128).classes('flex-1')

                    # Text color
                    with ui.row().classes('w-full gap-2 items-center'):
                        ui.label('Text Color:').classes('text-sm')
                        color_r = ui.number(value=255, min=0, max=255).classes('w-20')
                        color_g = ui.number(value=255, min=0, max=255).classes('w-20')
                        color_b = ui.number(value=255, min=0, max=255).classes('w-20')
                        ui.label('R G B').classes('text-xs text-gray-500')

                    # Scrolling options
                    with ui.row().classes('w-full gap-2 items-center'):
                        scroll_enabled = ui.checkbox('Enable Scrolling').classes('flex-1')
                        scroll_direction = ui.select(
                            {'left': 'Left', 'right': 'Right'},
                            label='Direction',
                            value='left'
                        ).classes('flex-1')
                        scroll_direction.bind_visibility_from(scroll_enabled, 'value')

                        scroll_speed = ui.number(label='Speed', value=20, min=1, max=200).classes('flex-1')
                        scroll_speed.bind_visibility_from(scroll_enabled, 'value')

                # Image scene inputs
                with ui.column().classes('w-full gap-2'):
                    image_path_input = ui.input(label='Image Path', placeholder='Enter path to image file').classes('w-full')
                    image_path_input.visible = False

                    # Image fit options
                    image_fit = ui.select(
                        {'contain': 'Contain', 'cover': 'Cover', 'stretch': 'Stretch'},
                        label='Fit Mode',
                        value='contain'
                    ).classes('w-full')

                # SysInfo scene inputs
                with ui.column().classes('w-full gap-2'):
                    sysinfo_theme = ui.select(
                        {'light': 'Light', 'accent': 'Accent', 'mono': 'Monochrome'},
                        label='Theme',
                        value='light'
                    ).classes('w-full')
                    sysinfo_theme.visible = False

                # Common scene inputs
                with ui.column().classes('w-full gap-2'):
                    scene_duration = ui.number(label='Duration (seconds)', value=8, min=1, max=600).classes('w-full')
                    scene_name = ui.input(label='Scene Name', placeholder='Enter scene name').classes('w-full')

                # Store references to inputs for dynamic updates
                self.add_scene_inputs = {
                    'scene_type': scene_type,
                    'text_input': text_input,
                    'text_align': text_align,
                    'line_spacing': line_spacing,
                    'color_r': color_r,
                    'color_g': color_g,
                    'color_b': color_b,
                    'scroll_enabled': scroll_enabled,
                    'scroll_direction': scroll_direction,
                    'scroll_speed': scroll_speed,
                    'image_path_input': image_path_input,
                    'image_fit': image_fit,
                    'sysinfo_theme': sysinfo_theme,
                    'scene_duration': scene_duration,
                    'scene_name': scene_name
                }

                # Show/hide inputs based on scene type
                def on_type_change():
                    # Hide all specialized inputs first
                    text_input.visible = False
                    image_path_input.visible = False
                    sysinfo_theme.visible = False

                    # Show inputs for selected scene type
                    if scene_type.value == 'text':
                        text_input.visible = True
                        text_align.visible = True
                        line_spacing.visible = True
                        color_r.visible = True
                        color_g.visible = True
                        color_b.visible = True
                        scroll_enabled.visible = True
                        scroll_direction.visible = scroll_enabled.value
                        scroll_speed.visible = scroll_enabled.value
                    elif scene_type.value == 'image':
                        image_path_input.visible = True
                        image_fit.visible = True
                    elif scene_type.value == 'sysinfo':
                        sysinfo_theme.visible = True

                    # Update the UI
                    text_input.update()
                    text_align.update()
                    line_spacing.update()
                    color_r.update()
                    color_g.update()
                    color_b.update()
                    scroll_enabled.update()
                    scroll_direction.update()
                    scroll_speed.update()
                    image_path_input.update()
                    image_fit.update()
                    sysinfo_theme.update()

                scene_type.on('update:model-value', lambda _: on_type_change())

                # Bind scroll direction and speed visibility to scroll checkbox
                scroll_enabled.on('update:model-value', lambda e: on_type_change())

                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=self.add_scene_dialog.close)
                    ui.button('Add', on_click=self._handle_add_scene).classes('primary')

            # Edit scene dialog
            with ui.dialog() as self.edit_scene_dialog, ui.card().classes('w-96'):
                ui.label('Edit Scene').classes('text-xl font-bold')

                edit_scene_type = ui.select(
                    {'text': 'Text Scene', 'image': 'Image Scene', 'sysinfo': 'System Info Scene'},
                    label='Scene Type',
                    value='text'
                ).classes('w-full').props('readonly')

                # Text scene inputs
                with ui.column().classes('w-full gap-2'):
                    edit_text_input = ui.textarea(label='Text Content', placeholder='Enter text for scene').classes('w-full')

                    # Text options
                    with ui.row().classes('w-full gap-2'):
                        edit_text_align = ui.select(
                            {'left': 'Left', 'center': 'Center', 'right': 'Right'},
                            label='Alignment',
                            value='left'
                        ).classes('flex-1')

                        edit_line_spacing = ui.number(label='Line Spacing', value=2, min=0, max=20).classes('flex-1')

                    # Per-line editor area (rebuilds from textarea / scene lines)
                    lines_container = ui.column().classes('w-full gap-1')
                    # Buttons for line operations
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Add Line', on_click=lambda _: self.add_edit_line()).classes('primary')
                        ui.button('Rebuild From Text', on_click=lambda _: self.rebuild_edit_lines_ui())

                    # Helper storage for current lines (list of dicts) - stored on self so handlers can access it
                    self.edit_lines_data = []

                    def sync_textarea_from_lines():
                        # Update the textarea content from self.edit_lines_data
                        try:
                            text = "\n".join([ln.get('text', '') for ln in self.edit_lines_data])
                            self.edit_scene_inputs['text_input'].value = text
                            self.edit_scene_inputs['text_input'].update()
                        except Exception:
                            pass

                    def rebuild_edit_lines_ui():
                        # Clear and rebuild lines UI based on self.edit_lines_data (or textarea if empty)
                        lines_container.clear()
                        # If no explicit lines_data, derive from textarea
                        if not self.edit_lines_data:
                            text = self.edit_scene_inputs['text_input'].value or ""
                            self.edit_lines_data = [{'text': t, 'color': [255, 255, 255], 'y': i * (12 + (self.edit_scene_inputs['line_spacing'].value if self.edit_scene_inputs['line_spacing'].value is not None else 2))} for i, t in enumerate(text.split('\n'))]

                        for idx, line in enumerate(self.edit_lines_data):
                            # create per-line row
                            with lines_container:
                                with ui.row().classes('w-full items-center gap-2'):
                                    li_text = ui.input(value=line.get('text', ''), placeholder='Line text').classes('flex-1')
                                    # color inputs
                                    cr = ui.number(value=line.get('color', [255,255,255])[0], min=0, max=255).classes('w-20')
                                    cg = ui.number(value=line.get('color', [255,255,255])[1], min=0, max=255).classes('w-20')
                                    cb = ui.number(value=line.get('color', [255,255,255])[2], min=0, max=255).classes('w-20')
                                    ui.button('↑', on_click=lambda _, i=idx: self.move_edit_line_up(i)).props('flat')
                                    ui.button('↓', on_click=lambda _, i=idx: self.move_edit_line_down(i)).props('flat')
                                    ui.button('Remove', on_click=lambda _, i=idx: self.remove_edit_line(i)).props('flat color=red')

                                    # Wire changes back to self.edit_lines_data
                                    def _on_line_text_change(_evt=None, i=idx, input_el=li_text):
                                        try:
                                            self.edit_lines_data[i]['text'] = input_el.value
                                            sync_textarea_from_lines()
                                        except Exception:
                                            pass

                                    def _on_color_change(_evt=None, i=idx, r_el=cr, g_el=cg, b_el=cb):
                                        try:
                                            self.edit_lines_data[i]['color'] = [int(r_el.value), int(g_el.value), int(b_el.value)]
                                        except Exception:
                                            pass

                                    li_text.on('update:model-value', lambda e, fn=_on_line_text_change: fn())
                                    cr.on('update:model-value', lambda e, fn=_on_color_change: fn())
                                    cg.on('update:model-value', lambda e, fn=_on_color_change: fn())
                                    cb.on('update:model-value', lambda e, fn=_on_color_change: fn())

                    def add_edit_line(text: str = ''):
                        # Use self.edit_lines_data so other methods can access the lines
                        if not self.edit_lines_data:
                            self.edit_lines_data = []
                        self.edit_lines_data.append({'text': text, 'color': [255, 255, 255], 'y': len(self.edit_lines_data) * (12 + (self.edit_scene_inputs['line_spacing'].value if self.edit_scene_inputs['line_spacing'].value is not None else 2))})
                        rebuild_edit_lines_ui()
                        sync_textarea_from_lines()

                    def remove_line(index: int):
                        if self.edit_lines_data and 0 <= index < len(self.edit_lines_data):
                            self.edit_lines_data.pop(index)
                            rebuild_edit_lines_ui()
                            sync_textarea_from_lines()

                    def move_line_up(index: int):
                        if self.edit_lines_data and 1 <= index < len(self.edit_lines_data):
                            self.edit_lines_data[index - 1], self.edit_lines_data[index] = self.edit_lines_data[index], self.edit_lines_data[index - 1]
                            rebuild_edit_lines_ui()
                            sync_textarea_from_lines()

                    def move_line_down(index: int):
                        if self.edit_lines_data and 0 <= index < len(self.edit_lines_data) - 1:
                            self.edit_lines_data[index + 1], self.edit_lines_data[index] = self.edit_lines_data[index], self.edit_lines_data[index + 1]
                            rebuild_edit_lines_ui()
                            sync_textarea_from_lines()

                    # Expose helpers to the instance so other methods can trigger rebuild/sync
                    self.rebuild_edit_lines_ui = rebuild_edit_lines_ui
                    self.add_edit_line = add_edit_line
                    self.remove_edit_line = remove_line
                    self.move_edit_line_up = move_line_up
                    self.move_edit_line_down = move_line_down
                    self.sync_textarea_from_lines = sync_textarea_from_lines

                    # Text color (default / global)
                    with ui.row().classes('w-full gap-2 items-center'):
                        ui.label('Text Color:').classes('text-sm')
                        edit_color_r = ui.number(value=255, min=0, max=255).classes('w-20')
                        edit_color_g = ui.number(value=255, min=0, max=255).classes('w-20')
                        edit_color_b = ui.number(value=255, min=0, max=255).classes('w-20')
                        ui.label('R G B').classes('text-xs text-gray-500')

                    # Scrolling options
                    with ui.row().classes('w-full gap-2 items-center'):
                        edit_scroll_enabled = ui.checkbox('Enable Scrolling').classes('flex-1')
                        edit_scroll_direction = ui.select(
                            {'left': 'Left', 'right': 'Right'},
                            label='Direction',
                            value='left'
                        ).classes('flex-1')
                        edit_scroll_direction.bind_visibility_from(edit_scroll_enabled, 'value')

                        edit_scroll_speed = ui.number(label='Speed', value=20, min=1, max=200).classes('flex-1')
                        edit_scroll_speed.bind_visibility_from(edit_scroll_enabled, 'value')

                # Image scene inputs
                with ui.column().classes('w-full gap-2'):
                    edit_image_path_input = ui.input(label='Image Path', placeholder='Enter path to image file').classes('w-full')

                    # Image fit options
                    edit_image_fit = ui.select(
                        {'contain': 'Contain', 'cover': 'Cover', 'stretch': 'Stretch'},
                        label='Fit Mode',
                        value='contain'
                    ).classes('w-full')

                # SysInfo scene inputs
                with ui.column().classes('w-full gap-2'):
                    edit_sysinfo_theme = ui.select(
                        {'light': 'Light', 'accent': 'Accent', 'mono': 'Monochrome'},
                        label='Theme',
                        value='light'
                    ).classes('w-full')

                # Common scene inputs
                with ui.column().classes('w-full gap-2'):
                    edit_scene_duration = ui.number(label='Duration (seconds)', value=8, min=1, max=600).classes('w-full')
                    edit_scene_name = ui.input(label='Scene Name', placeholder='Enter scene name').classes('w-full')

                # Store references to inputs for dynamic updates
                self.edit_scene_inputs = {
                    'scene_type': edit_scene_type,
                    'text_input': edit_text_input,
                    'text_align': edit_text_align,
                    'line_spacing': edit_line_spacing,
                    'color_r': edit_color_r,
                    'color_g': edit_color_g,
                    'color_b': edit_color_b,
                    'scroll_enabled': edit_scroll_enabled,
                    'scroll_direction': edit_scroll_direction,
                    'scroll_speed': edit_scroll_speed,
                    'image_path_input': edit_image_path_input,
                    'image_fit': edit_image_fit,
                    'sysinfo_theme': edit_sysinfo_theme,
                    'scene_duration': edit_scene_duration,
                    'scene_name': edit_scene_name
                }

                # Bind scroll direction and speed visibility to scroll checkbox
                def on_edit_scroll_change():
                    visible = edit_scroll_enabled.value
                    edit_scroll_direction.visible = visible
                    edit_scroll_speed.visible = visible
                    edit_scroll_direction.update()
                    edit_scroll_speed.update()

                edit_scroll_enabled.on('update:model-value', lambda _: on_edit_scroll_change())

                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=self.edit_scene_dialog.close)
                    ui.button('Save', on_click=self._handle_edit_scene).classes('primary')

            # Initialize the UI with any existing scenes
            self._refresh_scenes_display()

    def _refresh_scenes_display(self):
        """Refresh the scenes display container with current scenes"""
        if not self.scenes_container:
            return

        # Clear existing content
        self.scenes_container.clear()

        # Add scene cards
        with self.scenes_container:
            if not self.scenes:
                ui.label('No scenes yet. Click "Add Scene" to create your first scene.').classes('text-gray-500 italic')
            else:
                # Add some debug info
                logger.debug(f"Refreshing display with {len(self.scenes)} scenes")

                with ui.grid(columns=4).classes('w-full gap-4'):
                    for index, scene in enumerate(self.scenes):
                        logger.debug(f"Creating card for scene {index}: {scene.get('name', 'Unnamed')}")
                        self._create_scene_card(index, scene)

        # Update the container
        self.scenes_container.update()
        logger.debug("Scene display refresh completed")

    def _on_drag_start(self, event, index: int):
        """Handle drag start event"""
        logger.debug(f"DRAG START FIRED - index: {index}")
        logger.debug(f"Event object: {type(event)}")
        logger.debug(f"Event args: {getattr(event, 'args', 'no args')}")

        self.dragged_index = index

        # Try to access drag data transfer
        try:
            if hasattr(event, 'args') and isinstance(event.args, dict):
                logger.debug(f"Event args dict: {event.args}")
                if 'dataTransfer' in event.args:
                    logger.debug(f"DataTransfer found: {event.args['dataTransfer']}")

            # Set drag effect - this might help browsers understand the operation
            # Note: This is experimental and might not work in NiceGUI
            if hasattr(event, 'sender'):
                logger.debug(f"Event sender: {event.sender}")
                # Apply visual feedback
                event.sender.style('opacity: 0.5')

        except Exception as e:
            logger.debug(f"Error in drag start: {e}")

    def _on_drag_over(self, event, index: int):
        """Handle drag over event"""
        logger.debug(f"DRAG OVER FIRED - over card index: {index}")
        logger.debug(f"Event object: {type(event)}")
        logger.debug(f"Event args: {getattr(event, 'args', 'no args')}")
        logger.debug(f"Dragged index: {self.dragged_index}")

        # For HTML5 drag and drop to work, we need to prevent the default behavior
        # In NiceGUI, we can't directly call preventDefault(), but we can try other approaches
        try:
            if hasattr(event, 'args') and isinstance(event.args, dict):
                # Log what's available in the event
                logger.debug(f"Available event args keys: {list(event.args.keys()) if event.args else 'None'}")
        except Exception as e:
            logger.debug(f"Error in drag over: {e}")

    def _on_drop(self, event, target_index: int):
        """Handle drop event"""
        logger.debug(f"DROP FIRED - target index: {target_index}, dragged index: {self.dragged_index}")
        logger.debug(f"Event object: {type(event)}")
        logger.debug(f"Event args: {getattr(event, 'args', 'no args')}")

        try:
            if hasattr(event, 'args') and isinstance(event.args, dict):
                logger.debug(f"Drop event args keys: {list(event.args.keys()) if event.args else 'None'}")

            if self.dragged_index is not None and self.dragged_index != target_index:
                logger.debug(f"Performing reorder: moving scene from {self.dragged_index} to {target_index}")

                # Move the scene from dragged_index to target_index
                scene = self.scenes.pop(self.dragged_index)
                self.scenes.insert(target_index, scene)

                logger.debug(f"Scene reorder completed. New scene count: {len(self.scenes)}")

                # Clear the thumbnail cache since indices have changed
                self.thumbnail_cache.clear()

                # Refresh the display
                self._refresh_scenes_display()

                ui.notify(f"Scene moved from position {self.dragged_index + 1} to position {target_index + 1}")
            else:
                logger.debug(f"No reorder needed: dragged_index={self.dragged_index}, target_index={target_index}")

        except Exception as e:
            logger.error(f"Error in drop handler: {e}")
            ui.notify(f"Error reordering scenes: {str(e)}")

    def _on_drag_end(self, event):
        """Handle drag end event"""
        logger.debug(f"DRAG END FIRED")
        logger.debug(f"Event object: {type(event)}")
        logger.debug(f"Event args: {getattr(event, 'args', 'no args')}")
        logger.debug(f"Resetting dragged_index from {self.dragged_index} to None")

        try:
            # Reset visual feedback
            if hasattr(event, 'sender'):
                event.sender.style('opacity: 1')
                logger.debug("Reset opacity to 1")

            # Reset drag state
            self.dragged_index = None

        except Exception as e:
            logger.debug(f"Error in drag end: {e}")

    def _create_scene_card(self, index: int, scene: Dict[str, Any]):
        """Create a card UI element for a scene"""
        with ui.card().classes('w-full scene-card').props('draggable').style('cursor: grab; user-select: none;') as card:
            logger.debug(f"Creating scene card {index} with draggable=true")

            # Add event handlers separately for better clarity and debugging
            card.on('click', lambda e, idx=index: logger.debug(f"CLICK FIRED on card {idx}"))
            card.on('dragstart', lambda e, idx=index: self._on_drag_start(e, idx))
            card.on('dragover', lambda e, idx=index: self._on_drag_over(e, idx))
            card.on('drop', lambda e, idx=index: self._on_drop(e, idx))
            card.on('dragend', lambda e, idx=index: self._on_drag_end(e, idx))

            logger.debug(f"Attached all event handlers to card {index}")
            # Thumbnail preview
            thumbnail_element = ui.image().classes('w-16 h-16 object-cover rounded')

            # Render thumbnail asynchronously
            async def update_thumbnail():
                # Check cache first
                if index in self.thumbnail_cache:
                    thumbnail_element.set_source(self.thumbnail_cache[index])
                else:
                    # Create a scene object for preview rendering
                    preview_scene = self._create_preview_scene(scene)
                    data_uri = await async_render_scene_preview(preview_scene)
                    self.thumbnail_cache[index] = data_uri
                    thumbnail_element.set_source(data_uri)

            # Run the async thumbnail update
            asyncio.create_task(update_thumbnail())

            # Scene info
            with ui.column().classes('w-full gap-1'):
                # Title (first 16 chars for text scenes)
                title = scene.get('name', scene.get('text', 'Untitled'))[:16] if scene.get('type') == 'text' else scene.get('name', scene.get('type', 'Scene')).title()
                ui.label(title).classes('font-bold truncate')

                # Type badge
                ui.badge(scene.get('type', 'unknown').title()).classes('self-start')

                # Duration
                duration = scene.get('duration_s', 8)
                ui.label(f'{duration}s').classes('text-xs text-gray-500')

                # Action buttons
                with ui.row().classes('w-full justify-end gap-1 mt-2'):
                    # Play button - store reference for enabling/disabling
                    play_button = ui.button('Play', icon='play_arrow', on_click=lambda _, idx=index: self._handle_play_scene(idx)).props('flat round size=sm')
                    play_button.classes('play-button')

                    # Stop button
                    ui.button('Stop', icon='stop', on_click=lambda _, idx=index: self._handle_stop_scene(idx)).props('flat round size=sm color=red')

                    ui.button(icon='edit', on_click=lambda _, idx=index: self._open_edit_scene_dialog(idx)).props('flat round size=sm')
                    ui.button(icon='delete', on_click=lambda _, idx=index: self._confirm_delete_scene(idx)).props('flat round size=sm color=red')

    def _create_preview_scene(self, scene: Dict[str, Any]) -> Any:
        """
        Create a scene object suitable for preview rendering.

        Args:
            scene: The scene dictionary

        Returns:
            A scene-like object that can be rendered by async_render_scene_preview
        """
        class PreviewScene:
            def __init__(self, scene_data):
                self.type = scene_data.get('type', 'text')
                # Handle different scene types with detailed configuration
                if self.type == 'text':
                    # Handle both legacy and new multi-line formats
                    if 'lines' in scene_data:
                        # New multi-line format
                        self.config = {
                            'text_options': scene_data.get('text_options', {
                                'align': 'left',
                                'color': [255, 255, 255],
                                'line_spacing': 2
                            }),
                            'lines': scene_data.get('lines', [])
                        }
                    else:
                        # Legacy single-line format
                        self.text = scene_data.get('text', '')
                        self.config = {
                            'text': self.text,
                            'text_options': {
                                'align': scene_data.get('align', 'left'),
                                'color': scene_data.get('color', [255, 255, 255])
                            }
                        }
                elif self.type == 'image':
                    self.config = {
                        'path': scene_data.get('path', ''),
                        'fit': scene_data.get('fit', 'contain')
                    }
                elif self.type == 'sysinfo':
                    self.config = {
                        'theme': scene_data.get('theme', 'light')
                    }
                else:
                    self.text = ''
                    self.config = {}

        return PreviewScene(scene)

    def _open_add_scene_dialog(self):
        """Open the add scene dialog"""
        if self.add_scene_dialog:
            # Reset dialog inputs
            if 'scene_type' in self.add_scene_inputs:
                self.add_scene_inputs['scene_type'].value = 'text'
            if 'text_input' in self.add_scene_inputs:
                self.add_scene_inputs['text_input'].value = ''
            if 'text_align' in self.add_scene_inputs:
                self.add_scene_inputs['text_align'].value = 'left'
            if 'line_spacing' in self.add_scene_inputs:
                self.add_scene_inputs['line_spacing'].value = 2
            if 'color_r' in self.add_scene_inputs:
                self.add_scene_inputs['color_r'].value = 255
            if 'color_g' in self.add_scene_inputs:
                self.add_scene_inputs['color_g'].value = 255
            if 'color_b' in self.add_scene_inputs:
                self.add_scene_inputs['color_b'].value = 255
            if 'scroll_enabled' in self.add_scene_inputs:
                self.add_scene_inputs['scroll_enabled'].value = False
            if 'scroll_direction' in self.add_scene_inputs:
                self.add_scene_inputs['scroll_direction'].value = 'left'
            if 'scroll_speed' in self.add_scene_inputs:
                self.add_scene_inputs['scroll_speed'].value = 20
            if 'image_path_input' in self.add_scene_inputs:
                self.add_scene_inputs['image_path_input'].value = ''
            if 'image_fit' in self.add_scene_inputs:
                self.add_scene_inputs['image_fit'].value = 'contain'
            if 'sysinfo_theme' in self.add_scene_inputs:
                self.add_scene_inputs['sysinfo_theme'].value = 'light'
            if 'scene_duration' in self.add_scene_inputs:
                self.add_scene_inputs['scene_duration'].value = 8
            if 'scene_name' in self.add_scene_inputs:
                self.add_scene_inputs['scene_name'].value = ''

            # Trigger type change to update visibility
            if 'scene_type' in self.add_scene_inputs:
                # Manually trigger the visibility update
                scene_type = self.add_scene_inputs['scene_type']

                # Update visibility for all inputs
                text_inputs_visible = scene_type.value == 'text'
                image_inputs_visible = scene_type.value == 'image'
                sysinfo_inputs_visible = scene_type.value == 'sysinfo'

                # Update text inputs visibility
                if 'text_input' in self.add_scene_inputs:
                    self.add_scene_inputs['text_input'].visible = text_inputs_visible
                    self.add_scene_inputs['text_input'].update()
                if 'text_align' in self.add_scene_inputs:
                    self.add_scene_inputs['text_align'].visible = text_inputs_visible
                    self.add_scene_inputs['text_align'].update()
                if 'line_spacing' in self.add_scene_inputs:
                    self.add_scene_inputs['line_spacing'].visible = text_inputs_visible
                    self.add_scene_inputs['line_spacing'].update()
                if 'color_r' in self.add_scene_inputs:
                    self.add_scene_inputs['color_r'].visible = text_inputs_visible
                    self.add_scene_inputs['color_r'].update()
                if 'color_g' in self.add_scene_inputs:
                    self.add_scene_inputs['color_g'].visible = text_inputs_visible
                    self.add_scene_inputs['color_g'].update()
                if 'color_b' in self.add_scene_inputs:
                    self.add_scene_inputs['color_b'].visible = text_inputs_visible
                    self.add_scene_inputs['color_b'].update()
                if 'scroll_enabled' in self.add_scene_inputs:
                    self.add_scene_inputs['scroll_enabled'].visible = text_inputs_visible
                    self.add_scene_inputs['scroll_enabled'].update()

                # Update scroll direction and speed visibility based on scroll checkbox
                if 'scroll_enabled' in self.add_scene_inputs and 'scroll_direction' in self.add_scene_inputs:
                    scroll_enabled = self.add_scene_inputs['scroll_enabled'].value
                    if 'scroll_direction' in self.add_scene_inputs:
                        self.add_scene_inputs['scroll_direction'].visible = text_inputs_visible and scroll_enabled
                        self.add_scene_inputs['scroll_direction'].update()
                    if 'scroll_speed' in self.add_scene_inputs:
                        self.add_scene_inputs['scroll_speed'].visible = text_inputs_visible and scroll_enabled
                        self.add_scene_inputs['scroll_speed'].update()

                # Update image inputs visibility
                if 'image_path_input' in self.add_scene_inputs:
                    self.add_scene_inputs['image_path_input'].visible = image_inputs_visible
                    self.add_scene_inputs['image_path_input'].update()
                if 'image_fit' in self.add_scene_inputs:
                    self.add_scene_inputs['image_fit'].visible = image_inputs_visible
                    self.add_scene_inputs['image_fit'].update()

                # Update sysinfo inputs visibility
                if 'sysinfo_theme' in self.add_scene_inputs:
                    self.add_scene_inputs['sysinfo_theme'].visible = sysinfo_inputs_visible
                    self.add_scene_inputs['sysinfo_theme'].update()

            self.add_scene_dialog.open()

    def _open_edit_scene_dialog(self, index: int):
        """Open the edit scene dialog for a specific scene"""
        if index < 0 or index >= len(self.scenes):
            return

        self.scene_to_edit = index
        scene = self.scenes[index]

        if self.edit_scene_dialog:
            # Set dialog inputs based on scene data
            if 'scene_type' in self.edit_scene_inputs:
                self.edit_scene_inputs['scene_type'].value = scene.get('type', 'text')
            if 'text_input' in self.edit_scene_inputs:
                self.edit_scene_inputs['text_input'].value = scene.get('text', '')
            if 'text_align' in self.edit_scene_inputs:
                self.edit_scene_inputs['text_align'].value = scene.get('align', 'left')
            if 'line_spacing' in self.edit_scene_inputs:
                self.edit_scene_inputs['line_spacing'].value = scene.get('line_spacing', 2)
            if 'color_r' in self.edit_scene_inputs:
                color = scene.get('color', [255, 255, 255])
                self.edit_scene_inputs['color_r'].value = color[0] if len(color) > 0 else 255
            if 'color_g' in self.edit_scene_inputs:
                color = scene.get('color', [255, 255, 255])
                self.edit_scene_inputs['color_g'].value = color[1] if len(color) > 1 else 255
            if 'color_b' in self.edit_scene_inputs:
                color = scene.get('color', [255, 255, 255])
                self.edit_scene_inputs['color_b'].value = color[2] if len(color) > 2 else 255
            if 'scroll_enabled' in self.edit_scene_inputs:
                self.edit_scene_inputs['scroll_enabled'].value = scene.get('scroll', False)
            if 'scroll_direction' in self.edit_scene_inputs:
                self.edit_scene_inputs['scroll_direction'].value = scene.get('direction', 'left')
            if 'scroll_speed' in self.edit_scene_inputs:
                self.edit_scene_inputs['scroll_speed'].value = scene.get('speed', 20)
            if 'image_path_input' in self.edit_scene_inputs:
                self.edit_scene_inputs['image_path_input'].value = scene.get('path', '')
            if 'image_fit' in self.edit_scene_inputs:
                self.edit_scene_inputs['image_fit'].value = scene.get('fit', 'contain')
            if 'sysinfo_theme' in self.edit_scene_inputs:
                self.edit_scene_inputs['sysinfo_theme'].value = scene.get('theme', 'light')
            if 'scene_duration' in self.edit_scene_inputs:
                self.edit_scene_inputs['scene_duration'].value = scene.get('duration_s', 8)
            if 'scene_name' in self.edit_scene_inputs:
                self.edit_scene_inputs['scene_name'].value = scene.get('name', '')

            # Show/hide inputs based on scene type
            scene_type = scene.get('type', 'text')
            text_inputs_visible = scene_type == 'text'
            image_inputs_visible = scene_type == 'image'
            sysinfo_inputs_visible = scene_type == 'sysinfo'

            # Update text inputs visibility
            if 'text_input' in self.edit_scene_inputs:
                self.edit_scene_inputs['text_input'].visible = text_inputs_visible
                self.edit_scene_inputs['text_input'].update()
            if 'text_align' in self.edit_scene_inputs:
                self.edit_scene_inputs['text_align'].visible = text_inputs_visible
                self.edit_scene_inputs['text_align'].update()
            if 'line_spacing' in self.edit_scene_inputs:
                self.edit_scene_inputs['line_spacing'].visible = text_inputs_visible
                self.edit_scene_inputs['line_spacing'].update()
            if 'color_r' in self.edit_scene_inputs:
                self.edit_scene_inputs['color_r'].visible = text_inputs_visible
                self.edit_scene_inputs['color_r'].update()
            if 'color_g' in self.edit_scene_inputs:
                self.edit_scene_inputs['color_g'].visible = text_inputs_visible
                self.edit_scene_inputs['color_g'].update()
            if 'color_b' in self.edit_scene_inputs:
                self.edit_scene_inputs['color_b'].visible = text_inputs_visible
                self.edit_scene_inputs['color_b'].update()
            if 'scroll_enabled' in self.edit_scene_inputs:
                self.edit_scene_inputs['scroll_enabled'].visible = text_inputs_visible
                self.edit_scene_inputs['scroll_enabled'].update()

            # Update scroll direction and speed visibility based on scroll checkbox
            if 'scroll_enabled' in self.edit_scene_inputs and 'scroll_direction' in self.edit_scene_inputs:
                scroll_enabled = self.edit_scene_inputs['scroll_enabled'].value
                if 'scroll_direction' in self.edit_scene_inputs:
                    self.edit_scene_inputs['scroll_direction'].visible = text_inputs_visible and scroll_enabled
                    self.edit_scene_inputs['scroll_direction'].update()
                if 'scroll_speed' in self.edit_scene_inputs:
                    self.edit_scene_inputs['scroll_speed'].visible = text_inputs_visible and scroll_enabled
                    self.edit_scene_inputs['scroll_speed'].update()

            # Update image inputs visibility
            if 'image_path_input' in self.edit_scene_inputs:
                self.edit_scene_inputs['image_path_input'].visible = image_inputs_visible
                self.edit_scene_inputs['image_path_input'].update()
            if 'image_fit' in self.edit_scene_inputs:
                self.edit_scene_inputs['image_fit'].visible = image_inputs_visible
                self.edit_scene_inputs['image_fit'].update()

            # Update sysinfo inputs visibility
            if 'sysinfo_theme' in self.edit_scene_inputs:
                self.edit_scene_inputs['sysinfo_theme'].visible = sysinfo_inputs_visible
                self.edit_scene_inputs['sysinfo_theme'].update()

            # Populate per-line editor data from the scene so the per-line UI reflects current state
            if hasattr(self, 'edit_scene_inputs') and self.scene_to_edit is not None:
                try:
                    scene_lines = []
                    if 'lines' in scene:
                        default_color = scene.get('text_options', {}).get('color', [255, 255, 255])
                        for ln in scene.get('lines', []):
                            l = dict(ln)  # shallow copy
                            if 'color' not in l:
                                l['color'] = list(default_color)
                            scene_lines.append(l)
                    else:
                        # Legacy single-line fallback
                        text_val = scene.get('text', '')
                        color_val = scene.get('color', scene.get('text_options', {}).get('color', [255, 255, 255]))
                        scene_lines = [{'text': text_val, 'color': list(color_val), 'y': 20}]

                    # Assign to instance storage and rebuild UI if available
                    self.edit_lines_data = scene_lines
                    if hasattr(self, 'rebuild_edit_lines_ui'):
                        self.rebuild_edit_lines_ui()
                        # Sync textarea value in the dialog inputs
                        if 'text_input' in self.edit_scene_inputs:
                            self.edit_scene_inputs['text_input'].value = "\n".join([ln.get('text', '') for ln in self.edit_lines_data])
                            self.edit_scene_inputs['text_input'].update()
                except Exception:
                    pass

            self.edit_scene_dialog.open()

    def _handle_add_scene(self):
        """Handle adding a new scene with detailed configuration"""
        # Get values from dialog inputs
        scene_type = self.add_scene_inputs['scene_type'].value if 'scene_type' in self.add_scene_inputs else 'text'

        # Create scene dictionary based on type with detailed configuration
        scene = {
            'type': scene_type,
            'name': self.add_scene_inputs['scene_name'].value if 'scene_name' in self.add_scene_inputs else f'{scene_type.title()} Scene',
            'duration_s': int(self.add_scene_inputs['scene_duration'].value) if 'scene_duration' in self.add_scene_inputs else 8
        }

        if scene_type == 'text':
            # Text scene with detailed configuration (base values from dialog inputs)
            text_config = {
                'text': self.add_scene_inputs['text_input'].value if 'text_input' in self.add_scene_inputs else '',
                'align': self.add_scene_inputs['text_align'].value if 'text_align' in self.add_scene_inputs else 'left',
                'line_spacing': int(self.add_scene_inputs['line_spacing'].value) if 'line_spacing' in self.add_scene_inputs else 2,
                'color': [
                    int(self.add_scene_inputs['color_r'].value) if 'color_r' in self.add_scene_inputs else 255,
                    int(self.add_scene_inputs['color_g'].value) if 'color_g' in self.add_scene_inputs else 255,
                    int(self.add_scene_inputs['color_b'].value) if 'color_b' in self.add_scene_inputs else 255
                ],
                'scroll': bool(self.add_scene_inputs['scroll_enabled'].value) if 'scroll_enabled' in self.add_scene_inputs else False,
                'direction': self.add_scene_inputs['scroll_direction'].value if 'scroll_direction' in self.add_scene_inputs else 'left',
                'speed': int(self.add_scene_inputs['scroll_speed'].value) if 'scroll_speed' in self.add_scene_inputs else 20
            }

            # Prefer per-line editor data if present (preserves per-line colors/y)
            if hasattr(self, "add_lines_data") and self.add_lines_data:
                try:
                    line_spacing = int(self.add_scene_inputs['line_spacing'].value) if 'line_spacing' in self.add_scene_inputs else 2
                    default_color = text_config.get('color', [255, 255, 255])
                    scene_lines = []
                    for i, ln in enumerate(self.add_lines_data):
                        l = {
                            'text': ln.get('text', ''),
                            'y': int(ln.get('y', i * (12 + line_spacing)))
                        }
                        # preserve per-line color if provided, otherwise use default
                        l['color'] = list(ln.get('color') or default_color)
                        scene_lines.append(l)

                    scene['lines'] = scene_lines
                    scene['text_options'] = {
                        'align': text_config['align'],
                        'color': default_color,
                        'line_spacing': text_config['line_spacing']
                    }
                    # Remove legacy single-line fields if they exist
                    scene.pop('text', None)
                    scene.pop('align', None)
                    scene.pop('line_spacing', None)
                    scene.pop('color', None)
                except Exception:
                    # Fallback to textarea-based conversion on error
                    text_content = text_config['text']
                    if '\n' in text_content:
                        lines = text_content.split('\n')
                        scene_lines = []
                        line_spacing = text_config['line_spacing']
                        for i, line_text in enumerate(lines):
                            line_config = {
                                'text': line_text,
                                'y': int(i * (12 + line_spacing))
                            }
                            scene_lines.append(line_config)
                        scene['lines'] = scene_lines
                        scene['text_options'] = {
                            'align': text_config['align'],
                            'color': text_config['color'],
                            'line_spacing': text_config['line_spacing']
                        }
                        scene.pop('text', None)
                        scene.pop('align', None)
                        scene.pop('line_spacing', None)
                        scene.pop('color', None)
                    else:
                        scene.update(text_config)
            else:
                # No per-line editor data -> fallback to textarea-based conversion (existing behavior)
                text_content = text_config['text']
                if '\n' in text_content:
                    lines = text_content.split('\n')
                    scene_lines = []
                    line_spacing = text_config['line_spacing']

                    for i, line_text in enumerate(lines):
                        line_config = {
                            'text': line_text,
                            'y': int(i * (12 + line_spacing))  # 12 is default line height
                        }
                        scene_lines.append(line_config)

                    # Update scene with new multi-line format
                    scene['lines'] = scene_lines
                    scene['text_options'] = {
                        'align': text_config['align'],
                        'color': text_config['color'],
                        'line_spacing': text_config['line_spacing']
                    }
                    # Remove legacy single-line fields if they exist
                    scene.pop('text', None)
                    scene.pop('align', None)
                    scene.pop('line_spacing', None)
                    scene.pop('color', None)
                else:
                    # Keep legacy single-line format
                    scene.update(text_config)
        elif scene_type == 'image':
            # Image scene with detailed configuration
            scene.update({
                'path': self.add_scene_inputs['image_path_input'].value if 'image_path_input' in self.add_scene_inputs else '',
                'fit': self.add_scene_inputs['image_fit'].value if 'image_fit' in self.add_scene_inputs else 'contain'
            })
        elif scene_type == 'sysinfo':
            # SysInfo scene with detailed configuration
            scene.update({
                'theme': self.add_scene_inputs['sysinfo_theme'].value if 'sysinfo_theme' in self.add_scene_inputs else 'light'
            })

        # Add to scenes list
        self.scenes.append(scene)

        # Close dialog
        if self.add_scene_dialog:
            self.add_scene_dialog.close()

        # Refresh display
        self._refresh_scenes_display()

    def _handle_edit_scene(self):
        """Handle editing a scene with detailed configuration"""
        if self.scene_to_edit is None or self.scene_to_edit < 0 or self.scene_to_edit >= len(self.scenes):
            return

        # Get values from dialog inputs
        scene_type = self.edit_scene_inputs['scene_type'].value if 'scene_type' in self.edit_scene_inputs else 'text'

        # Update scene with detailed configuration
        self.scenes[self.scene_to_edit].update({
            'type': scene_type,
            'name': self.edit_scene_inputs['scene_name'].value if 'scene_name' in self.edit_scene_inputs else f'{scene_type.title()} Scene',
            'duration_s': int(self.edit_scene_inputs['scene_duration'].value) if 'scene_duration' in self.edit_scene_inputs else 8
        })

        if scene_type == 'text':
            # Text scene with detailed configuration (base values from dialog inputs)
            text_config = {
                'text': self.edit_scene_inputs['text_input'].value if 'text_input' in self.edit_scene_inputs else '',
                'align': self.edit_scene_inputs['text_align'].value if 'text_align' in self.edit_scene_inputs else 'left',
                'line_spacing': int(self.edit_scene_inputs['line_spacing'].value) if 'line_spacing' in self.edit_scene_inputs else 2,
                'color': [
                    int(self.edit_scene_inputs['color_r'].value) if 'color_r' in self.edit_scene_inputs else 255,
                    int(self.edit_scene_inputs['color_g'].value) if 'color_g' in self.edit_scene_inputs else 255,
                    int(self.edit_scene_inputs['color_b'].value) if 'color_b' in self.edit_scene_inputs else 255
                ],
                'scroll': bool(self.edit_scene_inputs['scroll_enabled'].value) if 'scroll_enabled' in self.edit_scene_inputs else False,
                'direction': self.edit_scene_inputs['scroll_direction'].value if 'scroll_direction' in self.edit_scene_inputs else 'left',
                'speed': int(self.edit_scene_inputs['scroll_speed'].value) if 'scroll_speed' in self.edit_scene_inputs else 20
            }

            # Prefer per-line editor data if present (preserves per-line colors/y)
            if hasattr(self, "edit_lines_data") and self.edit_lines_data:
                try:
                    line_spacing = int(self.edit_scene_inputs['line_spacing'].value) if 'line_spacing' in self.edit_scene_inputs else 2
                    default_color = text_config.get('color', [255, 255, 255])
                    scene_lines = []
                    for i, ln in enumerate(self.edit_lines_data):
                        l = {
                            'text': ln.get('text', ''),
                            'y': int(ln.get('y', i * (12 + line_spacing)))
                        }
                        # preserve per-line color if provided, otherwise use default
                        l['color'] = list(ln.get('color') or default_color)
                        scene_lines.append(l)

                    self.scenes[self.scene_to_edit]['lines'] = scene_lines
                    self.scenes[self.scene_to_edit]['text_options'] = {
                        'align': text_config['align'],
                        'color': default_color,
                        'line_spacing': text_config['line_spacing']
                    }
                    # Remove legacy single-line fields if they exist
                    self.scenes[self.scene_to_edit].pop('text', None)
                    self.scenes[self.scene_to_edit].pop('align', None)
                    self.scenes[self.scene_to_edit].pop('line_spacing', None)
                    self.scenes[self.scene_to_edit].pop('color', None)
                except Exception:
                    # Fallback to textarea-based conversion on error
                    text_content = text_config['text']
                    if '\n' in text_content:
                        lines = text_content.split('\n')
                        scene_lines = []
                        line_spacing = text_config['line_spacing']
                        for i, line_text in enumerate(lines):
                            line_config = {
                                'text': line_text,
                                'y': int(i * (12 + line_spacing))
                            }
                            scene_lines.append(line_config)
                        self.scenes[self.scene_to_edit]['lines'] = scene_lines
                        self.scenes[self.scene_to_edit]['text_options'] = {
                            'align': text_config['align'],
                            'color': text_config['color'],
                            'line_spacing': text_config['line_spacing']
                        }
                        self.scenes[self.scene_to_edit].pop('text', None)
                        self.scenes[self.scene_to_edit].pop('align', None)
                        self.scenes[self.scene_to_edit].pop('line_spacing', None)
                        self.scenes[self.scene_to_edit].pop('color', None)
                    else:
                        self.scenes[self.scene_to_edit].update(text_config)
            else:
                # No per-line editor data -> fallback to textarea-based conversion (existing behavior)
                text_content = text_config['text']
                if '\n' in text_content:
                    lines = text_content.split('\n')
                    scene_lines = []
                    line_spacing = text_config['line_spacing']

                    for i, line_text in enumerate(lines):
                        line_config = {
                            'text': line_text,
                            'y': int(i * (12 + line_spacing))  # 12 is default line height
                        }
                        scene_lines.append(line_config)

                    # Update scene with new multi-line format
                    self.scenes[self.scene_to_edit]['lines'] = scene_lines
                    self.scenes[self.scene_to_edit]['text_options'] = {
                        'align': text_config['align'],
                        'color': text_config['color'],
                        'line_spacing': text_config['line_spacing']
                    }
                    # Remove legacy single-line fields if they exist
                    self.scenes[self.scene_to_edit].pop('text', None)
                    self.scenes[self.scene_to_edit].pop('align', None)
                    self.scenes[self.scene_to_edit].pop('line_spacing', None)
                    self.scenes[self.scene_to_edit].pop('color', None)
                else:
                    # Keep legacy single-line format
                    self.scenes[self.scene_to_edit].update(text_config)
        elif scene_type == 'image':
            # Image scene with detailed configuration
            self.scenes[self.scene_to_edit].update({
                'path': self.edit_scene_inputs['image_path_input'].value if 'image_path_input' in self.edit_scene_inputs else '',
                'fit': self.edit_scene_inputs['image_fit'].value if 'image_fit' in self.edit_scene_inputs else 'contain'
            })
        elif scene_type == 'sysinfo':
            # SysInfo scene with detailed configuration
            self.scenes[self.scene_to_edit].update({
                'theme': self.edit_scene_inputs['sysinfo_theme'].value if 'sysinfo_theme' in self.edit_scene_inputs else 'light'
            })

        # Clear cache entry for this scene
        if self.scene_to_edit in self.thumbnail_cache:
            del self.thumbnail_cache[self.scene_to_edit]

        # Close dialog
        if self.edit_scene_dialog:
            self.edit_scene_dialog.close()

        # Reset edit index
        self.scene_to_edit = None

        # Refresh display
        self._refresh_scenes_display()

    def _confirm_delete_scene(self, index: int):
        """Show confirmation dialog for deleting a scene"""
        if index < 0 or index >= len(self.scenes):
            return

        scene = self.scenes[index]
        title = scene.get('name', scene.get('text', 'Untitled'))[:16] if scene.get('type') == 'text' else scene.get('name', scene.get('type', 'Scene')).title()

        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f'Delete Scene "{title}"?').classes('text-lg font-bold')
            ui.label('Are you sure you want to delete this scene? This action cannot be undone.').classes('mb-4')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=confirm_dialog.close)
                ui.button('Delete', on_click=lambda: self._handle_delete_scene(index, confirm_dialog)).classes('negative')

        confirm_dialog.open()

    def _handle_delete_scene(self, index: int, dialog):
        """Handle deleting a scene after confirmation"""
        if index < 0 or index >= len(self.scenes):
            return

        # Remove scene
        del self.scenes[index]

        # Clear cache entries and update indices
        new_cache = {}
        for cache_index, data_uri in self.thumbnail_cache.items():
            if cache_index < index:
                new_cache[cache_index] = data_uri
            elif cache_index > index:
                new_cache[cache_index - 1] = data_uri
        self.thumbnail_cache = new_cache

        # Close confirmation dialog
        dialog.close()

        # Refresh display
        self._refresh_scenes_display()

    def _create_player_scene(self, scene_dict: Dict[str, Any]) -> BaseScene:
        """
        Create a proper BaseScene object from a scene dictionary for use with the Player.

        Args:
            scene_dict: Dictionary containing scene data

        Returns:
            BaseScene: Proper scene object compatible with Player
        """
        scene_type = scene_dict.get('type', 'text')

        if scene_type == 'text':
            # Create a TextScene with proper configuration supporting both legacy and new formats
            if 'lines' in scene_dict:
                # New multi-line format
                return TextScene(
                    name=scene_dict.get('name', 'Text Scene'),
                    duration_s=scene_dict.get('duration_s', 8),
                    config={
                        'text_options': scene_dict.get('text_options', {
                            'align': 'left',
                            'color': [255, 255, 255],
                            'line_spacing': 2
                        }),
                        'lines': scene_dict.get('lines', [])
                    }
                )
            else:
                # Legacy single-line format
                text_content = scene_dict.get('text', '')
                return TextScene(
                    name=scene_dict.get('name', 'Text Scene'),
                    duration_s=scene_dict.get('duration_s', 8),
                    config={
                        'text_options': {
                            'align': scene_dict.get('align', 'left'),
                            'color': scene_dict.get('color', [255, 255, 255])
                        },
                        'lines': [
                            {
                                'text': text_content,
                                'y': 20
                            }
                        ]
                    }
                )
        elif scene_type == 'image':
            # Create an ImageScene with proper configuration
            image_path = scene_dict.get('path', '')
            return ImageScene(
                name=scene_dict.get('name', 'Image Scene'),
                duration_s=scene_dict.get('duration_s', 8),
                config={
                    'path': image_path,
                    'fit': scene_dict.get('fit', 'contain')
                }
            )
        elif scene_type == 'sysinfo':
            # Create a SysInfoScene with proper configuration
            theme = scene_dict.get('theme', 'light')
            return SysInfoScene(
                name=scene_dict.get('name', 'System Info'),
                duration_s=scene_dict.get('duration_s', 8),
                config={
                    'theme': theme
                }
            )
        else:
            # Fallback to a simple text scene
            return TextScene(
                name=scene_dict.get('name', 'Unknown Scene'),
                duration_s=scene_dict.get('duration_s', 8),
                config={
                    'text_options': {
                        'align': 'center',
                        'color': [255, 255, 255]
                    },
                    'lines': [
                        {
                            'text': "Unknown Scene",
                            'y': 20
                        }
                    ]
                }
            )

    async def _handle_play_scene(self, index: int):
        """
        Handle playing a scene.

        This method gets the current player instance via get_player(), validates it,
        and then plays the selected scene. It also updates the UI to show the playing state.
        """
        # Get the player instance
        if self.get_player is None:
            ui.notify("Error: Player getter not configured")
            logger.error("Player getter not configured in ScenesPage")
            return

        player = self.get_player()

        # Check if player is available
        if player is None:
            ui.notify("Please connect to a device first")
            logger.warning("No player available - device not connected")
            return

        # Validate scene index
        if index < 0 or index >= len(self.scenes):
            ui.notify("Invalid scene selected")
            logger.error(f"Invalid scene index: {index}")
            return

        scene = self.scenes[index]

        # Find the play button for this scene and update its state
        try:
            # Safely navigate the UI element hierarchy
            if (self.scenes_container and
                hasattr(self.scenes_container, 'default_slot') and
                self.scenes_container.default_slot and
                hasattr(self.scenes_container.default_slot, 'children') and
                self.scenes_container.default_slot.children):

                # Get the grid container (last child of scenes_container)
                grid_container = self.scenes_container.default_slot.children[-1] if self.scenes_container.default_slot.children else None
                if (grid_container and
                    hasattr(grid_container, 'default_slot') and
                    grid_container.default_slot and
                    hasattr(grid_container.default_slot, 'children') and
                    grid_container.default_slot.children and
                    0 <= index < len(grid_container.default_slot.children)):

                    # Get the specific card for this scene
                    card_container = grid_container.default_slot.children[index]
                    if (card_container and
                        hasattr(card_container, 'default_slot') and
                        card_container.default_slot and
                        hasattr(card_container.default_slot, 'children') and
                        card_container.default_slot.children):

                        # Get the column with action buttons (last child of card)
                        column_container = card_container.default_slot.children[-1]
                        if (column_container and
                            hasattr(column_container, 'default_slot') and
                            column_container.default_slot and
                            hasattr(column_container.default_slot, 'children') and
                            column_container.default_slot.children):

                            # Get the button row (last child of column)
                            button_row = column_container.default_slot.children[-1]
                            if (button_row and
                                hasattr(button_row, 'default_slot') and
                                button_row.default_slot and
                                hasattr(button_row.default_slot, 'children') and
                                button_row.default_slot.children and
                                len(button_row.default_slot.children) > 0):

                                # Get the play button (first child of button row)
                                play_button = button_row.default_slot.children[0]
                                if play_button and hasattr(play_button, 'props'):
                                    # Update button to show playing state
                                    play_button.props('disabled')
                                    play_button.props('label=Playing...')
                                    play_button.update()
        except Exception as e:
            logger.warning(f"Could not update play button state: {e}")

        try:
            # Create a proper scene object that the player can use
            scene_obj = self._create_player_scene(scene)

            # Set the player's scenes and index
            player.set_scenes([scene_obj])
            player.index = 0

            # Render the scene
            player.render_current()

            scene_name = scene.get('name', scene.get('text', 'Untitled'))[:16] if scene.get('type') == 'text' else scene.get('name', scene.get('type', 'Scene')).title()
            ui.notify(f"Playing scene: {scene_name}")
            logger.info(f"Playing scene: {scene}")

        except Exception as e:
            ui.notify(f"Failed to play scene: {str(e)}")
            logger.error(f"Failed to play scene: {e}", exc_info=True)
        finally:
            # Re-enable the play button after a short delay
            async def reenable_button():
                await asyncio.sleep(2)  # Show "Playing..." for 2 seconds
                try:
                    # Safely navigate the UI element hierarchy to re-enable the button
                    if (self.scenes_container and
                        hasattr(self.scenes_container, 'default_slot') and
                        self.scenes_container.default_slot and
                        hasattr(self.scenes_container.default_slot, 'children') and
                        self.scenes_container.default_slot.children):

                        # Get the grid container (last child of scenes_container)
                        grid_container = self.scenes_container.default_slot.children[-1] if self.scenes_container.default_slot.children else None
                        if (grid_container and
                            hasattr(grid_container, 'default_slot') and
                            grid_container.default_slot and
                            hasattr(grid_container.default_slot, 'children') and
                            grid_container.default_slot.children and
                            0 <= index < len(grid_container.default_slot.children)):

                            # Get the specific card for this scene
                            card_container = grid_container.default_slot.children[index]
                            if (card_container and
                                hasattr(card_container, 'default_slot') and
                                card_container.default_slot and
                                hasattr(card_container.default_slot, 'children') and
                                card_container.default_slot.children):

                                # Get the column with action buttons (last child of card)
                                column_container = card_container.default_slot.children[-1]
                                if (column_container and
                                    hasattr(column_container, 'default_slot') and
                                    column_container.default_slot and
                                    hasattr(column_container.default_slot, 'children') and
                                    column_container.default_slot.children):

                                    # Get the button row (last child of column)
                                    button_row = column_container.default_slot.children[-1]
                                    if (button_row and
                                        hasattr(button_row, 'default_slot') and
                                        button_row.default_slot and
                                        hasattr(button_row.default_slot, 'children') and
                                        button_row.default_slot.children and
                                        len(button_row.default_slot.children) > 0):

                                        # Get the play button (first child of button row)
                                        play_button = button_row.default_slot.children[0]
                                        if play_button and hasattr(play_button, 'props'):
                                            # Re-enable the button and reset text
                                            play_button.props(remove='disabled')
                                            play_button.props('label=Play')
                                            play_button.update()
                except Exception as e:
                    logger.warning(f"Could not re-enable play button: {e}")

            asyncio.create_task(reenable_button())

    async def _handle_stop_scene(self, index: int):
        """
        Handle stopping scene playback.

        This method gets the current player instance via get_player() and stops playback.
        """
        # Get the player instance
        if self.get_player is None:
            ui.notify("Error: Player getter not configured")
            logger.error("Player getter not configured in ScenesPage")
            return

        player = self.get_player()

        # Check if player is available
        if player is None:
            ui.notify("No active playback to stop")
            logger.warning("No player available to stop playback")
            return

        try:
            # In a real implementation, we would call player.stop() or similar
            # For now, we'll just notify that playback was stopped
            ui.notify("Scene playback stopped")
            logger.info("Scene playback stopped")
        except Exception as e:
            ui.notify(f"Failed to stop playback: {str(e)}")
            logger.error(f"Failed to stop playback: {e}", exc_info=True)



def example():
    """
    Example usage of the ScenesPage component.

    This function creates a ScenesPage instance and adds sample scenes
    for manual verification when imported.
    """
    # Create page instance
    page = ScenesPage()

    # Add sample scenes
    page.scenes = [
        {
            'type': 'text',
            'name': 'Hello World Scene',
            'text': 'Hello World',
            'duration_s': 10
        },
        {
            'type': 'text',
            'name': 'Multi-line Scene',
            'text': 'This is a longer\ntext example\nwith multiple lines',
            'duration_s': 15,
            'align': 'center',
            'color': [255, 0, 0]
        },
        {
            'type': 'image',
            'name': 'Image Scene',
            'path': '/path/to/image.png',
            'duration_s': 8
        },
        {
            'type': 'sysinfo',
            'name': 'System Info',
            'theme': 'light',
            'duration_s': 8
        }
    ]

    # Create UI
    page.create_ui()

    # Refresh display to show sample scenes
    page._refresh_scenes_display()

    return page


if __name__ == '__main__':
    # This block is for direct testing of the module
    from nicegui import ui

    # Create a simple test app
    @ui.page('/test')
    def test_page():
        ui.label('Scenes Page Test').classes('text-2xl')
        example()

    ui.run()