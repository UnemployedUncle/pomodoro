import os

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_pure_focus.db"

from app.main import app  # noqa: E402


client = TestClient(app)


def login():
    response = client.post("/auth/demo-login")
    assert response.status_code == 200


def test_demo_login_and_seeded_cycles():
    login()
    me_response = client.get("/me")
    assert me_response.status_code == 200
    cycles_response = client.get("/cycles")
    assert cycles_response.status_code == 200
    items = cycles_response.json()["items"]
    assert any(item["name"] == "sample cycle 1" and item["owned"] for item in items)
    assert any(item["name"] == "sample cycle 2" and not item["owned"] for item in items)


def test_focus_completion_and_reward_flow():
    login()
    cycles = client.get("/cycles").json()["items"]
    owned_cycle = [item for item in cycles if item["owned"]][0]
    run_response = client.post("/runs", json={
        "cycle_blueprint_id": owned_cycle["id"],
        "cycle_mode": "owned",
    })
    assert run_response.status_code == 200
    run_id = run_response.json()["runId"]

    for node in owned_cycle["focusNodes"]:
        focus_response = client.post(
            f"/runs/{run_id}/focus-complete",
            json={
                "focus_order": node["nodeOrder"],
                "checked_todos": ["ship mvp"],
                "remaining_nottodos": ["social feed"],
            },
        )
        assert focus_response.status_code == 200

    complete_response = client.post(f"/runs/{run_id}/complete")
    assert complete_response.status_code == 200
    reward_response = client.post(f"/rewards/{run_id}/claim-cycle")
    assert reward_response.status_code == 200
    collection_response = client.get("/collection")
    assert collection_response.status_code == 200
    assert collection_response.json()["items"]


def test_index_contains_three_tab_shell():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "Pure Focus" in html
    assert 'data-view-target="timer"' in html
    assert 'data-view-target="dashboard"' in html
    assert 'data-view-target="setting"' in html
    assert 'data-view-target="collection"' not in html
    assert "material-symbols-outlined" not in html
