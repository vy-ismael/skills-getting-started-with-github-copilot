from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect some known activity keys
    assert "Soccer Team" in data


def test_signup_and_unregister_flow():
    activity = "Soccer Team"
    email = "test.student@example.com"

    # Ensure not present initially
    res = client.get("/activities")
    assert res.status_code == 200
    participants = res.json()[activity]["participants"]
    if email in participants:
        # cleanup if previous run left the email registered
        client.delete(f"/activities/{quote(activity)}/unregister?email={quote(email)}")

    # Signup
    signup_res = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert signup_res.status_code == 200
    assert "Signed up" in signup_res.json().get("message", "")

    # Verify participant present
    res_after = client.get("/activities")
    assert res_after.status_code == 200
    participants_after = res_after.json()[activity]["participants"]
    assert email in participants_after

    # Unregister
    unregister_res = client.delete(f"/activities/{quote(activity)}/unregister?email={quote(email)}")
    assert unregister_res.status_code == 200
    assert "Unregistered" in unregister_res.json().get("message", "")

    # Verify removed
    res_final = client.get("/activities")
    participants_final = res_final.json()[activity]["participants"]
    assert email not in participants_final
