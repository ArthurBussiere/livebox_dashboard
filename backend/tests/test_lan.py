import pytest


class TestLan:
    async def test_get_status(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {"Status": "Up"}}
        r = await client.get("/lan/status")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("HomeLan", "getStatus", {})

    async def test_get_interfaces(self, client, mock_session):
        r = await client.get("/lan/interfaces")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("HomeLan", "getInterfacesNames", {})

    async def test_get_devices(self, client, mock_session):
        r = await client.get("/lan/devices")
        assert r.status_code == 200

    async def test_get_devices_status(self, client, mock_session):
        r = await client.get("/lan/devices/status")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("HomeLan", "getDevicesStatus", {})

    async def test_get_wan_counters(self, client, mock_session):
        r = await client.get("/lan/wan-counters")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("HomeLan", "getWANCounters", {})

    async def test_get_saturation(self, client, mock_session):
        r = await client.get("/lan/saturation")
        assert r.status_code == 200

    async def test_add_device(self, client, mock_session):
        r = await client.post("/lan/devices/aa:bb:cc:dd:ee:ff")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "HomeLan", "addDevice", {"macaddress": "aa:bb:cc:dd:ee:ff"}
        )

    async def test_delete_device(self, client, mock_session):
        r = await client.delete("/lan/devices/aa:bb:cc:dd:ee:ff")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "HomeLan", "deleteDevice", {"macaddress": "aa:bb:cc:dd:ee:ff"}
        )

    async def test_start_interface_monitoring(self, client, mock_session):
        r = await client.post(
            "/lan/monitoring/interface/start", json={"duration": 60, "interval": 5}
        )
        assert r.status_code == 200

    async def test_stop_interface_monitoring(self, client, mock_session):
        r = await client.post("/lan/monitoring/interface/stop")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "HomeLan", "stopInterfaceMonitoringTest", {}
        )

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/lan/status")
        assert r.status_code == 403
