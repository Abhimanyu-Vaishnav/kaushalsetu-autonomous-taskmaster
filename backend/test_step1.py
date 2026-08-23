import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add backend dir to sys path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from agent_engine import generate_assessment, AssessmentSchema

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("[OK] Health check passed")

def test_generate_assessment_mocked():
    mock_response_data = {
        "exam_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Automotive Electronics Repair Assessment",
        "mcqs": [
            {
                "question": "What is the primary function of a multimeter in automotive diagnostics?",
                "options": [
                    "Measure voltage, current, and resistance",
                    "Replace blown fuses",
                    "Recharge car batteries",
                    "Scan ECU fault codes directly"
                ],
                "correct_option": 0
            },
            {
                "question": "Which component protects electrical circuits from overcurrent?",
                "options": ["Relay", "Fuse", "Diode", "Transistor"],
                "correct_option": 1
            },
            {
                "question": "What does CAN stand for in vehicle networking?",
                "options": [
                    "Controller Area Network",
                    "Central Automotive Node",
                    "Car Automation Network",
                    "Computer Access Node"
                ],
                "correct_option": 0
            }
        ],
        "practical_task": "Diagnose an intermittent headlight failure on a test vehicle using a multimeter and circuit diagram.",
        "grading_rubric": [
            "Correct safety procedures followed before testing",
            "Accurate identification of circuit fault location using voltage drop measurement",
            "Proper documentation of repair procedure and wire repair standard compliance"
        ]
    }
    
    # Verify Pydantic schema validation directly
    validated = AssessmentSchema(**mock_response_data)
    assert len(validated.mcqs) == 3
    assert len(validated.grading_rubric) == 3
    print("[OK] AssessmentSchema Pydantic validation passed")

    with patch("main.generate_assessment") as mock_gen:
        mock_gen.return_value = mock_response_data
        
        response = client.post(
            "/api/assessment/generate",
            json={"topic": "Automotive Electronics", "difficulty": "Intermediate"}
        )
        if response.status_code != 200:
            print("Response error:", response.status_code, response.text)
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        assert res_json["data"]["title"] == "Automotive Electronics Repair Assessment"
        assert len(res_json["data"]["mcqs"]) == 3
        assert len(res_json["data"]["grading_rubric"]) == 3
        print("[OK] API Endpoint test passed with valid JSON output structure")
        return res_json["data"]

if __name__ == "__main__":
    test_health()
    sample_output = test_generate_assessment_mocked()
    print("\n--- SAMPLE GENERATED ASSESSMENT JSON ---")
    import json
    print(json.dumps(sample_output, indent=2))
