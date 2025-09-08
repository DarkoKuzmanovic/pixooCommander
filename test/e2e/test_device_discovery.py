#!/usr/bin/env python3
"""
Try to discover Pixoo64 device using the pixoo library
"""

import socket
import json
import time

def discover_pixoo_devices():
    """Discover Pixoo devices on the network using UDP broadcast"""
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send discovery packet
    discovery_packet = {
        "Command": "DeviceList",
        "Module": "system",
        "Version": 1
    }

    message = json.dumps(discovery_packet)
    print(f"Sending discovery packet: {message}")

    try:
        # Send to broadcast address
        sock.sendto(message.encode(), ('255.255.255', 6000))
        print("Waiting for responses...")

        # Wait for responses
        start_time = time.time()
        devices = []

        while time.time() - start_time < 5:  # Wait 5 seconds
            try:
                data, addr = sock.recvfrom(1024)
                response = json.loads(data.decode())
                print(f"Received response from {addr}: {response}")
                devices.append((addr[0], response))
            except socket.timeout:
                break
            except Exception as e:
                print(f"Error receiving data: {e}")

        return devices
    except Exception as e:
        print(f"Error during discovery: {e}")
        return []
    finally:
        sock.close()

def test_pixoo_library_connection(pixoo_ip):
    """Test connection using the pixoo library"""
    try:
        from pixoo import Pixoo
        print(f"Trying to connect to Pixoo device at {pixoo_ip}...")
        pixoo = Pixoo(pixoo_ip)

        # Try to get device info
        device_time = pixoo.get_device_time()
        print(f"Successfully connected! Device time: {device_time}")
        return True
    except Exception as e:
        print(f"Failed to connect to {pixoo_ip}: {e}")
        return False

if __name__ == "__main__":
    print("Attempting to discover Pixoo devices on the network...")
    devices = discover_pixoo_devices()

    if devices:
        print(f"\nFound {len(devices)} potential Pixoo devices:")
        for ip, info in devices:
            print(f"  - {ip}: {info}")

        # Try to connect to each device
        for ip, info in devices:
            print(f"\nTesting connection to {ip}...")
            if test_pixoo_library_connection(ip):
                print(f"*** Successfully connected to Pixoo device at {ip}! ***")
    else:
        print("No Pixoo devices found via discovery.")
        print("\nTrying known devices on your network...")

        import os
        test_ip = os.getenv('TEST_DEVICE_IP', '')
        if test_ip:
            print(f"\nTesting connection to test IP {test_ip}...")
            if test_pixoo_library_connection(test_ip):
                print(f"*** Successfully connected to Pixoo device at {test_ip}! ***")
            else:
                print("Could not connect to test IP.")
        else:
            print("No test IP provided via TEST_DEVICE_IP env var. Skipping connection test.")
            print("\nTo run connection test, set TEST_DEVICE_IP env var to device IP.")