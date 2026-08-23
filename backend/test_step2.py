import sys
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from agent_engine import gemma_fast_screening, evaluate_submission, dispatch_recruiter_action

client = TestClient(app)

def test_gemma_fast_screening():
    text = "First, completed standard safety procedure. Applied multimeter for voltage verification of circuit measurement tools."
    res = gemma_fast_screening(text)
    assert res["passed_screening"] is True
    assert res["structure_score"] >= 50
    print("[OK] Gemma Fast Screening unit test passed")

def test_high_scoring_student_dispatch():
    mock_high_eval = {
        "total_score": 92,
        "strengths": [
            "Flawless safety protocol execution",
            "Precise oscilloscope signal analysis",
            "Comprehensive diagnostic documentation"
        ],
        "skill_gaps": ["None identified"],
        "placement_ready": True,
        "recruiter_pitch": "Alex Mercer demonstrates exceptional technical diagnostic proficiency and safety mastery. Strongly recommended for top-tier hiring partner placement.",
        "fast_screening": {
            "passed_screening": True,
            "found_tokens": ["procedure", "safety", "verification"],
            "missing_tokens": [],
            "structure_score": 95
        }
    }
    
    with patch("main.evaluate_submission") as mock_eval:
        mock_eval.return_value = mock_high_eval
        
        payload = {
            "candidate_name": "Alex Mercer",
            "target_role": "Senior Automotive Diagnostic Technician",
            "practical_task": "Diagnose intermittent CAN bus signal degradation using oscilloscope.",
            "grading_rubric": [
                "Safety lockout procedure followed",
                "Signal measurement accurate",
                "Fault root cause documented"
            ],
            "submission_text": "Completed full safety procedure and verification..."
        }
        
        response = client.post("/api/submission/evaluate-and-dispatch", json=payload)
        assert response.status_code == 200
        res_data = response.json()
        
        assert res_data["success"] is True
        assert res_data["dispatch"]["action_tag"] == "ACTION: DISPATCHED_TO_HIRING_NETWORK"
        assert res_data["dispatch"]["placement_ready"] is True
        assert res_data["dispatch"]["payload"]["dispatch_status"] == "SUCCESS_SENT_TO_HIRING_PARTNER"
        assert "verified_metric_hash" in res_data["dispatch"]["payload"]
        
        print("[OK] High-scoring student test passed (DISPATCHED_TO_HIRING_NETWORK)")
        return res_data

def test_low_scoring_student_remedial():
    mock_low_eval = {
        "total_score": 58,
        "strengths": ["Basic awareness of electrical safety"],
        "skill_gaps": [
            "Failed to complete voltage drop measurements",
            "Incomplete circuit diagram interpretation"
        ],
        "placement_ready": False,
        "recruiter_pitch": "Candidate shows foundational knowledge but requires targeted practical remediation prior to employer referral.",
        "fast_screening": {
            "passed_screening": False,
            "found_tokens": ["safety"],
            "missing_tokens": ["procedure", "verification", "measurement"],
            "structure_score": 35
        }
    }
    
    with patch("main.evaluate_submission") as mock_eval:
        mock_eval.return_value = mock_low_eval
        
        payload = {
            "candidate_name": "Jordan Smith",
            "target_role": "Junior Electronics Technician",
            "practical_task": "Diagnose circuit failure.",
            "grading_rubric": ["Safety procedure", "Fault isolation"],
            "submission_text": "Checked safety briefly. Looked at wires."
        }
        
        response = client.post("/api/submission/evaluate-and-dispatch", json=payload)
        assert response.status_code == 200
        res_data = response.json()
        
        assert res_data["success"] is True
        assert res_data["dispatch"]["action_tag"] == "ACTION: QUEUED_FOR_REMEDIAL_TRAINING"
        assert res_data["dispatch"]["placement_ready"] is False
        assert res_data["dispatch"]["payload"]["dispatch_status"] == "QUEUED_FOR_REMEDIAL"
        
        print("[OK] Low-scoring student test passed (QUEUED_FOR_REMEDIAL_TRAINING)")
        return res_data

if __name__ == "__main__":
    test_gemma_fast_screening()
    high_res = test_high_scoring_student_dispatch()
    low_res = test_low_scoring_student_remedial()
    
    print("\n=======================================================")
    print("FORMATTED JSON OUTPUT: PASS CASE (HIGH-SCORING STUDENT)")
    print("=======================================================")
    print(json.dumps(high_res, indent=2))
    
    print("\n=======================================================")
    print("FORMATTED JSON OUTPUT: FAIL CASE (LOW-SCORING STUDENT)")
    print("=======================================================")
    print(json.dumps(low_res, indent=2))
