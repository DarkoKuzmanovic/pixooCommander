"""Device wrapper around `pixoo.Pixoo` with a simple, mockable API.

Keep all direct Pixoo calls here to ease testing and retries later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import asyncio
import socket
import json
import time
import logging
from typing import Callable

# Set up logging
logger = logging.getLogger(__name__)

try:
    from pixoo import Pixoo  # type: ignore
except Exception:  # pragma: no cover - optionally absent in some envs
    Pixoo = None # type: ignore

try:
    from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
    from zeroconf.asyncio import AsyncZeroconf
except ImportError:
    Zeroconf = None
    AsyncZeroconf = None
    ServiceBrowser = None
    ServiceListener = None

try:
    from async_upnp_client.aiohttp import AiohttpRequester
    from async_upnp_client.ssdp import SSDP_PORT
    from async_upnp_client.utils import CaseInsensitiveDict
    from async_upnp_client.search import async_search
except ImportError:
    AiohttpRequester = None
    SSDP_PORT = 1900
    async_search = None

@dataclass
class DeviceInfo:
    """Information about a discovered device."""
    ip: str
    port: int = 64
    name: str = ""
    model: str = ""
    id: str = ""

@dataclass
class DeviceConfig:
    ip: str
    screen_size: int = 64


class Device:
    """Thin convenience wrapper over the Pixoo client."""

    def __init__(self, config: DeviceConfig):
        self.config = config
        self._client = None

    def connect(self) -> None:
        if Pixoo is None:
            raise RuntimeError("pixoo library not available")
        self._client = Pixoo(self.config.ip, self.config.screen_size)
        # Simple probe
        _ = self.get_device_time()

    # Low-level passthroughs (kept small for now)
    def get_device_time(self):
        self._ensure()
        return self._client.get_device_time()

    def clear(self) -> None:
        self._ensure()
        self._client.clear()

    def draw_text_rgb(self, text: str, x: int, y: int, r: int, g: int, b: int) -> None:
        self._ensure()
        self._client.draw_text_at_location_rgb(text, x, y, r, g, b)

    def draw_image_path(self, path: str) -> None:
        self._ensure()
        self._client.draw_image(path)

    def push(self) -> None:
        self._ensure()
        self._client.push()

    # Discovery methods
    @staticmethod
    async def discover_devices(timeout: int = 10) -> List[DeviceInfo]:
        """Discover Pixoo devices on the network using multiple methods."""
        devices = []
        discovered_ips = set()

        # Try mDNS discovery first
        if Zeroconf is not None:
            try:
                logger.info("Starting mDNS discovery...")
                mdns_devices = await Device._discover_mdns(timeout)
                logger.info(f"Found {len(mdns_devices)} devices via mDNS")
                for device in mdns_devices:
                    if device.ip not in discovered_ips:
                        devices.append(device)
                        discovered_ips.add(device.ip)
            except Exception as e:
                logger.error(f"mDNS discovery failed: {e}")
                pass  # Continue with other methods

        # Try SSDP discovery
        if AiohttpRequester is not None and async_search is not None:
            try:
                logger.info("Starting SSDP discovery...")
                ssdp_devices = await Device._discover_ssdp(timeout)
                logger.info(f"Found {len(ssdp_devices)} devices via SSDP")
                for device in ssdp_devices:
                    if device.ip not in discovered_ips:
                        devices.append(device)
                        discovered_ips.add(device.ip)
            except Exception as e:
                logger.error(f"SSDP discovery failed: {e}")
                pass  # Continue with other methods

        # Try UDP broadcast as fallback
        try:
            logger.info("Starting UDP broadcast discovery...")
            udp_devices = await Device._discover_udp(timeout)
            logger.info(f"Found {len(udp_devices)} devices via UDP broadcast")
            for device in udp_devices:
                if device.ip not in discovered_ips:
                    devices.append(device)
                    discovered_ips.add(device.ip)
        except Exception as e:
            logger.error(f"UDP broadcast discovery failed: {e}")
            pass  # Continue with other methods

        logger.info(f"Total discovered devices: {len(devices)}")
        return devices

    @staticmethod
    async def _discover_mdns(timeout: int = 10) -> List[DeviceInfo]:
        """Discover devices using mDNS/Zeroconf."""
        if AsyncZeroconf is None or ServiceListener is None:
            return []

        devices = []

        class PixooListener(ServiceListener):
            def __init__(self):
                self.devices = []

            def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                try:
                    info = zc.get_service_info(type_, name)
                    if info:
                        ip = socket.inet_ntoa(info.addresses[0]) if info.addresses else None
                        if ip:
                            # Check if this is a Pixoo device by looking at the service name
                            is_pixoo = "pixoo" in name.lower() or "divoom" in name.lower()
                            if not is_pixoo:
                                # Also check for common HTTP services that might be Pixoo devices
                                # by sending a test request
                                try:
                                    import requests
                                    response = requests.get(f"http://{ip}/getinfo", timeout=2)
                                    if response.status_code == 200:
                                        data = response.json()
                                        is_pixoo = "DeviceName" in str(data) or "Pixoo" in str(data)
                                except Exception:
                                    pass

                            if is_pixoo:
                                device = DeviceInfo(
                                    ip=ip,
                                    port=info.port or 64,
                                    name=name,
                                    model="Pixoo",
                                    id=name
                                )
                                self.devices.append(device)
                                logger.info(f"Found Pixoo device via mDNS: {ip}")
                except Exception as e:
                    logger.error(f"Error processing mDNS service {name}: {e}")
                    pass

            def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                pass

            def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                pass

        try:
            aiozc = AsyncZeroconf()
            listener = PixooListener()
            # Look for common service types that Pixoo devices might advertise
            # Also search for generic HTTP services that we'll filter later
            browser = ServiceBrowser(aiozc.zeroconf, ["_http._tcp.local.", "_pixoo._tcp.local."], listener)

            # Wait for discovery
            await asyncio.sleep(timeout)

            # Clean up
            await aiozc.async_close()

            return listener.devices
        except Exception as e:
            logger.error(f"mDNS discovery error: {e}")
            return []

    @staticmethod
    async def _discover_ssdp(timeout: int = 10) -> List[DeviceInfo]:
        """Discover devices using SSDP."""
        if AiohttpRequester is None or async_search is None:
            return []

        devices = []
        try:
            async def on_response(headers):
                """Callback for SSDP responses."""
                try:
                    # Check if this looks like a Pixoo device
                    location = headers.get("location") or headers.get("LOCATION")
                    server = headers.get("server") or headers.get("SERVER", "")
                    usn = headers.get("usn") or headers.get("USN", "")

                    # Look for Pixoo-specific identifiers
                    is_pixoo = ("pixoo" in server.lower() or "pixoo" in usn.lower() or
                               "divoom" in server.lower() or "divoom" in usn.lower())

                    # Extract IP from location URL if available
                    ip = None
                    if location:
                        from urllib.parse import urlparse
                        parsed = urlparse(location)
                        ip = parsed.hostname

                    # If we can't determine from headers, try to verify by sending a test request
                    if not is_pixoo and ip:
                        try:
                            import requests
                            response = requests.get(f"http://{ip}/getinfo", timeout=2)
                            if response.status_code == 200:
                                data = response.json()
                                is_pixoo = "DeviceName" in str(data) or "Pixoo" in str(data)
                        except Exception:
                            pass

                    if is_pixoo and ip:
                        device = DeviceInfo(
                            ip=ip,
                            port=64,  # Default port for Pixoo
                            name=f"Pixoo-{ip}",
                            model="Pixoo",
                            id=ip
                        )
                        devices.append(device)
                        logger.info(f"Found Pixoo device via SSDP: {ip}")
                except Exception as e:
                    logger.error(f"Error processing SSDP response: {e}")
                    pass  # Continue processing other responses

            # Search for all devices
            await async_search(
                search_target="ssdp:all",
                timeout=timeout,
                async_callback=on_response
            )

            return devices
        except Exception as e:
            logger.error(f"SSDP discovery error: {e}")
            return []

    @staticmethod
    async def _discover_udp(timeout: int = 10) -> List[DeviceInfo]:
        """Discover devices using UDP broadcast."""
        devices = []

        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Send discovery packet
        discovery_packet = {
            "Command": "DeviceList",
            "Module": "system",
            "Version": 1
        }

        message = json.dumps(discovery_packet)

        try:
            # Send to broadcast address - fix the broadcast address
            sock.sendto(message.encode(), ('255.255', 6000))
            logger.info("Sent UDP discovery packet")

            # Wait for responses
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = json.loads(data.decode())
                    ip = addr[0]

                    # Check if this looks like a Pixoo device
                    if isinstance(response, dict):
                        # Verify this is actually a Pixoo device by checking for expected keys
                        is_pixoo = "DeviceName" in response or "DeviceType" in response
                        if not is_pixoo:
                            # Try to verify by sending a test request
                            try:
                                import requests
                                test_response = requests.get(f"http://{ip}/getinfo", timeout=2)
                                if test_response.status_code == 200:
                                    test_data = test_response.json()
                                    is_pixoo = "DeviceName" in str(test_data) or "Pixoo" in str(test_data)
                            except Exception:
                                pass

                        if is_pixoo:
                            device = DeviceInfo(
                                ip=ip,
                                port=64,  # Default port for Pixoo
                                name=response.get("DeviceName", f"Pixoo-{ip}"),
                                model=response.get("DeviceType", "Pixoo"),
                                id=response.get("DeviceId", ip)
                            )
                            devices.append(device)
                            logger.info(f"Found Pixoo device via UDP: {ip}")
                except socket.timeout:
                    break
                except json.JSONDecodeError:
                    # Not a JSON response, ignore
                    continue
                except Exception as e:
                    logger.error(f"Error processing UDP response from {addr[0] if 'addr' in locals() else 'unknown'}: {e}")
                    continue
        except Exception as e:
            logger.error(f"UDP discovery error: {e}")
            pass
        finally:
            sock.close()

        return devices

    # Internal helpers
    def _ensure(self) -> None:
        if self._client is None:
            raise RuntimeError("Device not connected. Call connect() first.")
