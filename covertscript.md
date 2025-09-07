# Converting Existing Scripts to Pytest

This guide outlines how to convert the remaining scripts in `test/` to pytest tests using the harness already added (`pytest.ini` and `test/conftest.py`).

## Target Scripts

- `test/test_device_endpoints.py` → `test/test_device_endpoints.py`
- `test/discover_pixoo.py` → `test/test_discovery.py`
- `test/find_device.py`, `test/find_device_simple.py` → `test/test_find_device.py`
- `test/test_message*.py` → `test/test_messages.py`
- `test/check_methods.py` → `test/test_methods.py`
- `test/final_test.py` → fold into the most relevant file(s)

## General Rules

- Use functions `test_*` with `assert` instead of prints.
- Mark network-dependent tests: `@pytest.mark.network` and use `pixoo_ip` fixture.
- Use `qt_app` fixture for any GUI-related code.
- Keep tests small, focused, and deterministic; prefer timeouts on network calls.
- Avoid global side effects; clean up device state when needed (e.g., `pixoo.clear()` at end).

## Example Conversion

From `test/test_device_endpoints.py` (imperative, prints) to pytest:

```bash
# test/test_device_endpoints.py
import pytest, requests

@pytest.mark.network
def test_device_http_endpoints(pixoo_ip):
    urls = [f"http://{pixoo_ip}/", f"http://{pixoo_ip}/getinfo",
            f"http://{pixoo_ip}/getdevicetime", f"http://{pixoo_ip}/getdeviceinfo"]
    for url in urls:
        r = requests.get(url, timeout=3)
        assert r.status_code == 200
```

From `test/test_message.py` (printing) to pytest with Pixoo:

```bash
# test/test_messages.py
import pytest
from pixoo import Pixoo

@pytest.mark.network
def test_draw_text_and_push(pixoo_ip):
    p = Pixoo(pixoo_ip, 64)
    p.clear()
    p.draw_text_at_location_rgb("Hello", 0, 0, 255, 255, 255)
    p.push()  # no exception
```

## Naming & Structure

- File names: `test_*.py`; function names: `test_*`.
- Group related tests per file (endpoints, discovery, messages, methods).
- Replace scripts with multiple flows into separate `test_*` functions.

## Running

- Non-network: `pytest -q`
- Network (requires device): `PIXOO_IP=192.168.0.103 pytest -m network -q`

## Checklist per Script

- Identify network use and add `@pytest.mark.network`.
- Replace `print`/`return True/False` with `assert`.
- Parameterize obvious variations with `@pytest.mark.parametrize`.
- Use `pixoo_ip`/`qt_app` fixtures where appropriate.
- Ensure tests finish quickly and fail fast on timeouts.
