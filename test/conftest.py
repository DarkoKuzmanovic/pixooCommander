import os
import pytest
from unittest.mock import MagicMock

try:
    from PySide6.QtWidgets import QApplication
except Exception:  # pragma: no cover - optional in non-GUI environments
    QApplication = None  # type: ignore


@pytest.fixture(scope="session")
def qt_app():
    """Provide a QApplication for GUI-related tests."""
    if QApplication is None:
        pytest.skip("PySide6 not available; skipping GUI tests")
    app = QApplication.instance() or QApplication([])
    return app


@pytest.fixture
def pixoo_ip():
    """Device IP from env; skip if not set."""
    ip = os.getenv("PIXOO_IP")
    if not ip:
        pytest.skip("PIXOO_IP not set; skipping network test")
    return ip


@pytest.fixture
def mock_pixoo():
    """Mock Pixoo device for unit testing."""
    mock = MagicMock()
    mock.get_device_time.return_value = "2023-01-01 12:00:00"
    return mock


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "device": {
            "ip": "192.168.0.100",
            "screen_size": 64
        },
        "scenes": [
            {
                "type": "text",
                "name": "Test Scene",
                "duration_s": 10,
                "config": {
                    "text": "Hello World",
                    "x": 0,
                    "y": 0,
                    "color": [255, 255, 255]
                }
            }
        ]
    }
