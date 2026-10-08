"""Cloud.ru settings protect credentials and refuse non-local clients."""
import asyncio
from starlette.requests import Request
from fastapi import HTTPException
from eonverse import cloud_ai
from app import configure_cloud, cloud_status, require_local_admin, CloudSettings


def local_request(origin="http://localhost", host="127.0.0.1"):
    scope = {"type": "http", "method": "POST", "path": "/api/local/cloud/configure",
             "scheme": "http", "server": ("localhost", 80),
             "client": (host, 45000),
             "headers": [(b"host", b"localhost"),
                         (b"origin", origin.encode()),
                         (b"x-eonverse-local-settings", b"1")]}
    return Request(scope)


def test_browser_key_is_never_returned():
    cloud_ai.disconnect()
    request = local_request()
    result = asyncio.run(configure_cloud(request, CloudSettings(
        key="secret-for-tests-012345", model="DeepSeek-V4-Flash")))
    assert result["enabled"]
    assert "secret-for-tests" not in str(result)
    assert "key" not in asyncio.run(cloud_status(request))
    cloud_ai.disconnect()


def test_nonlocal_origin_and_remote_client_rejected():
    for request in (local_request(origin="https://evil.example"),
                    local_request(host="203.0.113.10")):
        try:
            require_local_admin(request)
        except HTTPException as exc:
            assert exc.status_code == 403
        else:
            raise AssertionError("Nonlocal request accepted")


def test_disconnect_blocks_environment(monkeypatch):
    monkeypatch.setenv("EONVERSE_AI_ENABLED", "1")
    monkeypatch.setenv("CLOUDRU_API_KEY", "configured-in-environment")
    monkeypatch.setenv("CLOUDRU_MODEL", "DeepSeek-V4-Flash")
    cloud_ai.configure("test-local-secret-value", "DeepSeek-V4-Flash")
    assert cloud_ai.credentials()[0] == "test-local-secret-value"
    cloud_ai.disconnect()
    assert not cloud_ai.enabled()
    assert cloud_ai.credentials() == (None, None)
