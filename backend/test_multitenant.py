import sys
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import get_institute, get_all_students, add_student

client = TestClient(app)

def test_multi_tenant_architecture():
    # 1. Test Institute Info
    inst = get_institute()
    assert inst["id"] == "INST-GLOBAL-01"
    assert len(inst["branches"]) >= 3
    print("[OK] Multi-Tenant DB: Institute & Branches verified")
    
    # 2. Test Roster & Student Add
    students = get_all_students()
    assert len(students) >= 4
    print("[OK] Multi-Tenant DB: Student roster verified with", len(students), "candidates")
    
    # 3. Test API Config Endpoint
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "3.0.0"
    print("[OK] Multi-Tenant FastAPI v3.0.0 Health endpoint verified")
    
    # 4. Test Student Pipeline Endpoint with Mock
    mock_eval = {
        "total_score": 85,
        "strengths": ["Excellent safety procedure", "Diagnostic waveforms verified"],
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
        
        pipeline_res = client.post(
            "/api/student/evaluate-and-dispatch",
            json={
                "student_id": "STU-1001",
                "practical_task": "Diagnose CAN bus fault.",
                "grading_rubric": ["Safety lockout", "Waveform check"],
                "submission_text": "Completed safety lockout and waveform check."
            }
        )
        assert pipeline_res.status_code == 200
        data = pipeline_res.json()["data"]
        assert data["dispatch"]["status"] == "DISPATCHED_TO_HIRING_PARTNER"
        print("[OK] Multi-Tenant Autonomous Placement Dispatch verified")

if __name__ == "__main__":
    test_multi_tenant_architecture()
