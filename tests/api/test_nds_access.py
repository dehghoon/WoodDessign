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


def test_verified_simple_beam_request_runs_the_same_engine(monkeypatch):
    from test_nds2024 import fixture
    monkeypatch.setattr('wooddessign.api.tool_auth.verify_access',lambda _:(200,'test-verified'))
    payload=dict(method='ASD',duration='normal',span_in=120,width_in=2,depth_in=12,
        beam_effective_length_in=120,combination_udl_lbf_per_in=10,total_sls_udl_lbf_per_in=8,
        live_sls_udl_lbf_per_in=4,bearing_length_in=3,total_limit_divisor=240,live_limit_divisor=360,
        material=fixture()['material'],engineer_confirmed_inputs_and_factors=True)
    response=TestClient(app).post('/api/v1/nds2024/simple-beam',json=payload)
    assert response.status_code==200
    result=response.json()
    assert result['analysis']['reaction_each_lbf']==600
    assert result['whole_member_status']=='not-checked'
    assert result['engineering_approval'] is False
    assert all('status' in check for check in result['checks'])
