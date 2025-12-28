"""Tests for the activities endpoints."""

import pytest


def test_get_activities(client):
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_activity_structure(client):
    """Test that activities have the correct structure."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity(client):
    """Test signing up for an activity."""
    email = "test.student@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate_participant(client):
    """Test that duplicate signups are rejected."""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity."""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_unregister_from_activity(client):
    """Test unregistering from an activity."""
    email = "test.unregister@mergington.edu"
    activity = "Chess Club"
    
    # First sign up
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant(client):
    """Test unregistering a participant that doesn't exist."""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from a non-existent activity."""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_root_redirect(client):
    """Test that root path redirects to static index."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_participants_exist(client):
    """Test that initial participants are loaded."""
    response = client.get("/activities")
    data = response.json()
    
    # Check that some activities have initial participants
    assert len(data["Chess Club"]["participants"]) > 0
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


def test_max_participants_limit(client):
    """Test activity participant limits."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_data in data.items():
        # Verify that current participants don't exceed max
        assert len(activity_data["participants"]) <= activity_data["max_participants"]
