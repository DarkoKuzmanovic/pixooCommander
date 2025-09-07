#!/usr/bin/env python3
"""
Test script for the new multi-line TextScene functionality.
"""

import sys
import os

# Add the core directory to the path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.scenes.text import TextScene
from core.scenes.base import SceneType
from core.device import Device, DeviceConfig

# Mock device for testing
class MockDevice:
    def __init__(self):
        self.config = DeviceConfig(ip="192.168.0.100", screen_size=64)
        self.draw_calls = []
        self.cleared = False
        self.pushed = False

    def clear(self):
        self.cleared = True

    def draw_text_rgb(self, text, x, y, r, g, b):
        self.draw_calls.append({
            'text': text,
            'x': x,
            'y': y,
            'color': (r, g, b)
        })

    def push(self):
        self.pushed = True

def test_multiline_text_scene():
    """Test the new multi-line text scene functionality."""
    print("Testing multi-line TextScene...")

    # Create a multi-line text scene
    scene = TextScene(
        name="Test Multi-line Scene",
        duration_s=10,
        config={
            "text_options": {
                "align": "center",
                "line_spacing": 2,
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Line 1", "y": 0},
                {"text": "Line 2", "y": 12, "color": [255, 0, 0]},
                {"text": "Line 3", "y": 24}
            ]
        }
    )

    # Validate the scene
    scene.validate()

    # Render with mock device
    device = MockDevice()
    scene.render(device)

    # Check that device methods were called
    assert device.cleared, "Device clear() should be called"
    assert device.pushed, "Device push() should be called"

    # Check that we have the right number of draw calls
    assert len(device.draw_calls) == 3, f"Expected 3 draw calls, got {len(device.draw_calls)}"

    # Check first line
    assert device.draw_calls[0]['text'] == "Line 1"
    assert device.draw_calls[0]['y'] == 0
    assert device.draw_calls[0]['color'] == (255, 255, 255)
    # Check center alignment (6 characters * 6 pixels = 36, (64-36)/2 = 14)
    assert device.draw_calls[0]['x'] == 14

    # Check second line
    assert device.draw_calls[1]['text'] == "Line 2"
    assert device.draw_calls[1]['y'] == 12
    assert device.draw_calls[1]['color'] == (255, 0, 0)
    assert device.draw_calls[1]['x'] == 14 # Should also be centered

    # Check third line
    assert device.draw_calls[2]['text'] == "Line 3"
    assert device.draw_calls[2]['y'] == 24
    assert device.draw_calls[2]['color'] == (255, 255, 255)
    assert device.draw_calls[2]['x'] == 14  # Should also be centered

    print("✓ Multi-line TextScene test passed!")

def test_legacy_compatibility():
    """Test that legacy single-line format still works."""
    print("Testing legacy compatibility...")

    # Create a legacy single-line text scene
    scene = TextScene(
        name="Test Legacy Scene",
        duration_s=10,
        config={
            "text": "Hello World",
            "x": 10,
            "y": 20,
            "color": (0, 255, 0)
        }
    )

    # Validate the scene (should trigger migration)
    scene.validate()

    # Check that migration happened
    assert "lines" in scene.config, "Migration to multi-line format failed"
    assert "text_options" in scene.config, "Migration to multi-line format failed"

    # Render with mock device
    device = MockDevice()
    scene.render(device)

    # Check that device methods were called
    assert device.cleared, "Device clear() should be called"
    assert device.pushed, "Device push() should be called"

    # Check that we have the right number of draw calls
    assert len(device.draw_calls) == 1, f"Expected 1 draw call, got {len(device.draw_calls)}"

    # Check the line
    assert device.draw_calls[0]['text'] == "Hello World"
    assert device.draw_calls[0]['x'] == 10
    assert device.draw_calls[0]['y'] == 20
    assert device.draw_calls[0]['color'] == (0, 255, 0)

    print("✓ Legacy compatibility test passed!")

