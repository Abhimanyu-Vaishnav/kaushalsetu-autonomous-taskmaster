import sys
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from center_manager import get_centers, get_batches
from recruiter_hub import get_hiring_partners, get_requisitions

client = TestClient(app)

def test_production_modules():
    # 1. Test Center Manager SQLite Store
    centers = get_centers()
    assert len(centers) >= 3
    print("[OK] Module 1: Center Manager DB verified with", len(centers), "centers")
    
    # 2. Test Recruiter Hub Store
    partners = get_hiring_partners()
    reqs = get_requisitions()
    assert len(partners) >= 3
    assert len(reqs) >= 3
    print("[OK] Module 3: Recruiter Hub verified with", len(partners), "partners and", len(reqs), "requisitions")
    
    # 3. Test API Health & Endpoints
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "2.0.0"
    print("[OK] FastAPI v2.0.0 Health endpoint verified")
    
    # 4. Test Multimodal Evaluation API call with Mock
    mock_eval = {
        "total_score": 90,
        "strengths": ["Multimodal vision hardware check verified", "Safety protocol executed"],
        "skill_gaps": ["None"],
        "placement_ready": True,
        "recruiter_pitch": "Alex Mercer demonstrates exceptional technical diagnostic proficiency.",
        "fast_screening": {
            "passed_screening": True,
            "found_tokens": ["safety", "procedure"],
            "missing_tokens": [],
            "structure_score": 90
        }
    }
    
    with patch("main.evaluate_submission") as mock_eval_fn:
        mock_eval_fn.return_value = mock_eval
        
        response = client.post(
            "/api/submission/evaluate-and-dispatch",
            json={
                "candidate_name": "Alex Mercer",
                "target_role": "Automotive Systems Technician",
                "practical_task": "Diagnose CAN bus fault.",
                "grading_rubric": ["Safety procedure", "Diagnostic accuracy"],
                "submission_text": "Completed safety lockout and waveform check."
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["dispatch"]["action_tag"] == "ACTION: DISPATCHED_TO_HIRING_NETWORK"
        print("[OK] Module 2 & 3: Multimodal Evaluation & Recruiter Matching verified")

if __name__ == "__main__":
    test_production_modules()
