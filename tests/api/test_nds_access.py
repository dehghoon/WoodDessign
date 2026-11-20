from fastapi.testclient import TestClient
from wooddessign.api.app import app


def test_anonymous_direct_routes_are_denied_before_calculation():
    client=TestClient(app)
    for route in ['calculate','nds2024/member-check','nds2024/simple-beam']:
        response=client.post('/api/v1/'+route,json={})
        assert response.status_code==401
        assert response.headers['cache-control']=='no-store'


def test_verified_caller_must_supply_valid_engineering_inputs(monkeypatch):
    monkeypatch.setattr('wooddessign.api.tool_auth.verify_access',lambda _:(200,'test-verified'))
    response=TestClient(app).post('/api/v1/nds2024/simple-beam',json={})
    assert response.status_code==422
