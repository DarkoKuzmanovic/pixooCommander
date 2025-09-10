import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from ui.pages.scenes import ScenesPage
from core.scenes.base import BaseScene
from core.scenes.text import TextScene
from core.scenes.image import ImageScene
from core.scenes.sysinfo import SysInfoScene


@pytest.fixture
def mock_get_player():
    return Mock(return_value=None)


@pytest.fixture
def scenes_page(mock_get_player):
    return ScenesPage(get_player=mock_get_player)


def test_scenes_page_init(scenes_page):
    assert isinstance(scenes_page.scenes, list)
    assert isinstance(scenes_page.thumbnail_cache, dict)
    assert scenes_page.scenes == []
    assert scenes_page.thumbnail_cache == {}
    assert scenes_page.get_player is not None
    assert scenes_page.scenes_container is None
    assert scenes_page.add_scene_dialog is None
    assert scenes_page.edit_scene_dialog is None
    assert scenes_page.scene_to_edit is None
    assert scenes_page.dragged_index is None
    assert scenes_page.add_scene_inputs == {}
    assert scenes_page.edit_scene_inputs == {}


@patch('ui.pages.scenes.ui')
def test_create_ui(mock_ui, scenes_page):
    scenes_page.create_ui()
    # Verify UI elements are set
    assert scenes_page.scenes_container is not None
    assert scenes_page.add_scene_dialog is not None
    assert scenes_page.edit_scene_dialog is not None
    # Mock calls would be verified, but since ui is patched, assume structure
    mock_ui.column.assert_called()
    mock_ui.row.assert_called()
    mock_ui.label.assert_called()
    mock_ui.button.assert_called()
    mock_ui.dialog.assert_called()


def test_refresh_scenes_display_empty(scenes_page):
    # Patch to avoid UI creation
    with patch.object(scenes_page, 'scenes_container', Mock()):
        scenes_page._refresh_scenes_display()
        # Should clear and add empty label
        scenes_page.scenes_container.clear.assert_called_once()
        # Grid not created since empty


def test_refresh_scenes_display_with_scenes(scenes_page):
    scenes_page.scenes = [{'type': 'text', 'name': 'Test'}]
    with patch.object(scenes_page, 'scenes_container', Mock()), \
         patch.object(scenes_page, '_create_scene_card') as mock_create_card:
        scenes_page._refresh_scenes_display()
        scenes_page.scenes_container.clear.assert_called_once()
        mock_create_card.assert_called_once_with(0, {'type': 'text', 'name': 'Test'})
        scenes_page.scenes_container.update.assert_called_once()


def test_handle_add_scene_text_single_line(scenes_page):
    # Setup mock inputs
    mock_inputs = {
        'scene_type': Mock(value='text'),
        'scene_name': Mock(value='Test Scene'),
        'scene_duration': Mock(value=5),
        'text_input': Mock(value='Hello'),
        'text_align': Mock(value='center'),
        'line_spacing': Mock(value=3),
        'color_r': Mock(value=100),
        'color_g': Mock(value=200),
        'color_b': Mock(value=150),
        'scroll_enabled': Mock(value=False),
    }
    scenes_page.add_scene_inputs = mock_inputs
    scenes_page.add_lines_data = []  # No per-line data

    scenes_page._handle_add_scene()

    assert len(scenes_page.scenes) == 1
    scene = scenes_page.scenes[0]
    assert scene['type'] == 'text'
    assert scene['name'] == 'Test Scene'
    assert scene['duration_s'] == 5
    assert scene['text'] == 'Hello'
    assert scene['align'] == 'center'
    assert scene['line_spacing'] == 3
    assert scene['color'] == [100, 200, 150]
    assert not scene['scroll']
    assert 'lines' not in scene  # Single line


def test_handle_add_scene_text_multi_line_with_per_line(scenes_page):
    # Setup mock inputs
    mock_inputs = {
        'scene_type': Mock(value='text'),
        'scene_name': Mock(value='Multi Test'),
        'scene_duration': Mock(value=10),
        'text_input': Mock(value='Line1\nLine2'),
        'line_spacing': Mock(value=4),
        'color_r': Mock(value=255),
        'color_g': Mock(value=0),
        'color_b': Mock(value=0),
    }
    scenes_page.add_scene_inputs = mock_inputs
    # Per-line data with different colors
    scenes_page.add_lines_data = [
        {'text': 'Line1', 'color': [255, 255, 0], 'y': 0},
        {'text': 'Line2', 'color': [0, 255, 255], 'y': 16}
    ]

    scenes_page._handle_add_scene()

    assert len(scenes_page.scenes) == 1
    scene = scenes_page.scenes[0]
    assert 'lines' in scene
    assert len(scene['lines']) == 2
    assert scene['lines'][0]['text'] == 'Line1'
    assert scene['lines'][0]['color'] == [255, 255, 0]
    assert scene['lines'][0]['y'] == 0
    assert scene['lines'][1]['text'] == 'Line2'
    assert scene['lines'][1]['color'] == [0, 255, 255]
    assert scene['lines'][1]['y'] == 16
    assert scene['text_options']['line_spacing'] == 4
    assert scene['text_options']['color'] == [255, 0, 0]  # Default from inputs
    assert 'text' not in scene


