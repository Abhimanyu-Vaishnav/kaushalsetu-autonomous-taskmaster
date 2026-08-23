from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import csv
import io
import os

from database import (
    get_all_institutes,
    get_institute_by_id,
    get_institute_by_code,
    create_institute,
    get_branches_by_institute,
    create_branch,
    get_courses_by_branch,
    create_course,
    get_all_students,
    get_student_by_id,
    add_student,
    set_student_consent,
    get_assessments,
    get_job_applications
)
from agent_engine import (
    generate_assessment,
    generate_verified_certificate
)
from recruiter_agent import AutonomousRecruiterAgent

app = FastAPI(
    title="SkillForge Autonomous - Enterprise Multi-Tenant Platform",
    description="Autonomous Vocational Operations, Multimodal Grading & Placement Action Engine",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PORTFOLIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
os.makedirs(PORTFOLIO_DIR, exist_ok=True)

# --- Pydantic Schemas ---

class InstituteCreateReq(BaseModel):
    name: str
    code: str
    placement_threshold: int = 70
    max_interviews_cap: int = 3

class BranchCreateReq(BaseModel):
    institute_id: str
    branch_name: str
    city: str

class CourseCreateReq(BaseModel):
    institute_id: str
    branch_id: str
    course_name: str
    curriculum_summary: str = ""

class StudentCreateReq(BaseModel):
    institute_id: str
    branch_id: str
    course_id: str
    branch_name: str
    course_name: str
    full_name: str
    dob: str = "2002-01-01"
    email: str
    phone: str = ""
    bio: str = ""
    fees_status: str = "PAID"
    consent: int = 1

class StudentConsentReq(BaseModel):
    student_id: str
    consent: bool

class AssessmentGenReq(BaseModel):
    topic: str
    difficulty: str = "Intermediate"
    institute_id: str = "INST-GLOBAL-01"

class FullEvaluationReq(BaseModel):
    student_id: str
    assessment_id: str = "ASS-DEFAULT"
    mcq_answers: Optional[List[int]] = None
    mcq_key: Optional[List[int]] = None
    practical_task: str
    grading_rubric: List[str]
    submission_text: str
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    image_base64: Optional[str] = None

class CertificateReq(BaseModel):
    candidate_name: str
    student_id: str
    course_name: str
    branch_name: str
    total_score: int
    mcq_score: float
    practical_score: float
    metric_hash: str


# --- REST API Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillForge Autonomous Multi-Tenant Architecture Engine",
        "version": "4.0.0"
    }

# Standalone Portfolio HTML Route
@app.get("/portfolio/{student_id}", response_class=HTMLResponse)
def get_student_portfolio(student_id: str):
    file_path = os.path.join(PORTFOLIO_DIR, f"{student_id}.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail=f"Portfolio dossier for student '{student_id}' not found.")

# 1. Relational Governance Endpoints (Institutes -> Branches -> Courses)
@app.get("/api/institutes")
def api_get_all_institutes():
    return {"success": True, "data": get_all_institutes()}

@app.post("/api/institutes/create")
def api_create_institute(req: InstituteCreateReq):
    inst = create_institute(req.name, req.code, req.placement_threshold, req.max_interviews_cap)
    return {"success": True, "data": inst}

@app.get("/api/branches")
def api_get_branches(institute_id: str):
    return {"success": True, "data": get_branches_by_institute(institute_id)}

@app.post("/api/branches/create")
def api_create_branch(req: BranchCreateReq):
    branch = create_branch(req.institute_id, req.branch_name, req.city)
    return {"success": True, "data": branch}

@app.get("/api/courses")
def api_get_courses(branch_id: str):
    return {"success": True, "data": get_courses_by_branch(branch_id)}

@app.post("/api/courses/create")
def api_create_course(req: CourseCreateReq):
    course = create_course(req.institute_id, req.branch_id, req.course_name, req.curriculum_summary)
    return {"success": True, "data": course}

# 2. Student Enrollment & CSV Bulk Upload
@app.get("/api/students")
def api_get_students(institute_id: Optional[str] = None, branch_id: Optional[str] = None):
    return {"success": True, "data": get_all_students(institute_id, branch_id)}

@app.get("/api/student/{student_id}")
def api_get_student_detail(student_id: str):
    stu = get_student_by_id(student_id)
    if stu:
        return {"success": True, "data": stu}
    raise HTTPException(status_code=404, detail="Student not found")

@app.post("/api/students/add")
def api_add_student(req: StudentCreateReq):
    stu = add_student(
        req.institute_id, req.branch_id, req.course_id, req.branch_name, req.course_name,
        req.full_name, req.dob, req.email, req.phone, req.bio, req.fees_status, req.consent
    )
    return {"success": True, "data": stu}

@app.post("/api/students/consent")
def api_set_consent(req: StudentConsentReq):
    set_student_consent(req.student_id, req.consent)
    return {"success": True, "data": get_student_by_id(req.student_id)}

@app.post("/api/students/bulk-upload")
async def api_bulk_upload(
    file: UploadFile = File(...),
    institute_id: str = "INST-GLOBAL-01",
    branch_id: str = "BR-NANGLOI",
    course_id: str = "CRS-AUTO-01",
    branch_name: str = "Nangloi Center",
    course_name: str = "Automotive & Hardware Diagnostics"
):
    contents = await file.read()
    buffer = io.StringIO(contents.decode("utf-8"))
    reader = csv.DictReader(buffer)
    
    added_students = []
    for row in reader:
        full_name = row.get("full_name", row.get("name", "Student"))
        dob = row.get("dob", "2002-01-01")
        email = row.get("email", "student@skillforge-edu.org")
        phone = row.get("phone", "+91 9876543210")
        
        stu = add_student(
            institute_id, branch_id, course_id, branch_name, course_name,
            full_name, dob, email, phone, "Bulk enrolled candidate", "PAID", 1
        )
        added_students.append(stu)
        
    return {"success": True, "count": len(added_students), "data": added_students}

# 3. Assessment Synthesizer
@app.get("/api/assessments")
def api_get_assessments(institute_id: Optional[str] = None):
    return {"success": True, "data": get_assessments(institute_id)}

@app.post("/api/assessment/generate")
def api_generate_exam(req: AssessmentGenReq):
    try:
        exam = generate_assessment(req.topic, req.difficulty, req.institute_id)
        return {"success": True, "data": exam}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Student Submission & Autonomous Background Dispatcher
@app.post("/api/student/evaluate-and-dispatch")
def api_student_pipeline(req: FullEvaluationReq):
    try:
        agent = AutonomousRecruiterAgent()
        res = agent.execute_autonomous_pipeline(
            student_id=req.student_id,
            assessment_id=req.assessment_id,
            mcq_answers=req.mcq_answers,
            mcq_key=req.mcq_key,
            submission_text=req.submission_text,
            practical_task=req.practical_task,
            rubric=req.grading_rubric,
            github_url=req.github_url,
            live_url=req.live_url,
            image_base64=req.image_base64
        )
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Job Applications Ledger
@app.get("/api/placements/ledger")
def api_get_placements(branch_id: Optional[str] = None):
    return {"success": True, "data": get_job_applications(branch_id)}

# 6. Verified Certificate Generator Endpoint
@app.post("/api/certificate/generate")
def api_generate_certificate(req: CertificateReq):
    cert = generate_verified_certificate(
        req.candidate_name,
        req.student_id,
        req.course_name,
        req.branch_name,
        {"total_score": req.total_score, "mcq_score": req.mcq_score, "practical_score": req.practical_score},
        req.metric_hash
    )
    return {"success": True, "data": cert}
