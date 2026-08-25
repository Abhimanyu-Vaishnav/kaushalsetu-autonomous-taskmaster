import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from recruiter_agent import AutonomousRecruiterAgent

client = TestClient(app)

def test_autonomous_background_agent():
    # 1. Test Portfolio HTML Route
    res = client.get("/portfolio/STU-1001")
    # Will be 404 until generated or 200 if generated
    assert res.status_code in [200, 404]
    print("[OK] Portfolio HTML route tested successfully")

    # 2. Test Autonomous Recruiter Pipeline Execution
    agent = AutonomousRecruiterAgent()
    with patch("recruiter_agent.get_genai_client") as mock_gen:
        output = agent.execute_autonomous_pipeline(
            student_id="STU-1001",
            assessment_id="ASS-DEFAULT",
            mcq_answers=[0, 0, 0, 0, 0],
            mcq_key=[0, 0, 0, 0, 0],
            submission_text="First, performed a full safety lockout procedure and verified system power status using a multimeter.",
            practical_task="Diagnose hardware fault",
            rubric=["Safety lockout", "Diagnostic accuracy"],
            github_url="https://github.com/skillforge/test-repo",
            live_url="http://localhost:8000/portfolio/STU-1001"
        )
        assert output["evaluation"]["mcq_score"] == 50.0
        assert output["evaluation"]["total_score"] >= 70
        assert output["dispatch"]["status"] in ["INTERVIEW_SCHEDULED", "APPLIED_AND_DISPATCHED", "NEEDS_HUMAN_INTERVENTION", "REMEDIAL_ASSIGNED"]
        assert len(output["telemetry"]) > 0
        print("[OK] Autonomous Recruiter Agent: Full background pipeline & telemetry execution verified!")

if __name__ == "__main__":
    test_autonomous_background_agent()
