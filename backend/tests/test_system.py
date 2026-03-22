import pytest


class TestDiagnostics:
    async def test_list_diagnostics(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": []}
        r = await client.get("/system/diagnostics")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("AutoDiag", "listDiagnostics", {})

    async def test_get_diagnostics_state(self, client, mock_session):
        r = await client.get("/system/diagnostics/state")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("AutoDiag", "getDiagnosticsState", {})

    async def test_execute_diagnostics(self, client, mock_session):
        r = await client.post("/system/diagnostics/ping")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "AutoDiag", "executeDiagnostics", {"id": "ping"}
        )

    async def test_execute_diagnostics_with_usr(self, client, mock_session):
        r = await client.post("/system/diagnostics/ping", json={"usr": True})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "AutoDiag", "executeDiagnostics", {"id": "ping", "usr": True}
        )

    async def test_cancel_diagnostics(self, client, mock_session):
        r = await client.delete("/system/diagnostics/ping")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "AutoDiag", "cancelDiagnostics", {"id": "ping"}
        )

    async def test_execute_trigger(self, client, mock_session):
        r = await client.post("/system/diagnostics/trigger", json={"event": "WanUp"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "AutoDiag", "executeTrigger", {"event": "WanUp"}
        )

    async def test_execute_trigger_validation(self, client):
        r = await client.post("/system/diagnostics/trigger", json={})
        assert r.status_code == 422

    async def test_get_datamodel_whitelist(self, client, mock_session):
        r = await client.get("/system/diagnostics/whitelist/datamodel")
        assert r.status_code == 200

    async def test_get_function_whitelist(self, client, mock_session):
        r = await client.get("/system/diagnostics/whitelist/function")
        assert r.status_code == 200

    async def test_get_context(self, client, mock_session):
        r = await client.get("/system/diagnostics/context")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("AutoDiag", "getContext", {})

    async def test_clear_context(self, client, mock_session):
        r = await client.delete("/system/diagnostics/context")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("AutoDiag", "clearContext", {})

    async def test_set_user_input(self, client, mock_session):
        r = await client.post("/system/diagnostics/input", json={"input": "yes"})
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with(
            "AutoDiag", "setUserInput", {"input": "yes"}
        )


class TestDNS:
    async def test_get_dns_servers(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": []}
        r = await client.get("/system/dns")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("DNS", "getDNSServers", {})

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/system/diagnostics")
        assert r.status_code == 403
