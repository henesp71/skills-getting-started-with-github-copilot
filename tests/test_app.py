"""
Unit tests for FastAPI application using AAA (Arrange-Act-Assert) pattern
"""

import pytest
from fastapi import HTTPException
from copy import deepcopy
from src.app import get_activities, signup_for_activity, unregister_from_activity, activities as original_activities


@pytest.fixture
def reset_activities():
    """
    Reset activities to initial state before each test to ensure isolation.
    This prevents test interdependency and ensures clean test state.
    """
    original_state = deepcopy(original_activities)
    yield
    # Restore original state after test
    original_activities.clear()
    original_activities.update(original_state)


class TestGetActivities:
    """Tests for get_activities() endpoint"""

    def test_get_activities_returns_all_activities(self, reset_activities):
        """
        Test that get_activities returns all 9 activities with correct structure
        
        Arrange: Access the activities data
        Act: Call get_activities()
        Assert: Verify 9 activities returned with expected structure
        """
        # Arrange: No setup needed - activities are pre-loaded

        # Act
        result = get_activities()

        # Assert
        assert len(result) == 9, "Should have 9 activities"
        assert "Chess Club" in result, "Chess Club should be present"
        assert "Programming Class" in result, "Programming Class should be present"
        assert "Gym Class" in result, "Gym Class should be present"
        assert "Basketball Team" in result, "Basketball Team should be present"
        assert "Soccer Club" in result, "Soccer Club should be present"
        assert "Drama Club" in result, "Drama Club should be present"
        assert "Art Club" in result, "Art Club should be present"
        assert "Debate Club" in result, "Debate Club should be present"
        assert "Science Club" in result, "Science Club should be present"

        # Verify structure of each activity
        for activity_name, activity_data in result.items():
            assert "description" in activity_data, f"{activity_name} should have description"
            assert "schedule" in activity_data, f"{activity_name} should have schedule"
            assert "max_participants" in activity_data, f"{activity_name} should have max_participants"
            assert "participants" in activity_data, f"{activity_name} should have participants list"
            assert isinstance(activity_data["participants"], list), f"{activity_name} participants should be a list"


class TestSignupForActivity:
    """Tests for signup_for_activity() endpoint"""

    def test_signup_for_activity_success(self, reset_activities):
        """
        Test successful signup adds participant to activity
        
        Arrange: Set up activity name and email
        Act: Call signup_for_activity()
        Assert: Verify participant added to activity
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "john.doe@mergington.edu"
        initial_count = len(original_activities[activity_name]["participants"])

        # Act
        result = signup_for_activity(activity_name, email)

        # Assert
        assert result["message"] == f"Signed up {email} for {activity_name}"
        assert email in original_activities[activity_name]["participants"], "Email should be added to participants"
        assert len(original_activities[activity_name]["participants"]) == initial_count + 1, "Participant count should increase by 1"

    def test_signup_for_activity_duplicate_signup(self, reset_activities):
        """
        Test that duplicate signup prevents the same student from signing up twice
        
        Arrange: Sign up student once, then attempt to sign up again
        Act: Call signup_for_activity() with same email
        Assert: Verify HTTPException raised with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(activity_name, email)
        
        assert exc_info.value.status_code == 400
        assert "already signed up" in exc_info.value.detail.lower()

    def test_signup_for_activity_nonexistent_activity(self, reset_activities):
        """
        Test that signup for non-existent activity raises 404 error
        
        Arrange: Use non-existent activity name
        Act: Call signup_for_activity() with invalid activity name
        Assert: Verify HTTPException raised with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(activity_name, email)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestUnregisterFromActivity:
    """Tests for unregister_from_activity() endpoint"""

    def test_unregister_from_activity_success(self, reset_activities):
        """
        Test successful unregister removes participant from activity
        
        Arrange: Use activity with existing participant
        Act: Call unregister_from_activity() with enrolled student
        Assert: Verify participant removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        initial_count = len(original_activities[activity_name]["participants"])

        # Act
        result = unregister_from_activity(activity_name, email)

        # Assert
        assert result["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in original_activities[activity_name]["participants"], "Email should be removed from participants"
        assert len(original_activities[activity_name]["participants"]) == initial_count - 1, "Participant count should decrease by 1"

    def test_unregister_from_activity_not_enrolled(self, reset_activities):
        """
        Test that unregister fails when student is not enrolled
        
        Arrange: Use student not signed up for activity
        Act: Call unregister_from_activity() with non-enrolled student
        Assert: Verify HTTPException raised with appropriate error message
        """
        # Arrange
        activity_name = "Basketball Team"  # No participants initially
        email = "notEnrolled@mergington.edu"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity(activity_name, email)

        assert exc_info.value.status_code == 400
        assert "not signed up" in exc_info.value.detail.lower()

    def test_unregister_from_activity_nonexistent_activity(self, reset_activities):
        """
        Test that unregister from non-existent activity raises 404 error
        
        Arrange: Use non-existent activity name
        Act: Call unregister_from_activity() with invalid activity name
        Assert: Verify HTTPException raised with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity(activity_name, email)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
