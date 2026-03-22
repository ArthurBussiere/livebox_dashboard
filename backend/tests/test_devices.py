import pytest


class TestDevices:
    async def test_get_devices(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": []}
        r = await client.get("/devices")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("Devices", "get", {"flags": ""})

    async def test_find_devices(self, client, mock_session):
        r = await client.post("/devices/find", json={"expression": {"Active": True}})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices",
            "find",
            {"expression": {"Active": True}, "flags": ""},
        )

    async def test_fetch_device(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {"Key": "aa:bb:cc:dd:ee:ff"}}
        r = await client.get("/devices/aa:bb:cc:dd:ee:ff")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices", "fetchDevice", {"key": "aa:bb:cc:dd:ee:ff", "flags": ""}
        )

    async def test_destroy_device(self, client, mock_session):
        r = await client.delete("/devices/aa:bb:cc:dd:ee:ff")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices", "destroyDevice", {"key": "aa:bb:cc:dd:ee:ff"}
        )

    async def test_set_name(self, client, mock_session):
        r = await client.put(
            "/devices/aa:bb:cc:dd:ee:ff/name",
            json={"name": "MyPC", "source": "user"},
        )
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices.Device", "setName", {"name": "MyPC", "source": "user"}
        )

    async def test_set_name_validation(self, client):
        r = await client.put("/devices/aa:bb:cc:dd:ee:ff/name", json={})
        assert r.status_code == 422

    async def test_add_name(self, client, mock_session):
        r = await client.post(
            "/devices/aa:bb:cc:dd:ee:ff/name",
            json={"name": "AltName", "source": "user"},
        )
        assert r.status_code == 200

    async def test_remove_name(self, client, mock_session):
        r = await client.delete("/devices/aa:bb:cc:dd:ee:ff/name?source=user")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices.Device", "removeName", {"source": "user"}
        )

    async def test_set_type(self, client, mock_session):
        r = await client.put(
            "/devices/aa:bb:cc:dd:ee:ff/type",
            json={"type": "Computer", "source": "user"},
        )
        assert r.status_code == 200

    async def test_has_tag(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": True}
        r = await client.get("/devices/aa:bb:cc:dd:ee:ff/tags/printer")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices.Device", "hasTag", {"tag": "printer"}
        )

    async def test_set_tag(self, client, mock_session):
        r = await client.put(
            "/devices/aa:bb:cc:dd:ee:ff/tags/printer", json={}
        )
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices.Device", "setTag", {"expression": "", "traverse": "", "tag": "printer"}
        )

    async def test_clear_tag(self, client, mock_session):
        r = await client.delete("/devices/aa:bb:cc:dd:ee:ff/tags/printer")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Devices.Device", "clearTag", {"tag": "printer"}
        )

    async def test_not_found(self, client, mock_session):
        from tests.conftest import not_found
        mock_session.call.side_effect = not_found()
        r = await client.get("/devices/nonexistent")
        assert r.status_code == 404

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/devices")
        assert r.status_code == 403
