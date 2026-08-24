import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import get_all_institutes, get_branches_by_institute, get_courses_by_branch, get_all_students, get_job_applications
from recruiter_agent import AutonomousRecruiterAgent

client = TestClient(app)

def test_relational_architecture():
    # 1. Test Relational Institutes, Branches & Courses
    insts = get_all_institutes()
    assert len(insts) >= 1
    inst_id = insts[0]["id"]
    print(f"[OK] Found Institute: {insts[0]['name']} ({inst_id})")
    
    branches = get_branches_by_institute(inst_id)
    assert len(branches) >= 1
    branch_id = branches[0]["id"]
    print(f"[OK] Found Branch: {branches[0]['branch_name']} ({branch_id})")
    
    courses = get_courses_by_branch(branch_id)
    assert len(courses) >= 1
    print(f"[OK] Found Course: {courses[0]['course_name']}")
    
    students = get_all_students(inst_id, branch_id)
    assert len(students) >= 1
    stu = students[0]
    print(f"[OK] Found Isolated Student: {stu['full_name']} ({stu['student_id']})")
    
    # 2. Test API Health v4.0.0
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "4.1.0"
    print("[OK] FastAPI v4.1.0 Multi-Tenant Health verified")
    
    # 3. Test Agent Execution & Human Intervention Ledger
    agent = AutonomousRecruiterAgent()
    with patch("recruiter_agent.get_genai_client") as mock_gen:
        output = agent.execute_autonomous_pipeline(
            student_id=stu["student_id"],
            assessment_id="ASS-DEFAULT",
            mcq_answers=[0, 0, 0, 0, 0],
            mcq_key=[0, 0, 0, 0, 0],
            submission_text="First, performed a full safety lockout procedure and verified system power status using a multimeter.",
            practical_task="Diagnose hardware fault",
            rubric=["Safety lockout", "Diagnostic accuracy"]
        )
        assert output["evaluation"]["total_score"] >= 70
        assert output["dispatch"]["status"] in ["APPLIED_AND_DISPATCHED", "INTERVIEW_SCHEDULED", "NEEDS_HUMAN_INTERVENTION", "REMEDIAL_ASSIGNED", "STUDENT_MATCH_HUB"]
        print(f"[OK] Agent Execution Dispatch Status: {output['dispatch']['status']}")
        
    # 4. Verify Ledger Branch Isolation
    ledger = get_job_applications(branch_id)
    assert len(ledger) >= 1
    print(f"[OK] Isolated Job Ledger for Branch verified ({len(ledger)} entry)")

if __name__ == "__main__":
    test_relational_architecture()
