import sys
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import get_institute, get_all_students, add_student, get_student_by_id

client = TestClient(app)

def test_enterprise_schema():
    # 1. Test Institute Schema & Config
    inst = get_institute()
    assert inst["code"] == "SKILLFORGE-HQ"
    assert inst["placement_threshold"] == 70
    assert inst["max_interviews_cap"] == 3
    print("[OK] Enterprise Schema: Institute model verified with code SKILLFORGE-HQ")
    
    # 2. Test Student Schema & Consent Flag
    students = get_all_students()
    assert len(students) >= 4
    alex = get_student_by_id("STU-1001")
    assert alex["branch_name"] == "Nangloi Center"
    assert alex["consent_for_job_dispatch"] == 1
    print("[OK] Enterprise Schema: Student model & consent flag verified")
    
    # 3. Test API Health
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "3.5.0"
    print("[OK] FastAPI v3.5.0 Enterprise Health verified")
    
    # 4. Test Verification Gate & Placement Dispatch
    mock_eval = {
        "total_score": 85,
        "strengths": ["Safety protocol followed", "Oscilloscope waveform isolation accurate"],
        "skill_gaps": ["None"],
        "placement_ready": True,
        "recruiter_pitch": "Alex Mercer demonstrates exceptional technical diagnostic proficiency.",
        "fast_screening": {
            "passed_screening": True,
            "found_tokens": ["safety", "procedure"],
            "missing_tokens": [],
            "structure_score": 85
        }
    }
    
    with patch("agent_engine.evaluate_submission") as mock_eval_fn:
        mock_eval_fn.return_value = mock_eval
        
        pipe_res = client.post(
            "/api/student/evaluate-and-dispatch",
            json={
                "student_id": "STU-1001",
                "assessment_id": "ASS-DEFAULT",
                "practical_task": "Diagnose CAN bus hardware fault.",
                "grading_rubric": ["Safety lockout", "Waveform check"],
                "submission_text": "Completed safety lockout and waveform diagnostic check."
            }
        )
        assert pipe_res.status_code == 200
        data = pipe_res.json()["data"]
        assert data["dispatch"]["status"] == "APPLIED_AND_DISPATCHED"
        assert "notifications" in data["dispatch"]
        print("[OK] Enterprise Autonomous Placement Verification Gate & Dispatch verified")

if __name__ == "__main__":
    test_enterprise_schema()
