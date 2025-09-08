#!/usr/bin/env python3
"""
Final test to verify all functionality works correctly
"""

from pixoo import Pixoo
import psutil

def test_all_features():
    """Test all features of the Pixoo64 device"""
    try:
        print("Testing Pixoo64 device with screen size 64...")

        # Connect to device
        import os
        device_ip = os.getenv('TEST_DEVICE_IP', '')
        if not device_ip:
            print("No TEST_DEVICE_IP environment variable set. Using empty string.")
        pixoo = Pixoo(device_ip, 64)

        # Test 1: Get device info
        print("Test 1: Getting device info...")
        device_time = pixoo.get_device_time()
        print(f"  Device time: {device_time}")

        # Test 2: Clear screen
        print("Test 2: Clearing screen...")
        pixoo.clear()
        pixoo.push()

        # Test 3: Draw text
        print("Test 3: Drawing text...")
        pixoo.draw_text_at_location_rgb("Hello!", 0, 0, 255, 255, 255)
        pixoo.draw_text_at_location_rgb("Pixoo64", 0, 10, 0, 255, 0)
        pixoo.push()

        # Test 4: System info
        print("Test 4: Getting system info...")
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        print(f"  CPU: {cpu_percent:.1f}%, RAM: {memory_percent:.1f}%")

        # Test 5: Display system info
        print("Test 5: Displaying system info...")
        pixoo.clear()
        pixoo.draw_text_at_location_rgb(f"CPU:{cpu_percent:.0f}%", 0, 0, 255, 255, 255)
        pixoo.draw_text_at_location_rgb(f"RAM:{memory_percent:.0f}%", 0, 10, 255, 255, 255)
        pixoo.push()

        print("All tests completed successfully!")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_all_features()