import sys
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from agent_engine import evaluate_submission

client = TestClient(app)

def test_dynamic_scoring_pipeline():
    mcq_key = [0, 0, 0, 0, 0]
    
    # 1. High-Scoring Student Test (5/5 MCQs = 30 pts)
    high_mcq_answers = [0, 0, 0, 0, 0]
    high_sub_text = "First, performed a full safety lockout procedure and verified system power status using a multimeter. Cleaned connector J-12 and re-tested voltage drop with tools."
    
    # Patch get_genai_client to avoid missing GEMINI_API_KEY error during unit test
    with patch("agent_engine.get_genai_client") as mock_gen:
        high_eval = evaluate_submission(
            mcq_answers=high_mcq_answers,
            mcq_key=mcq_key,
            submission_text=high_sub_text,
            practical_task="Diagnose hardware fault",
            grading_rubric=["Safety lockout", "Diagnostic accuracy"]
        )
        assert high_eval["mcq_score"] == 30.0
        assert high_eval["total_score"] >= 70
        assert high_eval["placement_ready"] is True
        print("[OK] Dynamic Scoring: High-Scoring Student calculation verified (MCQ: 30 pts, Total >= 70)")

    # 2. Low-Scoring Student Test (1/5 MCQs = 6 pts)
    low_mcq_answers = [0, 1, 2, 3, 1]
    low_sub_text = "Looked at wires."
    
    with patch("agent_engine.get_genai_client") as mock_gen:
        low_eval = evaluate_submission(
            mcq_answers=low_mcq_answers,
            mcq_key=mcq_key,
            submission_text=low_sub_text,
            practical_task="Diagnose hardware fault",
            grading_rubric=["Safety lockout", "Diagnostic accuracy"]
        )
        assert low_eval["mcq_score"] == 6.0
        assert low_eval["total_score"] < 70
        assert low_eval["placement_ready"] is False
        assert "remedial_schedule" in low_eval
        print("[OK] Dynamic Scoring: Low-Scoring Student calculation verified (MCQ: 6 pts, Total < 70 -> Remedial)")

if __name__ == "__main__":
    test_dynamic_scoring_pipeline()
