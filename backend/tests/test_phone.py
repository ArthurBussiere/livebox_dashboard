import pytest


class TestPhone:
    async def test_get_voip_config(self, client, mock_session):
        mock_session.call.return_value = {"status": 0, "data": {}}
        r = await client.get("/phone/config")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("NMC", "getVoIPConfig", {})

    async def test_get_voip_info(self, client, mock_session):
        r = await client.get("/phone/info")
        assert r.status_code == 200
        mock_session.call.assert_awaited_once_with("VoiceService", "get", {})

    async def test_permission_denied(self, client, mock_session):
        from tests.conftest import permission_denied
        mock_session.call.side_effect = permission_denied()
        r = await client.get("/phone/config")
        assert r.status_code == 403
