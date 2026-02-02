import copy

from fastapi.testclient import TestClient

from src import app as appmod


client = TestClient(appmod.app)

# Keep a pristine copy of the initial in-memory activities so tests can reset state
_INITIAL_ACTIVITIES = copy.deepcopy(appmod.activities)


def setup_function():
    # Reset the in-memory activities between tests
    appmod.activities.clear()
    appmod.activities.update(copy.deepcopy(_INITIAL_ACTIVITIES))


def test_get_activities_returns_200_and_contains_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_adds_participant_and_prevents_duplicates():
    email = "pytest_student@mergington.edu"
    # signup
    resp = client.post(f"/activities/Basketball/signup?email={email}")
    assert resp.status_code == 200
    assert email in appmod.activities["Basketball"]["participants"]

    # signing up again returns 400
    resp2 = client.post(f"/activities/Basketball/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_removes_participant_and_handles_missing():
    email = "temp_remove@mergington.edu"
    # add first
    resp = client.post(f"/activities/Basketball/signup?email={email}")
    assert resp.status_code == 200
    assert email in appmod.activities["Basketball"]["participants"]

    # remove
    resp2 = client.delete(f"/activities/Basketball/participants?email={email}")
    assert resp2.status_code == 200
    assert email not in appmod.activities["Basketball"]["participants"]

    # removing again returns 404
    resp3 = client.delete(f"/activities/Basketball/participants?email={email}")
    assert resp3.status_code == 404


def test_signup_nonexistent_activity_returns_404():
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404
