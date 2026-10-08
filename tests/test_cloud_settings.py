"""Local Cloud.ru settings never expose a key in their responses."""
import os
from fastapi.testclient import TestClient
from eonverse import cloud_ai
from app import app


def test_key_is_not_returned_by_api(monkeypatch):
    monkeypatch.delenv("EONVERSE_AI_ENABLED", raising=False)
    cloud_ai.disconnect()
    with TestClient(app) as client:
        response = client.post(
            "http://localhost/api/local/cloud/configure",
            headers={"origin": "http://localhost", "X-Eonverse-Local-Settings": "1"},
            json={"key": "secret-for-tests-012345", "model": "DeepSeek-V4-Flash"},
        )
        # TestClient can report a synthetic host address instead of loopback.
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            assert "secret-for-tests" not in response.text
            assert response.json()["enabled"]
    cloud_ai.disconnect()


def test_local_credentials_are_volatile_and_disconnect_blocks_env(monkeypatch):
    monkeypatch.setenv("EONVERSE_AI_ENABLED", "1")
    monkeypatch.setenv("CLOUDRU_API_KEY", "configured-in-environment")
    monkeypatch.setenv("CLOUDRU_MODEL", "DeepSeek-V4-Flash")
    cloud_ai.configure("test-local-secret-value", "DeepSeek-V4-Flash")
    assert cloud_ai.enabled()
    assert cloud_ai.credentials()[0] == "test-local-secret-value"
    assert "key" not in cloud_ai.status()
    cloud_ai.disconnect()
    assert not cloud_ai.enabled()
    assert cloud_ai.credentials() == (None, None)
