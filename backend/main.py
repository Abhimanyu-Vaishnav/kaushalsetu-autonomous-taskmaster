from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from center_manager import get_centers, get_batches, get_candidates
from recruiter_hub import get_hiring_partners, get_requisitions, get_dispatch_ledger
from agent_engine import (
    generate_assessment,
    evaluate_submission,
    dispatch_recruiter_action,
    generate_remedial_curriculum
)

app = FastAPI(
    title="SkillForge Autonomous - Institutional Operations Engine API",
    description="Autonomous Vocational Institute Operations, Multimodal Grading & Recruiter Action Engine",
    version="2.0.0",
)

# Enable CORS for cross-origin frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssessmentRequest(BaseModel):
    center_id: Optional[str] = None
    batch_id: Optional[str] = None
    topic: str = Field(..., example="CNC Machine Operations")
    difficulty: str = Field(default="Intermediate", example="Intermediate")

class SubmissionEvaluationRequest(BaseModel):
    candidate_name: str = Field(..., example="Alex Mercer")
    target_role: str = Field(..., example="Automotive Systems Technician")
    practical_task: str = Field(..., example="Diagnose intermittent electrical fault on CAN bus network.")
    grading_rubric: List[str] = Field(..., example=["Safety procedure followed", "Fault identified", "Documentation complete"])
    submission_text: str = Field(..., example="First performed safety lockout. Used oscilloscope to trace CAN signals...")
    image_base64: Optional[str] = None


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillForge Institutional Operations Engine",
        "version": "2.0.0"
    }

# --- Module 1 Endpoints: Center & Batch Roster ---

@app.get("/api/centers")
def api_get_centers():
    return {"success": True, "data": get_centers()}

@app.get("/api/batches")
def api_get_batches(center_id: Optional[str] = None):
    return {"success": True, "data": get_batches(center_id)}

@app.get("/api/candidates")
def api_get_candidates(batch_id: Optional[str] = None):
    return {"success": True, "data": get_candidates(batch_id)}

# --- Assessment Generation Endpoint ---

@app.post("/api/assessment/generate")
def api_generate_assessment(req: AssessmentRequest):
    try:
        assessment = generate_assessment(topic=req.topic, difficulty=req.difficulty)
        assessment["center_id"] = req.center_id
        assessment["batch_id"] = req.batch_id
        return {
            "success": True,
            "data": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Module 2 & 3 Endpoint: Multimodal Evaluation & Recruiter Dispatch ---

@app.post("/api/submission/evaluate-and-dispatch")
def api_evaluate_and_dispatch(req: SubmissionEvaluationRequest):
    try:
        # 1. Fast Gemma screening + Gemini 3.5 Multimodal Cognitive Evaluation
        eval_result = evaluate_submission(
            submission_text=req.submission_text,
            practical_task=req.practical_task,
            grading_rubric=req.grading_rubric,
            image_base64=req.image_base64
        )
        
        # 2. Autonomous Recruiter Matching & Dispatch Ledger Logging
        dispatch_result = dispatch_recruiter_action(
            candidate_name=req.candidate_name,
            target_role=req.target_role,
            evaluation_data=eval_result
        )
        
        return {
            "success": True,
            "candidate_name": req.candidate_name,
            "target_role": req.target_role,
            "evaluation": eval_result,
            "dispatch": dispatch_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Module 3 Endpoints: Recruiter Network & Ledger ---

@app.get("/api/recruiter/partners")
def api_get_partners():
    return {"success": True, "data": get_hiring_partners()}

@app.get("/api/recruiter/requisitions")
def api_get_requisitions():
    return {"success": True, "data": get_requisitions()}

@app.get("/api/recruiter/ledger")
def api_get_ledger():
    return {"success": True, "data": get_dispatch_ledger()}
