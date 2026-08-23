from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from agent_engine import (
    generate_assessment,
    evaluate_submission,
    dispatch_recruiter_action
)

app = FastAPI(
    title="SkillForge Autonomous - Agent Engine API",
    description="Autonomous Operations & Assessment Synthesizer for Vocational Institutes",
    version="1.0.0",
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
    topic: str = Field(..., example="CNC Machine Operations")
    difficulty: str = Field(default="Intermediate", example="Intermediate")

class SubmissionEvaluationRequest(BaseModel):
    candidate_name: str = Field(..., example="Alex Mercer")
    target_role: str = Field(..., example="Automotive Systems Technician")
    practical_task: str = Field(..., example="Diagnose intermittent electrical fault on CAN bus network.")
    grading_rubric: List[str] = Field(..., example=["Safety procedure followed", "Fault identified", "Documentation complete"])
    submission_text: str = Field(..., example="First performed safety lockout. Used oscilloscope to trace CAN signals...")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillForge Autonomous Engine",
        "step": 2
    }

@app.post("/api/assessment/generate")
def api_generate_assessment(req: AssessmentRequest):
    try:
        assessment = generate_assessment(topic=req.topic, difficulty=req.difficulty)
        return {
            "success": True,
            "data": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submission/evaluate-and-dispatch")
def api_evaluate_and_dispatch(req: SubmissionEvaluationRequest):
    try:
        # Step 1: Gemma Pre-Check + Gemini Deep Evaluation
        eval_result = evaluate_submission(
            submission_text=req.submission_text,
            practical_task=req.practical_task,
            grading_rubric=req.grading_rubric
        )
        
        # Step 2: Autonomous Recruiter Action Engine Dispatch
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
