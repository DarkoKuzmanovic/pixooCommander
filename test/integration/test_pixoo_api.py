#!/usr/bin/env python3
"""
Check available methods in the Pixoo library
"""

from pixoo import Pixoo

def check_pixoo_methods(ip):
    """Check what methods are available in the Pixoo library"""
    try:
        print(f"Connecting to Pixoo device at {ip}...")
        pixoo = Pixoo(ip)

        # Print all available methods
        print("Available methods in Pixoo class:")
        methods = [method for method in dir(pixoo) if not method.startswith('_')]
        for method in methods:
            print(f"  - {method}")

        # Test some basic methods
        print("\nTesting basic methods...")

        # Get device info
        print("Getting device info...")
        device_time = pixoo.get_device_time()
        print(f"Device time: {device_time}")

        # Try to clear the screen
        print("Clearing screen...")
        pixoo.clear()

        # Try to set brightness
        print("Setting brightness to 50%...")
        pixoo.set_brightness(50)

        # Try to push changes
        print("Pushing changes...")
        pixoo.push()

        print("Basic tests completed successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Use the IP we found
    ip = "192.168.0.103"
    check_pixoo_methods(ip)