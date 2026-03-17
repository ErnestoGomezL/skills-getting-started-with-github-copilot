import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function():
    global _activities_backup
    _activities_backup = copy.deepcopy(activities)


def teardown_function():
    activities.clear()
    activities.update(_activities_backup)


def test_root_redirects_to_static_index():
    resp = client.get("/")
    assert resp.status_code in (200, 307, 308)
    if resp.status_code in (307, 308):
        assert resp.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    email = "newstudent@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_not_found():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_signup_for_activity_full():
    activities["Chess Club"]["max_participants"] = len(activities["Chess Club"]["participants"])
    resp = client.post("/activities/Chess Club/signup", params={"email": "newstudent2@mergington.edu"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Activity is full"


def test_remove_participant_success():
    email = activities["Chess Club"]["participants"][0]
    resp = client.delete("/activities/Chess Club/participants", params={"email": email})
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found():
    resp = client.delete("/activities/Chess Club/participants", params={"email": "nobody@mergington.edu"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found in this activity"