def test_left_alignment():
    """Test left alignment."""
    print("Testing left alignment...")

    scene = TextScene(
        name="Test Left Align",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",
                "color": [25, 255, 255]
            },
            "lines": [
                {"text": "Left", "y": 0}
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    assert device.draw_calls[0]['x'] == 0, f"Expected x=0 for left alignment, got {device.draw_calls[0]['x']}"

    print("✓ Left alignment test passed!")

def test_right_alignment():
    """Test right alignment."""
    print("Testing right alignment...")

    scene = TextScene(
        name="Test Right Align",
        duration_s=10,
        config={
            "text_options": {
                "align": "right",
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Right", "y": 0}  # 5 characters
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # 5 characters * 6 pixels = 30, 64 - 30 = 34
    expected_x = 34
    assert device.draw_calls[0]['x'] == expected_x, f"Expected x={expected_x} for right alignment, got {device.draw_calls[0]['x']}"

    print("✓ Right alignment test passed!")

def test_default_line_spacing():
    """Test default line spacing behavior (12 pixels per line)."""
    print("Testing default line spacing...")

    scene = TextScene(
        name="Test Default Line Spacing",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Line 1"},  # No explicit y, should default to 0
                {"text": "Line 2"},  # No explicit y, should default to 12
                {"text": "Line 3"}   # No explicit y, should default to 24
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # Check that we have the right number of draw calls
    assert len(device.draw_calls) == 3, f"Expected 3 draw calls, got {len(device.draw_calls)}"

    # Check Y positions with default line spacing (12 pixels)
    assert device.draw_calls[0]['y'] == 0, f"Expected y=0 for first line, got {device.draw_calls[0]['y']}"
    assert device.draw_calls[1]['y'] == 12, f"Expected y=12 for second line, got {device.draw_calls[1]['y']}"
    assert device.draw_calls[2]['y'] == 24, f"Expected y=24 for third line, got {device.draw_calls[2]['y']}"

    print("✓ Default line spacing test passed!")

def test_explicit_line_positions():
    """Test explicit line positions override default spacing."""
    print("Testing explicit line positions...")

    scene = TextScene(
        name="Test Explicit Line Positions",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Line 1", "y": 5},   # Explicit y position
                {"text": "Line 2", "y": 20},  # Explicit y position
                {"text": "Line 3", "y": 40}   # Explicit y position
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # Check that we have the right number of draw calls
    assert len(device.draw_calls) == 3, f"Expected 3 draw calls, got {len(device.draw_calls)}"

    # Check explicit Y positions
    assert device.draw_calls[0]['y'] == 5, f"Expected y=5 for first line, got {device.draw_calls[0]['y']}"
    assert device.draw_calls[1]['y'] == 20, f"Expected y=20 for second line, got {device.draw_calls[1]['y']}"
    assert device.draw_calls[2]['y'] == 40, f"Expected y=40 for third line, got {device.draw_calls[2]['y']}"

    print("✓ Explicit line positions test passed!")

def test_empty_text_lines():
    """Test handling of empty text lines."""
    print("Testing empty text lines handling...")

    scene = TextScene(
        name="Test Empty Lines",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",
                "color": [25, 255, 255]
            },
            "lines": [
                {"text": "Line 1", "y": 0},
                {"text": "", "y": 12},  # Empty line
                {"text": "Line 3", "y": 24}
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # Empty lines should be skipped, so only 2 draw calls
    assert len(device.draw_calls) == 2, f"Expected 2 draw calls (empty line skipped), got {len(device.draw_calls)}"

    # Check that the empty line was skipped
    assert device.draw_calls[0]['text'] == "Line 1"
    assert device.draw_calls[1]['text'] == "Line 3"

    print("✓ Empty text lines test passed!")

def test_long_text_lines():
    """Test text lines with different alignments."""
    print("Testing text lines with different alignments...")

    # Create a moderate length text
    moderate_text = "Moderate length text"

    scene = TextScene(
        name="Test Moderate Text",
        duration_s=10,
        config={
            "text_options": {
                "align": "center",  # Test center alignment
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": moderate_text, "y": 0}
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # Check the text
    assert device.draw_calls[0]['text'] == moderate_text

    # Check center alignment (19 characters * 6 pixels = 114, (64-114)/2 = -25, but clamped to 0)
    # Since the text is longer than screen, it should be clamped to 0
    assert device.draw_calls[0]['x'] == 0, f"Expected x=0 for center alignment of long text, got {device.draw_calls[0]['x']}"

    print("✓ Text lines with different alignments test passed!")

def test_mixed_color_configurations():
    """Test mixed color configurations."""
    print("Testing mixed color configurations...")

    scene = TextScene(
        name="Test Mixed Colors",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",
                "color": [100, 100, 100]  # Global color
            },
            "lines": [
                {"text": "Line 1", "y": 0},  # Should use global color
                {"text": "Line 2", "y": 12, "color": [255, 0, 0]},  # Should use line color
                {"text": "Line 3", "y": 24}  # Should use global color
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # Check that we have the right number of draw calls
    assert len(device.draw_calls) == 3, f"Expected 3 draw calls, got {len(device.draw_calls)}"

    # Check first line uses global color
    assert device.draw_calls[0]['text'] == "Line 1"
    assert device.draw_calls[0]['color'] == (100, 100, 100)

    # Check second line uses line color
    assert device.draw_calls[1]['text'] == "Line 2"
    assert device.draw_calls[1]['color'] == (255, 0, 0)

    # Check third line uses global color
    assert device.draw_calls[2]['text'] == "Line 3"
    assert device.draw_calls[2]['color'] == (100, 100, 100)

    print("✓ Mixed color configurations test passed!")

def test_explicit_x_positions():
    """Test explicit x positions in line configurations."""
    print("Testing explicit x positions...")

    scene = TextScene(
        name="Test Explicit X",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",  # This should be ignored when x is explicit
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Line 1", "x": 20, "y": 0},  # Explicit x position
                {"text": "Line 2", "y": 12}  # Should use alignment
            ]
        }
    )

    scene.validate()
    device = MockDevice()
    scene.render(device)

    # Check that we have the right number of draw calls
    assert len(device.draw_calls) == 2, f"Expected 2 draw calls, got {len(device.draw_calls)}"

    # Check first line uses explicit x position
    assert device.draw_calls[0]['text'] == "Line 1"
    assert device.draw_calls[0]['x'] == 20, f"Expected x=20, got {device.draw_calls[0]['x']}"

    # Check second line uses alignment (left align = x=0)
    assert device.draw_calls[1]['text'] == "Line 2"
    assert device.draw_calls[1]['x'] == 0, f"Expected x=0 for left alignment, got {device.draw_calls[1]['x']}"

    print("✓ Explicit x positions test passed!")

def test_config_validation():
    """Test TextScene config validation."""
    print("Testing config validation...")

    # Test valid multi-line config
    valid_scene = TextScene(
        name="Valid Scene",
        duration_s=10,
        config={
            "text_options": {
                "align": "center",
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Line 1"}
            ]
        }
    )

    try:
        valid_scene.validate()
        print("✓ Valid config validation passed!")
    except Exception as e:
        assert False, f"Valid config should not raise exception: {e}"

    # Test invalid alignment
    invalid_scene = TextScene(
        name="Invalid Scene",
        duration_s=10,
        config={
            "text_options": {
                "align": "invalid",  # Invalid alignment
                "color": [255, 255, 255]
            },
            "lines": [
                {"text": "Line 1"}
            ]
        }
    )

    try:
        invalid_scene.validate()
        assert False, "Invalid alignment should raise exception"
    except ValueError:
        print("✓ Invalid alignment validation passed!")

    # Test missing text in line
    invalid_scene2 = TextScene(
        name="Invalid Scene 2",
        duration_s=10,
        config={
            "text_options": {
                "align": "left",
                "color": [255, 255, 255]
            },
            "lines": [
                {}  # Missing 'text' field
            ]
        }
    )

    try:
        invalid_scene2.validate()
        assert False, "Missing text field should raise exception"
    except ValueError:
        print("✓ Missing text field validation passed!")

    print("✓ Config validation tests passed!")

def test_migration_edge_cases():
    """Test edge cases in legacy format migration."""
    print("Testing migration edge cases...")

    # Test migration with string alignment
    scene1 = TextScene(
        name="Migrate String Align",
        duration_s=10,
        config={
            "text": "Hello",
            "x": "center",  # String alignment
            "y": 20,
            "color": (255, 0, 0)
        }
    )

    scene1.validate()
    assert "lines" in scene1.config, "Migration should create lines array"
    assert scene1.config["text_options"]["align"] == "center", "String alignment should be converted"

    # Test migration with explicit x position
    scene2 = TextScene(
        name="Migrate Explicit X",
        duration_s=10,
        config={
            "text": "Hello",
            "x": 30, # Explicit integer position
            "y": 20,
            "color": (0, 25, 0)
        }
    )

    scene2.validate()
    assert "lines" in scene2.config, "Migration should create lines array"
    assert scene2.config["lines"][0]["x"] == 30, "Explicit x position should be preserved"

    print("✓ Migration edge cases test passed!")

if __name__ == "__main__":
    test_multiline_text_scene()
    test_legacy_compatibility()
    test_left_alignment()
    test_right_alignment()
    test_default_line_spacing()
    test_explicit_line_positions()
    test_empty_text_lines()
    test_long_text_lines()
    test_mixed_color_configurations()
    test_explicit_x_positions()
    test_config_validation()
    test_migration_edge_cases()
    print("\n🎉 All tests passed!")