from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import csv
import io

from database import (
    get_institute,
    update_institute_config,
    create_institute,
    get_all_students,
    get_student_by_id,
    add_student,
    set_student_consent,
    get_assessments,
    get_job_applications
)
from agent_engine import (
    generate_assessment,
    evaluate_submission,
    dispatch_autonomous_placement
)

app = FastAPI(
    title="SkillForge Autonomous - Enterprise Multi-Tenant Platform",
    description="Autonomous Vocational Operations, Multimodal Grading & Placement Action Engine",
    version="3.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---

class InstituteCreateReq(BaseModel):
    name: str
    code: str
    branches: List[str]
    courses: List[str]
    placement_threshold: int = 70
    max_interviews_cap: int = 3

class InstituteConfigReq(BaseModel):
    institute_id: str = "INST-GLOBAL-01"
    placement_threshold: int = Field(70, ge=50, le=100)
    max_interviews_cap: int = Field(3, ge=1, le=10)

class StudentCreateReq(BaseModel):
    institute_id: str = "INST-GLOBAL-01"
    branch_name: str
    full_name: str
    email: str
    phone: str = ""
    course_name: str
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
    image_base64: Optional[str] = None


# --- REST API Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillForge Enterprise Multi-Tenant Platform",
        "version": "3.6.0"
    }

# 1. Institute & Branch Management
@app.get("/api/institute/info")
def api_get_institute(inst_id: str = "INST-GLOBAL-01"):
    return {"success": True, "data": get_institute(inst_id)}

@app.post("/api/institute/create")
def api_create_institute(req: InstituteCreateReq):
    inst = create_institute(req.name, req.code, req.branches, req.courses, req.placement_threshold, req.max_interviews_cap)
    return {"success": True, "data": inst}

@app.post("/api/institute/config")
def api_update_config(req: InstituteConfigReq):
    update_institute_config(req.institute_id, req.placement_threshold, req.max_interviews_cap)
    return {"success": True, "data": get_institute(req.institute_id)}

# 2. Student Roster & CSV Bulk Upload
@app.get("/api/students")
def api_get_students(institute_id: Optional[str] = None):
    return {"success": True, "data": get_all_students(institute_id)}

@app.post("/api/students/add")
def api_add_student(req: StudentCreateReq):
    stu = add_student(req.institute_id, req.branch_name, req.full_name, req.email, req.phone, req.course_name, req.fees_status, req.consent)
    return {"success": True, "data": stu}

@app.post("/api/students/consent")
def api_set_consent(req: StudentConsentReq):
    set_student_consent(req.student_id, req.consent)
    return {"success": True, "data": get_student_by_id(req.student_id)}

@app.post("/api/students/bulk-upload")
async def api_bulk_upload(file: UploadFile = File(...), institute_id: str = "INST-GLOBAL-01"):
    contents = await file.read()
    buffer = io.StringIO(contents.decode("utf-8"))
    reader = csv.DictReader(buffer)
    
    added_students = []
    for row in reader:
        full_name = row.get("full_name", row.get("name", "Student"))
        email = row.get("email", "student@skillforge-edu.org")
        phone = row.get("phone", "+91 9876543210")
        branch_name = row.get("branch_name", row.get("branch", "Nangloi Center"))
        course_name = row.get("course_name", row.get("course", "Automotive & Hardware Diagnostics"))
        fees_status = row.get("fees_status", "PAID")
        
        stu = add_student(institute_id, branch_name, full_name, email, phone, course_name, fees_status, 1)
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

# 4. Student Submission & Dynamic Evaluation Pipeline
@app.post("/api/student/evaluate-and-dispatch")
def api_student_pipeline(req: FullEvaluationReq):
    try:
        res = dispatch_autonomous_placement(
            student_id=req.student_id,
            assessment_id=req.assessment_id,
            mcq_answers=req.mcq_answers,
            mcq_key=req.mcq_key,
            submission_text=req.submission_text,
            practical_task=req.practical_task,
            rubric=req.grading_rubric,
            image_base64=req.image_base64
        )
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Job Applications Ledger
@app.get("/api/placements/ledger")
def api_get_placements():
    return {"success": True, "data": get_job_applications()}

# 6. Verified Certificate Generator Endpoint
class CertificateReq(BaseModel):
    candidate_name: str
    student_id: str
    course_name: str
    branch_name: str
    total_score: int
    mcq_score: float
    practical_score: float
    metric_hash: str

@app.post("/api/certificate/generate")
def api_generate_certificate(req: CertificateReq):
    from agent_engine import generate_verified_certificate
    cert = generate_verified_certificate(
        req.candidate_name,
        req.student_id,
        req.course_name,
        req.branch_name,
        {"total_score": req.total_score, "mcq_score": req.mcq_score, "practical_score": req.practical_score},
        req.metric_hash
    )
    return {"success": True, "data": cert}
