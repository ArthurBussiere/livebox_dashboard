import pytest


class TestWifi:
    async def test_get_wifi(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {"Enable": True}}
        r = await client.get("/wifi")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC.Wifi", "get", {})

    async def test_set_wifi(self, client, mock_session):
        r = await client.put("/wifi", json={"enable": True})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.Wifi", "set", {"enable": True}
        )

    async def test_set_wifi_validation(self, client):
        r = await client.put("/wifi", json={})
        assert r.status_code == 422

    async def test_set_enable(self, client, mock_session):
        r = await client.patch("/wifi/enable", json={"value": False})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.Wifi", "setEnable", {"value": False}
        )

    async def test_toggle_enable(self, client, mock_session):
        r = await client.post("/wifi/enable/toggle")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC.Wifi", "toggleEnable", {})

    async def test_get_stats(self, client, mock_session):
        r = await client.get("/wifi/stats")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC.Wifi", "getStats", {})

    async def test_auto_channel(self, client, mock_session):
        r = await client.post("/wifi/channel/auto")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.Wifi", "startAutoChannelSelection", {}
        )

    async def test_start_pairing(self, client, mock_session):
        r = await client.post("/wifi/pairing/start", json={"client_pin": "12345678"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.Wifi", "startPairing", {"clientPIN": "12345678"}
        )

    async def test_stop_pairing(self, client, mock_session):
        r = await client.post("/wifi/pairing/stop")
        assert r.status_code == 200

    async def test_generate_wps_pin(self, client, mock_session):
        r = await client.post("/wifi/wps/pin")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC.Wifi.WPS", "generateSelfPIN", {})

    async def test_get_guest(self, client, mock_session):
        r = await client.get("/wifi/guest")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC.Guest", "get", {})

    async def test_set_guest(self, client, mock_session):
        r = await client.put("/wifi/guest", json={"enable": True})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.Guest", "set", {"Enable": True}
        )

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/wifi")
        assert r.status_code == 403
