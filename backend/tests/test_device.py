import pytest
from unittest.mock import AsyncMock


class TestDeviceInfo:
    async def test_get_info(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {"Manufacturer": "Sagemcom"}}
        r = await client.get("/device/info")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DeviceInfo", "get", {})

    async def test_get_pairing(self, client, mock_session):
        r = await client.get("/device/pairing")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DeviceInfo", "getPairingInfo", {})

    async def test_update(self, client, mock_session):
        r = await client.put("/device")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DeviceInfo", "update", {})

    async def test_export(self, client, mock_session):
        r = await client.post("/device/export", json={"file_name": "backup.cfg"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DeviceInfo", "export", {"fileName": "backup.cfg"}
        )

    async def test_export_validation_error(self, client):
        r = await client.post("/device/export", json={})
        assert r.status_code == 422

    async def test_restore(self, client, mock_session):
        body = {"url": "http://server/cfg", "username": "u", "password": "p"}
        r = await client.post("/device/config/restore", json=body)
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DeviceInfo.VendorConfigFile",
            "Restore",
            {"url": "http://server/cfg", "username": "u", "password": "p"},
        )

    async def test_restore_extended(self, client, mock_session):
        body = {
            "url": "http://server/cfg",
            "username": "u",
            "password": "p",
            "ca_cert": "cert",
        }
        r = await client.post("/device/config/restore-extended", json=body)
        assert r.status_code == 200

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/device/info")
        assert r.status_code == 403

    async def test_not_found(self, client, mock_session):
        from tests.conftest import not_found
        mock_session.call.side_effect = not_found()
        r = await client.get("/device/info")
        assert r.status_code == 404
