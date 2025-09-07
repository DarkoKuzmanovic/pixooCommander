#!/usr/bin/env python3
"""
Pytest-style network test for Pixoo64 connectivity and basic actions.

Run with a device IP: PIXOO_IP=192.168.0.103 pytest -m network
"""

import pytest
from pixoo import Pixoo


@pytest.mark.network
def test_connection_and_draw(pixoo_ip):
    """Connect, query time, clear, draw text, and push."""
    pixoo = Pixoo(pixoo_ip, 64)

    # Device time should be retrievable (not None/empty)
    device_time = pixoo.get_device_time()
    assert device_time is not None and str(device_time) != ""

    # Basic draw cycle should not raise
    pixoo.clear()
    pixoo.draw_text_at_location_rgb("Test", 0, 0, 255, 255, 255)
    pixoo.push()
