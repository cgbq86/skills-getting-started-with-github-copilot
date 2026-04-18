import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    """Test the root endpoint redirect"""
    
    def test_root_redirects_to_static_index(self):
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Music Club",
            "Debate Club",
            "Science Club",
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert set(data.keys()) == set(expected_activities)
        assert all("description" in data[activity] for activity in expected_activities)
        assert all("schedule" in data[activity] for activity in expected_activities)
        assert all("max_participants" in data[activity] for activity in expected_activities)
        assert all("participants" in data[activity] for activity in expected_activities)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]
    
    def test_signup_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRemoveParticipant:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        assert email not in client.get("/activities").json()[activity_name]["participants"]
    
    def test_remove_nonexistent_participant_returns_404(self):
        # Arrange
        activity_name = "Basketball Team"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_from_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
