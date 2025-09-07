#!/usr/bin/env python3
"""
Test sending a message to the Pixoo64 device using correct method signatures
"""

from pixoo import Pixoo

def test_pixoo_features(ip):
    """Test various features of the Pixoo device"""
    try:
        print(f"Connecting to Pixoo device at {ip}...")
        pixoo = Pixoo(ip)
        
        # Test getting device info
        print("Getting device time...")
        device_time = pixoo.get_device_time()
        print(f"Device time: {device_time}")
        
        # Clear the screen
        print("Clearing screen...")
        pixoo.clear()
        
        # Draw some text using the correct method signature
        print("Drawing text...")
        # Method signature is: draw_text_at_location_rgb(self, text, x, y, r, g, b)
        pixoo.draw_text_at_location_rgb("Hello Pixoo!", 0, 0, 255, 255, 255)  # White text
        pixoo.draw_text_at_location_rgb("It works!", 0, 10, 0, 255, 0)  # Green text
        
        # Push to device
        print("Pushing to device...")
        pixoo.push()
        
        print("Successfully sent message to Pixoo device!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Use the IP we found
    ip = "192.168.0.103"
    test_pixoo_features(ip)