#!/usr/bin/env python3
"""
Test specific Pixoo device endpoints
"""

import requests
import json

def test_pixoo_device(ip):
    """Test if the IP corresponds to a Pixoo device by checking specific endpoints"""
    urls_to_test = [
        f"http://{ip}/",
        f"http://{ip}/getinfo",
        f"http://{ip}/getdevicetime",
        f"http://{ip}/getdeviceinfo"
    ]

    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=3)
            print(f"Response from {url}:")
            print(f"  Status code: {response.status_code}")

            # Try to parse JSON response
            try:
                data = response.json()
                print(f"  JSON data: {json.dumps(data, indent=2)}")
                if "DeviceName" in str(data) or "Pixoo" in str(data):
                    print(f"*** This is likely your Pixoo64 device! ***")
                    return True
            except:
                # If not JSON, print first 200 characters
                print(f"  Response text: {response.text[:200]}")

            print()
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to {url}: {e}")
            print()

    return False

if __name__ == "__main__":
    # Test the devices we found
    devices_to_test = ["192.168.0.108"]

    print("Testing potential Pixoo devices...")
    for device_ip in devices_to_test:
        print(f"\n--- Testing {device_ip} ---")
        if test_pixoo_device(device_ip):
            print(f"Found Pixoo device at {device_ip}!")
            break
    else:
        print("No Pixoo devices found.")