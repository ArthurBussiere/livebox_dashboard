import pytest


class TestNMCCore:
    async def test_get_nmc(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {}}
        r = await client.get("/nmc")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC", "get", {})

    async def test_set_nmc(self, client, mock_session):
        r = await client.put("/nmc", json={"SomeParam": "value"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC", "set", {"SomeParam": "value"})


class TestNMCSystemControl:
    async def test_reboot(self, client, mock_session):
        r = await client.post("/nmc/reboot", json={"reason": "maintenance"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC", "reboot", {"reason": "maintenance"}
        )

    async def test_reset(self, client, mock_session):
        r = await client.post("/nmc/reset", json={"reason": "factory reset"})
        assert r.status_code == 200

    async def test_shutdown(self, client, mock_session):
        r = await client.post("/nmc/shutdown", json={"reason": "maintenance"})
        assert r.status_code == 200


class TestNMCWan:
    async def test_get_wan_status(self, client, mock_session):
        r = await client.get("/nmc/wan/status")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC", "getWANStatus", {})

    async def test_get_wan_modes(self, client, mock_session):
        r = await client.get("/nmc/wan/modes")
        assert r.status_code == 200

    async def test_set_wan_mode(self, client, mock_session):
        body = {"wan_mode": "FTTH", "username": "user@isp", "password": "pass"}
        r = await client.put("/nmc/wan/mode", json=body)
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC",
            "setWanMode",
            {"WanMode": "FTTH", "Username": "user@isp", "Password": "pass"},
        )

    async def test_set_wan_mode_validation(self, client):
        r = await client.put("/nmc/wan/mode", json={})
        assert r.status_code == 422


class TestNMCLanIP:
    async def test_get_lan_ip(self, client, mock_session):
        r = await client.get("/nmc/lan-ip")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC", "getLANIP", {})

    async def test_set_lan_ip(self, client, mock_session):
        body = {
            "address": "192.168.1.1",
            "netmask": "255.255.255.0",
            "dhcp_enable": True,
            "dhcp_min_address": "192.168.1.100",
            "dhcp_max_address": "192.168.1.200",
            "lease_time": 86400,
        }
        r = await client.put("/nmc/lan-ip", json=body)
        assert r.status_code == 200


class TestNMCIPv6:
    async def test_get_ipv6(self, client, mock_session):
        r = await client.get("/nmc/ipv6")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC.IPv6", "get", {})

    async def test_set_ipv6(self, client, mock_session):
        r = await client.put("/nmc/ipv6", json={"enable": True})
        assert r.status_code == 200


class TestNMCFirmware:
    async def test_check_upgrades(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": False}
        r = await client.get("/nmc/firmware/check")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC", "checkForUpgrades", {})

    async def test_update_version_info(self, client, mock_session):
        r = await client.post("/nmc/firmware/version")
        assert r.status_code == 200


class TestNMCLed:
    async def test_get_led(self, client, mock_session):
        r = await client.get("/nmc/led/power")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.LED", "getLedStatus", {"name": "power"}
        )

    async def test_set_led(self, client, mock_session):
        r = await client.put("/nmc/led/power", json={"state": "on", "color": "green"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.LED",
            "setLed",
            {"name": "power", "state": "on", "color": "green"},
        )


class TestNMCWlanTimer:
    async def test_get_timer(self, client, mock_session):
        r = await client.get("/nmc/wlan-timer/wl0")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.WlanTimer", "getActivationTimer", {"InterfaceName": "wl0"}
        )

    async def test_set_timer(self, client, mock_session):
        r = await client.put("/nmc/wlan-timer/wl0", json={"timeout": 3600})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.WlanTimer",
            "setActivationTimer",
            {"InterfaceName": "wl0", "Timeout": 3600},
        )

    async def test_delete_timer(self, client, mock_session):
        r = await client.delete("/nmc/wlan-timer/wl0")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "NMC.WlanTimer", "disableActivationTimer", {"InterfaceName": "wl0"}
        )

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/nmc")
        assert r.status_code == 403
