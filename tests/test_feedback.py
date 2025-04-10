import pytest
from fastapi.testclient import TestClient
from app import app
import json
import os

client = TestClient(app)

def test_submit_feedback():
    feedback_data = {
        "feedback_type": "bug",
        "title": "Test Bug",
        "description": "This is a test bug report",
        "severity": "medium",
        "reproduction_steps": "1. Do this\n2. Do that",
        "expected_behavior": "Should work",
        "actual_behavior": "Doesn't work"
    }
    
    response = client.post("/api/v1/feedback", json=feedback_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "feedback_id" in data

def test_get_feedback_summary():
    response = client.get("/api/v1/feedback/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "feedback" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["feedback"], list)

def test_invalid_feedback():
    invalid_data = {
        "feedback_type": "invalid_type",
        "title": "",
        "description": ""
    }
    
    response = client.post("/api/v1/feedback", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_feedback_storage():
    # Test that feedback is actually stored
    feedback_dir = "logs/feedback"
    assert os.path.exists(feedback_dir)
    
    feedback_files = [f for f in os.listdir(feedback_dir) if f.endswith('.json')]
    assert len(feedback_files) > 0
    
    # Check content of a feedback file
    with open(os.path.join(feedback_dir, feedback_files[0]), 'r') as f:
        feedback_data = json.load(f)
        assert "timestamp" in feedback_data
        assert "title" in feedback_data
        assert "description" in feedback_data 