def test_handle_add_scene_image(scenes_page):
    mock_inputs = {
        'scene_type': Mock(value='image'),
        'scene_name': Mock(value='Image Test'),
        'scene_duration': Mock(value=8),
        'image_path_input': Mock(value='/path/to/img.png'),
        'image_fit': Mock(value='cover'),
    }
    scenes_page.add_scene_inputs = mock_inputs

    scenes_page._handle_add_scene()

    scene = scenes_page.scenes[0]
    assert scene['type'] == 'image'
    assert scene['path'] == '/path/to/img.png'
    assert scene['fit'] == 'cover'


def test_handle_edit_scene_with_per_line(scenes_page):
    # Add initial scene
    initial_scene = {'type': 'text', 'name': 'Edit Test', 'duration_s': 5, 'lines': [{'text': 'Old', 'y': 0}]}
    scenes_page.scenes = [initial_scene]
    scenes_page.scene_to_edit = 0

    # Mock inputs
    mock_inputs = {
        'scene_type': Mock(value='text'),
        'scene_duration': Mock(value=7),
        'line_spacing': Mock(value=5),
        'color_r': Mock(value=128),
        'color_g': Mock(value=128),
        'color_b': Mock(value=128),
    }
    scenes_page.edit_scene_inputs = mock_inputs
    # Updated per-line data
    scenes_page.edit_lines_data = [
        {'text': 'Updated', 'color': [100, 100, 100], 'y': 0},
        {'text': 'New Line', 'color': [200, 200, 200], 'y': 17}
    ]

    scenes_page._handle_edit_scene()

    updated_scene = scenes_page.scenes[0]
    assert len(updated_scene['lines']) == 2
    assert updated_scene['lines'][0]['text'] == 'Updated'
    assert updated_scene['lines'][0]['color'] == [100, 100, 100]
    assert updated_scene['lines'][1]['text'] == 'New Line'
    assert updated_scene['text_options']['line_spacing'] == 5
    assert updated_scene['text_options']['color'] == [128, 128, 128]
    assert updated_scene['duration_s'] == 7
    assert scenes_page.scene_to_edit is None


def test_create_player_scene_text_multi_line(scenes_page):
    scene_dict = {
        'type': 'text',
        'name': 'Player Test',
        'duration_s': 10,
        'lines': [{'text': 'Line1', 'y': 0}, {'text': 'Line2', 'y': 16}],
        'text_options': {'align': 'center', 'color': [255, 0, 0], 'line_spacing': 4}
    }
    player_scene = scenes_page._create_player_scene(scene_dict)
    assert isinstance(player_scene, TextScene)
    assert player_scene.name == 'Player Test'
    assert player_scene.duration_s == 10
    assert len(player_scene.config['lines']) == 2
    assert player_scene.config['text_options']['align'] == 'center'


def test_create_player_scene_image(scenes_page):
    scene_dict = {'type': 'image', 'name': 'Img', 'duration_s': 5, 'path': '/img.png', 'fit': 'stretch'}
    player_scene = scenes_page._create_player_scene(scene_dict)
    assert isinstance(player_scene, ImageScene)
    assert player_scene.config['path'] == '/img.png'
    assert player_scene.config['fit'] == 'stretch'


def test_create_player_scene_sysinfo(scenes_page):
    scene_dict = {'type': 'sysinfo', 'name': 'Sys', 'duration_s': 5, 'theme': 'dark'}
    player_scene = scenes_page._create_player_scene(scene_dict)
    assert isinstance(player_scene, SysInfoScene)
    assert player_scene.config['theme'] == 'dark'


def test_create_player_scene_fallback(scenes_page):
    scene_dict = {'type': 'unknown', 'name': 'Fallback'}
    player_scene = scenes_page._create_player_scene(scene_dict)
    assert isinstance(player_scene, TextScene)
    assert player_scene.config['lines'][0]['text'] == 'Unknown Scene'


def test_handle_delete_scene(scenes_page):
    scenes_page.scenes = [{'type': 'text', 'name': 'To Delete'}]
    with patch.object(scenes_page, 'thumbnail_cache', {0: 'data:uri'}), \
         patch('ui.pages.scenes.ui') as mock_ui:  # Mock dialog
        mock_dialog = Mock()
        scenes_page._handle_delete_scene(0, mock_dialog)

    assert len(scenes_page.scenes) == 0
    assert scenes_page.thumbnail_cache == {}
    mock_dialog.close.assert_called_once()


@pytest.mark.asyncio
async def test_handle_play_scene(scenes_page):
    # Mock player
    mock_player = Mock()
    scenes_page.get_player = Mock(return_value=mock_player)
    mock_player.set_scenes = Mock()
    mock_player.render_current = Mock()

    # Add scene
    scenes_page.scenes = [{'type': 'text', 'name': 'Play Test', 'duration_s': 5, 'text': 'Play'}]

    await scenes_page._handle_play_scene(0)

    mock_player.set_scenes.assert_called_once()
    mock_player.render_current.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])