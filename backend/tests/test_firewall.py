import pytest


class TestFirewallLevel:
    async def test_get_level(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {"level": "Medium"}}
        r = await client.get("/firewall/level")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("Firewall", "getFirewallLevel", {})

    async def test_set_level(self, client, mock_session):
        r = await client.put("/firewall/level", json={"level": "High"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Firewall", "setFirewallLevel", {"level": "High"}
        )

    async def test_set_level_validation(self, client):
        r = await client.put("/firewall/level", json={})
        assert r.status_code == 422

    async def test_get_ipv6_level(self, client, mock_session):
        r = await client.get("/firewall/ipv6-level")
        assert r.status_code == 200

    async def test_commit(self, client, mock_session):
        r = await client.post("/firewall/commit")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("Firewall", "commit", {})


class TestFirewallPing:
    async def test_get_ping(self, client, mock_session):
        r = await client.get("/firewall/ping/wan")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Firewall", "getRespondToPing", {"sourceInterface": "wan"}
        )

    async def test_set_ping(self, client, mock_session):
        r = await client.put("/firewall/ping/wan", json={"service_enable": True})
        assert r.status_code == 200


class TestPortForwarding:
    async def test_get_all(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": []}
        r = await client.get("/firewall/port-forwarding")
        assert r.status_code == 200

    async def test_create(self, client, mock_session):
        body = {
            "origin": "webui",
            "source_interface": "data",
            "internal_port": 80,
            "destination_ip_address": "192.168.1.10",
            "protocol": "TCP",
        }
        r = await client.post("/firewall/port-forwarding", json=body)
        assert r.status_code == 200

    async def test_create_validation(self, client):
        r = await client.post("/firewall/port-forwarding", json={})
        assert r.status_code == 422

    async def test_delete(self, client, mock_session):
        r = await client.delete("/firewall/port-forwarding/rule1?origin=webui")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "Firewall", "deletePortForwarding", {"id": "rule1", "origin": "webui"}
        )

    async def test_enable(self, client, mock_session):
        r = await client.patch(
            "/firewall/port-forwarding/rule1/enable",
            json={"origin": "webui", "enable": True},
        )
        assert r.status_code == 200

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/firewall/port-forwarding")
        assert r.status_code == 403


class TestDMZ:
    async def test_get_dmz(self, client, mock_session):
        r = await client.get("/firewall/dmz")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("Firewall", "getDMZ", {})

    async def test_create_dmz(self, client, mock_session):
        body = {
            "source_interface": "data",
            "destination_ip_address": "192.168.1.50",
            "enable": True,
        }
        r = await client.post("/firewall/dmz", json=body)
        assert r.status_code == 200

    async def test_delete_dmz(self, client, mock_session):
        r = await client.delete("/firewall/dmz/dmz1")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("Firewall", "deleteDMZ", {"id": "dmz1"})
