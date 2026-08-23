from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from database import (
    get_institute,
    update_institute_config,
    get_all_students,
    get_student_by_id,
    add_student,
    get_assessments,
    get_job_applications
)
from agent_engine import (
    generate_assessment,
    evaluate_submission,
    dispatch_autonomous_placement
)

app = FastAPI(
    title="SkillForge Autonomous - Multi-Tenant Operations API",
    description="Multi-Tenant Vocational Institute Platform & Autonomous Placement Engine",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---

class InstituteConfigUpdate(BaseModel):
    institute_id: str = "INST-GLOBAL-01"
    dispatch_threshold: int = Field(70, ge=50, le=100)
    interview_cap_limit: int = Field(3, ge=1, le=10)

class StudentCreateRequest(BaseModel):
    full_name: str
    email: str
    branch_id: str
    course_name: str
    fees_status: str = "PAID"
    consent_given: int = 1

class AssessmentGenRequest(BaseModel):
    topic: str
    difficulty: str = "Intermediate"
    institute_id: str = "INST-GLOBAL-01"

class FullEvaluationRequest(BaseModel):
    student_id: str
    assessment_id: str = "ASS-DEFAULT"
    practical_task: str
    grading_rubric: List[str]
    submission_text: str
    image_base64: Optional[str] = None

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillForge Multi-Tenant Platform",
        "version": "3.0.0"
    }

# Institute Admin Endpoints
@app.get("/api/institute/info")
def api_get_institute(inst_id: str = "INST-GLOBAL-01"):
    return {"success": True, "data": get_institute(inst_id)}

@app.post("/api/institute/config")
def api_update_config(req: InstituteConfigUpdate):
    update_institute_config(req.institute_id, req.dispatch_threshold, req.interview_cap_limit)
    return {"success": True, "data": get_institute(req.institute_id)}

@app.get("/api/students")
def api_get_students():
    return {"success": True, "data": get_all_students()}

@app.post("/api/students/add")
def api_add_student(req: StudentCreateRequest):
    stu = add_student(req.full_name, req.email, req.branch_id, req.course_name, req.fees_status, req.consent_given)
    return {"success": True, "data": stu}

# Assessment & Exam Endpoints
@app.get("/api/assessments")
def api_get_assessments():
    return {"success": True, "data": get_assessments()}

@app.post("/api/assessment/generate")
def api_generate_exam(req: AssessmentGenRequest):
    try:
        exam = generate_assessment(req.topic, req.difficulty, req.institute_id)
        return {"success": True, "data": exam}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Student Evaluation & Autonomous Placement Pipeline
@app.post("/api/student/evaluate-and-dispatch")
def api_student_pipeline(req: FullEvaluationRequest):
    try:
        res = dispatch_autonomous_placement(
            student_id=req.student_id,
            assessment_id=req.assessment_id,
            submission_text=req.submission_text,
            practical_task=req.practical_task,
            rubric=req.grading_rubric,
            image_base64=req.image_base64
        )
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job Placement Ledger
@app.get("/api/placements/ledger")
def api_get_placements():
    return {"success": True, "data": get_job_applications()}
