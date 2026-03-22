import pytest


class TestDynDNS:
    async def test_get_hosts(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": []}
        r = await client.get("/dyndns")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DynDNS", "getHosts", {})

    async def test_add_host(self, client, mock_session):
        body = {
            "service": "dyndns.org",
            "hostname": "myhome.dyndns.org",
            "username": "user",
            "password": "pass",
        }
        r = await client.post("/dyndns", json=body)
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DynDNS",
            "addHost",
            {
                "service": "dyndns.org",
                "hostname": "myhome.dyndns.org",
                "username": "user",
                "password": "pass",
                "enable": True,
            },
        )

    async def test_add_host_validation(self, client):
        r = await client.post("/dyndns", json={})
        assert r.status_code == 422

    async def test_delete_host(self, client, mock_session):
        r = await client.delete("/dyndns/myhome.dyndns.org")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DynDNS", "delHost", {"hostname": "myhome.dyndns.org"}
        )

    async def test_get_services(self, client, mock_session):
        r = await client.get("/dyndns/services")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DynDNS", "getServices", {})

    async def test_get_global_enable(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {"enable": False}}
        r = await client.get("/dyndns/enable")
        assert r.status_code == 200

    async def test_set_global_enable(self, client, mock_session):
        r = await client.patch("/dyndns/enable", json={"enable": True})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DynDNS", "setGlobalEnable", {"enable": True}
        )

    async def test_get_cgnat(self, client, mock_session):
        r = await client.get("/dyndns/cgnat")
        assert r.status_code == 200

    async def test_set_cgnat(self, client, mock_session):
        r = await client.patch("/dyndns/cgnat", json={"enable": False})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "DynDNS", "setEnableOnCgnat", {"value": False}
        )

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/dyndns")
        assert r.status_code == 403
