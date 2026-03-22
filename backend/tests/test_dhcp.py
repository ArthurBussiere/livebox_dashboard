import pytest


class TestDHCP:
    async def test_get_leases(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": []}
        r = await client.get("/dhcp/leases")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DHCPv4.Server.Pool.default", "getLeases", {})

    async def test_get_static_leases(self, client, mock_session):
        r = await client.get("/dhcp/leases/static")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server.Pool.default", "getStaticLeases", {}
        )

    async def test_add_static_lease(self, client, mock_session):
        body = {"mac_address": "aa:bb:cc:dd:ee:ff", "ip_address": "192.168.1.50"}
        r = await client.post("/dhcp/leases/static", json=body)
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server.Pool.default",
            "addStaticLease",
            {"MACAddress": "aa:bb:cc:dd:ee:ff", "IPAddress": "192.168.1.50"},
        )

    async def test_add_static_lease_validation(self, client):
        r = await client.post("/dhcp/leases/static", json={})
        assert r.status_code == 422

    async def test_update_static_lease(self, client, mock_session):
        r = await client.put(
            "/dhcp/leases/static/aa:bb:cc:dd:ee:ff",
            json={"ip_address": "192.168.1.51"},
        )
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server.Pool.default",
            "setStaticLease",
            {"MACAddress": "aa:bb:cc:dd:ee:ff", "IPAddress": "192.168.1.51"},
        )

    async def test_delete_static_lease(self, client, mock_session):
        r = await client.delete("/dhcp/leases/static/aa:bb:cc:dd:ee:ff")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server.Pool.default",
            "deleteStaticLease",
            {"MACAddress": "aa:bb:cc:dd:ee:ff"},
        )

    async def test_renew_lease(self, client, mock_session):
        r = await client.post("/dhcp/leases/static/aa:bb:cc:dd:ee:ff/renew")
        assert r.status_code == 200

    async def test_set_lease_time(self, client, mock_session):
        r = await client.put("/dhcp/lease-time", json={"lease_time": 86400})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server.Pool.default", "setLeaseTime", {"leasetime": 86400}
        )

    async def test_create_pool(self, client, mock_session):
        r = await client.post("/dhcp/pool", json={"name": "default", "interface": "lan"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server",
            "createPool",
            {"name": "default", "interface": "lan"},
        )

    async def test_get_dora_cycles(self, client, mock_session):
        r = await client.get("/dhcp/stats/dora")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DHCPv4.Server.Stats", "getDoraCyclesDetails", {}
        )

    async def test_clear_stats(self, client, mock_session):
        r = await client.delete("/dhcp/stats")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DHCPv4.Server", "clearStatistics", {})

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/dhcp/leases")
        assert r.status_code == 403
