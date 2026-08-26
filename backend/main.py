import os
import sys

# Ensure both backend directory and root project directory are in sys.path for direct imports
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
for d in [BACKEND_DIR, ROOT_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import re
import csv
import io
import json
import sqlite3
import uuid
from datetime import datetime, date

try:
    from database import (
        DB_PATH,
        get_db,
        init_complete_db,
        export_database_snapshot,
        get_db_connection,
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
        get_job_applications,
        ensure_db_schema
    )
except ImportError:
    from backend.database import (
        DB_PATH,
        get_db,
        init_complete_db,
        export_database_snapshot,
        get_db_connection,
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
        get_job_applications,
        ensure_db_schema
    )

try:
    from agent_engine import (
        generate_assessment,
        generate_verified_certificate
    )
except ImportError:
    from backend.agent_engine import (
        generate_assessment,
        generate_verified_certificate
    )

try:
    from recruiter_agent import AutonomousRecruiterAgent
except ImportError:
    from backend.recruiter_agent import AutonomousRecruiterAgent

# Ensure database schema is up-to-date on startup
ensure_db_schema()

app = FastAPI(
    title="KaushalSetu: Autonomous Vocational Taskmaster",
    description="Autonomous Dual-AI Institutional Taskmaster for Vocational Skilling, Multimodal Evaluation & Zero-HITL Job Dispatch",
    version="4.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "kaushalsetu-backend", "time": datetime.now().isoformat()}

def get_db():
    from database import get_db_connection
    return get_db_connection()

def direct_reset_database():
    try:
        from database import reset_database_clean_slate
        reset_database_clean_slate()
        return {"status": "success", "message": "Database reset cleanly."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_student_login(student_id: str, dob_raw: str):
    from database import get_db_connection, normalize_dob
    norm_dob = normalize_dob(dob_raw)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE UPPER(student_id) = UPPER(?) OR UPPER(id) = UPPER(?)", (student_id.strip(), student_id.strip()))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"authenticated": False, "message": "Student ID not found."}
    s = dict(row)
    if not s.get("dob") or normalize_dob(s.get("dob")) == norm_dob:
        return {"authenticated": True, "student": s}
    return {"authenticated": False, "message": "Date of Birth does not match."}

def direct_get_institutes():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, name, code, address, contact_email, contact_phone, placement_threshold FROM institutes ORDER BY created_at DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching institutes: {e}")
        return []

def direct_get_branches(institute_id: str = None):
    try:
        conn = get_db()
        c = conn.cursor()
        if institute_id:
            c.execute("SELECT id, institute_id, name, branch_name, city, location, contact_person, phone FROM branches WHERE institute_id = ? ORDER BY created_at DESC", (str(institute_id).strip(),))
        else:
            c.execute("SELECT id, institute_id, name, branch_name, city, location, contact_person, phone FROM branches ORDER BY created_at DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        for r in rows:
            if not r.get("name"):
                r["name"] = r.get("branch_name") or "Main Center"
            if not r.get("location"):
                r["location"] = r.get("city") or "Delhi"
        return rows
    except Exception as e:
        print(f"Error fetching branches: {e}")
        return []

def direct_create_institute(payload: dict):
    try:
        name = str(payload.get("name") or payload.get("institute_name") or "").strip()
        if not name:
            return {"status": "error", "message": "Institute name is required"}
        inst_id = str(payload.get("id") or f"INST-{uuid.uuid4().hex[:6].upper()}").strip()
        code = str(payload.get("code") or f"INST-{int(time.time())%10000 if 'time' in globals() else 1001}").strip()
        address = str(payload.get("address") or payload.get("location") or "").strip()
        email = str(payload.get("contact_email") or payload.get("email") or "").strip()
        phone = str(payload.get("contact_phone") or payload.get("phone") or "").strip()
        initial_branch = str(payload.get("initial_branch_name") or payload.get("branch_name") or "Main Center Node").strip()
        initial_city = str(payload.get("initial_city") or payload.get("city") or "New Delhi").strip()
        thresh = int(payload.get("placement_threshold") or 70)

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO institutes (id, name, code, address, contact_email, contact_phone, placement_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (inst_id, name, code, address, email, phone, thresh))
        
        branch_id = f"BR-{uuid.uuid4().hex[:6].upper()}"
        c.execute("""
            INSERT OR REPLACE INTO branches (id, institute_id, name, branch_name, city, location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (branch_id, inst_id, initial_branch, initial_branch, initial_city, initial_city))
        
        conn.commit()
        conn.close()
        try:
            export_database_snapshot()
        except Exception:
            pass
        return {"status": "success", "success": True, "message": "Institute created successfully", "id": inst_id, "data": {"id": inst_id, "name": name, "code": code}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_create_branch(payload: dict):
    try:
        name = str(payload.get("name") or payload.get("branch_name") or "").strip()
        if not name:
            return {"status": "error", "message": "Branch name is required"}
        branch_id = str(payload.get("id") or f"BR-{uuid.uuid4().hex[:6].upper()}").strip()
        inst_id = str(payload.get("institute_id") or "INST-GLOBAL-01").strip()
        city = str(payload.get("city") or payload.get("location") or "Delhi").strip()
        contact_person = str(payload.get("contact_person") or "").strip()
        phone = str(payload.get("phone") or "").strip()

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO branches (id, institute_id, name, branch_name, city, location, contact_person, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (branch_id, inst_id, name, name, city, city, contact_person, phone))
        conn.commit()
        conn.close()
        try:
            export_database_snapshot()
        except Exception:
            pass
        return {"status": "success", "success": True, "message": "Branch created successfully", "id": branch_id, "data": {"id": branch_id, "name": name, "city": city}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_get_placement_ledger(branch_id: str = None, institute_id: str = None):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS placement_ledger (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                track TEXT,
                branch_id TEXT,
                company_name TEXT,
                role_title TEXT,
                match_percentage INTEGER,
                status TEXT DEFAULT 'DISPATCHED',
                dossier_url TEXT,
                ledger_hash TEXT,
                dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        if branch_id and str(branch_id).strip():
            c.execute("SELECT * FROM placement_ledger WHERE branch_id = ? ORDER BY dispatched_at DESC", (str(branch_id).strip(),))
        elif institute_id and str(institute_id).strip():
            c.execute("SELECT * FROM placement_ledger WHERE branch_id IN (SELECT id FROM branches WHERE institute_id = ?) ORDER BY dispatched_at DESC", (str(institute_id).strip(),))
        else:
            c.execute("SELECT * FROM placement_ledger ORDER BY dispatched_at DESC")
        
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return {"status": "success", "success": True, "ledger": rows, "data": rows}
    except Exception as e:
        return {"status": "error", "message": str(e), "ledger": [], "data": []}

def direct_dispatch_placement(payload: dict):
    try:
        import hashlib
        import uuid
        s_id = str(payload.get("student_id") or "").strip()
        s_name = str(payload.get("student_name") or payload.get("full_name") or "Candidate").strip()
        track = str(payload.get("track") or payload.get("course_name") or "General Track").strip()
        branch_id = str(payload.get("branch_id") or "BR-MAIN").strip()
        company = str(payload.get("company_name") or "Hiring Partner").strip()
        role = str(payload.get("role_title") or "Specialist").strip()
        match_pct = int(payload.get("match_percentage") or 85)
        dossier_url = str(payload.get("dossier_url") or "").strip()

        raw_sign = f"{s_id}|{company}|{role}|{datetime.now().isoformat()}"
        ledger_hash = hashlib.sha256(raw_sign.encode()).hexdigest()[:16].upper()
        entry_id = f"PLC-{uuid.uuid4().hex[:8].upper()}"

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS placement_ledger (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                student_name TEXT,
                track TEXT,
                branch_id TEXT,
                company_name TEXT,
                role_title TEXT,
                match_percentage INTEGER,
                status TEXT DEFAULT 'DISPATCHED',
                dossier_url TEXT,
                ledger_hash TEXT,
                dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            INSERT INTO placement_ledger 
            (id, student_id, student_name, track, branch_id, company_name, role_title, match_percentage, status, dossier_url, ledger_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'DISPATCHED', ?, ?)
        """, (entry_id, s_id, s_name, track, branch_id, company, role, match_pct, dossier_url, ledger_hash))

        c.execute("""
            INSERT INTO agent_activity_logs (id, action_type, description)
            VALUES (?, 'AUTO_PLACEMENT_DISPATCH', ?)
        """, (f"LOG-{uuid.uuid4().hex[:8].upper()}", f"Dispatched dossier for {s_name} ({s_id}) to {company} for role {role} (Seal: {ledger_hash})"))

        conn.commit()
        conn.close()
        try:
            export_database_snapshot()
        except Exception:
            pass
        return {"status": "success", "success": True, "ledger_id": entry_id, "ledger_hash": ledger_hash}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_create_course(payload: dict):
    try:
        import uuid, json
        
        c_title = str(
            payload.get("course_name") 
            or payload.get("title") 
            or payload.get("course_title") 
            or "Vocational Technical Course"
        ).strip()

        topic = str(payload.get("topic") or c_title).strip()
        modules = payload.get("modules") or payload.get("curriculum_sections") or []
        mcqs = payload.get("mcqs") or []
        capstone = str(payload.get("capstone_assignment") or payload.get("capstone") or payload.get("course_description") or "").strip()
        skills = payload.get("skills") or payload.get("core_skills") or []
        branch_id = str(payload.get("branch_id") or "").strip()
        institute_id = str(payload.get("institute_id") or "").strip()
        desc = str(payload.get("course_description") or payload.get("curriculum_summary") or c_title).strip()

        course_id = str(payload.get("id") or f"CRS-{uuid.uuid4().hex[:6].upper()}").strip()

        modules_json = json.dumps(modules) if isinstance(modules, (list, dict)) else str(modules)
        mcqs_json = json.dumps(mcqs) if isinstance(mcqs, (list, dict)) else str(mcqs)
        skills_json = json.dumps(skills) if isinstance(skills, (list, dict)) else str(skills)

        conn = get_db()
        c = conn.cursor()

        # Check existing columns in courses table
        c.execute("PRAGMA table_info(courses)")
        cols = [r[1] for r in c.fetchall()]

        # Build dynamic INSERT query based on actual existing columns
        insert_data = {
            "id": course_id,
            "topic": topic,
            "modules": modules_json,
            "mcqs": mcqs_json,
            "capstone": capstone
        }

        if "title" in cols:
            insert_data["title"] = c_title
        if "course_name" in cols:
            insert_data["course_name"] = c_title
        if "skills" in cols:
            insert_data["skills"] = skills_json
        if "branch_id" in cols:
            insert_data["branch_id"] = branch_id
        if "institute_id" in cols:
            insert_data["institute_id"] = institute_id
        if "course_description" in cols:
            insert_data["course_description"] = desc
        if "curriculum_summary" in cols:
            insert_data["curriculum_summary"] = desc
        if "curriculum_sections" in cols:
            insert_data["curriculum_sections"] = modules_json
        if "core_skills" in cols:
            insert_data["core_skills"] = skills_json

        columns_str = ", ".join(insert_data.keys())
        placeholders_str = ", ".join(["?"] * len(insert_data))
        values = list(insert_data.values())

        c.execute(f"INSERT OR REPLACE INTO courses ({columns_str}) VALUES ({placeholders_str})", values)
        conn.commit()
        conn.close()

        try:
            log_agent_activity("CREATE_COURSE", "course", course_id, f"Created curriculum for {c_title}")
        except Exception:
            pass

        try:
            export_database_snapshot()
        except Exception:
            pass

        return {"status": "success", "success": True, "message": "Course created successfully!", "course_id": course_id, "title": c_title, "id": course_id, "data": {"id": course_id, "title": c_title, "course_name": c_title}}
    except Exception as e:
        return {"status": "error", "message": f"Course creation failed: {str(e)}"}

def direct_get_courses(branch_id: str = None, institute_id: str = None):
    try:
        conn = get_db()
        c = conn.cursor()
        if branch_id and str(branch_id).strip():
            c.execute("SELECT * FROM courses WHERE branch_id = ? OR branch_id = '' OR branch_id IS NULL ORDER BY created_at DESC", (str(branch_id).strip(),))
        elif institute_id and str(institute_id).strip():
            c.execute("SELECT * FROM courses WHERE institute_id = ? OR institute_id = '' OR institute_id IS NULL ORDER BY created_at DESC", (str(institute_id).strip(),))
        else:
            c.execute("SELECT * FROM courses ORDER BY created_at DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        for r in rows:
            if not r.get("course_name"):
                r["course_name"] = r.get("title") or "Vocational Track"
            if not r.get("title"):
                r["title"] = r.get("course_name") or "Vocational Track"
        return rows
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []

def direct_update_course(course_id: str, payload: dict):
    try:
        title = payload.get("title") or payload.get("course_name") or "Vocational Track"
        topic = payload.get("topic") or title
        modules = payload.get("modules") or payload.get("curriculum_sections") or []
        mcqs = payload.get("mcqs") or []
        capstone = payload.get("capstone") or payload.get("course_description") or ""
        desc = payload.get("course_description") or payload.get("curriculum_summary") or title
        skills = payload.get("core_skills") or payload.get("skills") or []

        modules_json = json.dumps(modules) if isinstance(modules, (list, dict)) else str(modules)
        mcqs_json = json.dumps(mcqs) if isinstance(mcqs, (list, dict)) else str(mcqs)
        skills_json = json.dumps(skills) if isinstance(skills, (list, dict)) else str(skills)

        conn = get_db()
        c = conn.cursor()
        c.execute("""
            UPDATE courses 
            SET title = ?, topic = ?, modules = ?, mcqs = ?, capstone = ?, course_description = ?, curriculum_summary = ?, curriculum_sections = ?, core_skills = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, topic, modules_json, mcqs_json, capstone, desc, desc, modules_json, skills_json, str(course_id)))
        conn.commit()
        conn.close()
        try:
            export_database_snapshot()
        except Exception:
            pass
        return {"status": "success", "success": True, "message": "Course updated successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_delete_course(course_id: str):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM courses WHERE id = ?", (str(course_id),))
        conn.commit()
        conn.close()
        try:
            export_database_snapshot()
        except Exception:
            pass
        return {"status": "success", "success": True, "message": "Course deleted successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_get_students(branch_id: str = None, institute_id: str = None):
    try:
        conn = get_db()
        c = conn.cursor()
        if branch_id and str(branch_id).strip():
            c.execute("SELECT * FROM students WHERE branch_id = ? OR branch_center LIKE ? ORDER BY created_at DESC", (str(branch_id).strip(), f"%{branch_id}%"))
        elif institute_id and str(institute_id).strip():
            c.execute("SELECT * FROM students WHERE institute_id = ? ORDER BY created_at DESC", (str(institute_id).strip(),))
        else:
            c.execute("SELECT * FROM students ORDER BY created_at DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        for r in rows:
            if not r.get("full_name"):
                r["full_name"] = r.get("name") or "Candidate"
            if not r.get("student_id"):
                r["student_id"] = r.get("id") or "STU-1001"
            if not r.get("course_name"):
                r["course_name"] = r.get("track") or "Vocational Track"
        return rows
    except Exception as e:
        print(f"Error fetching students: {e}")
        return []

def direct_add_student(payload: dict):
    if not isinstance(payload, dict):
        return {"status": "error", "message": "Invalid payload format"}
    try:
        from database import add_student
        return add_student(**payload)
    except Exception as e:
        return {"status": "error", "message": str(e)}

def direct_get_agent_logs(page: int = 1, page_size: int = 15, branch_id: str = None):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_activity_logs (
                id TEXT PRIMARY KEY,
                institute_id TEXT DEFAULT 'INST-GLOBAL-01',
                branch_id TEXT DEFAULT '',
                student_id TEXT DEFAULT '',
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        page = max(1, int(page or 1))
        page_size = max(1, int(page_size or 15))
        offset = (page - 1) * page_size

        if branch_id and str(branch_id).strip():
            c.execute("SELECT COUNT(*) FROM agent_activity_logs WHERE branch_id = ?", (str(branch_id).strip(),))
            total_count = c.fetchone()[0]
            c.execute("SELECT * FROM agent_activity_logs WHERE branch_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?", (str(branch_id).strip(), page_size, offset))
        else:
            c.execute("SELECT COUNT(*) FROM agent_activity_logs")
            total_count = c.fetchone()[0]
            c.execute("SELECT * FROM agent_activity_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?", (page_size, offset))

        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        for r in rows:
            if not r.get("action"):
                r["action"] = r.get("action_type") or "AGENT_ACTION"
            if not r.get("details"):
                r["details"] = r.get("description") or "Operation recorded"
            if not r.get("entity_id"):
                r["entity_id"] = r.get("student_id") or r.get("id") or "N/A"

        total_pages = max(1, (total_count + page_size - 1) // page_size)

        return {
            "status": "success",
            "success": True,
            "logs": rows,
            "data": rows,
            "total_count": total_count,
            "page": page,
            "total_pages": total_pages
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "logs": [], "data": [], "total_count": 0, "total_pages": 1}

def direct_create_student(payload: dict):
    if not isinstance(payload, dict):
        return {"status": "error", "message": "Invalid payload format"}
    try:
        from database import add_student
        return add_student(**payload)
    except Exception as e:
        return {"status": "error", "message": f"Student creation failed: {str(e)}"}

def direct_delete_student(student_id: str):
    try:
        sid = str(student_id).strip()
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE UPPER(id) = UPPER(?) OR UPPER(student_id) = UPPER(?)", (sid, sid))
        c.execute("DELETE FROM evaluations WHERE UPPER(student_id) = UPPER(?)", (sid,))
        conn.commit()
        conn.close()
        try:
            export_database_snapshot()
        except Exception:
            pass
        return {"status": "success", "success": True, "message": "Student record deleted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

PORTFOLIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
os.makedirs(PORTFOLIO_DIR, exist_ok=True)

# --- Pydantic Schemas ---

class InstituteCreateReq(BaseModel):
    name: str
    code: str
    initial_branch_name: str = "Main Center"
    initial_city: str = "Delhi"
    num_mcqs_config: int = 10
    placement_threshold: int = 70
    max_interviews_cap: int = 3

class InstituteConfigReq(BaseModel):
    institute_id: str
    num_mcqs_config: int = 10
    placement_threshold: int = 70
    max_interviews_cap: int = 3

class BranchCreateReq(BaseModel):
    institute_id: str
    branch_name: str
    city: str

from typing import List, Optional, Dict, Any, Union

class CourseCreateReq(BaseModel):
    institute_id: str
    branch_id: str
    course_name: str
    curriculum_summary: str = ""
    course_description: str = ""
    curriculum_sections: Union[str, List[str], Any] = ""
    core_skills: Union[str, List[str], Any] = ""
    default_mcq_count: int = 10

class CourseUpdateReq(BaseModel):
    course_id: Optional[str] = None
    course_name: str
    curriculum_summary: Optional[str] = ""
    course_description: Optional[str] = ""
    curriculum_sections: Optional[Union[str, List[str]]] = ""
    core_skills: Optional[Union[str, List[str]]] = ""
    default_mcq_count: Optional[int] = 10

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

class StudentLoginRequest(BaseModel):
    student_id: Optional[str] = None
    id: Optional[str] = None
    dob: str

class StudentLoginReq(BaseModel):
    student_id: Optional[str] = None
    id: Optional[str] = None
    dob: str

class StudentUpdateProfileReq(BaseModel):
    student_id: str
    full_name: str
    email: str
    phone: str = ""
    dob: str = ""
    city: str = ""
    bio: str = ""
    github_url: str = ""
    linkedin_url: str = ""
    website_url: str = ""
    twitter_url: str = ""
    skills_list: str = ""
    target_role_preference: str = ""
    past_companies_text: str = ""
    work_experience_years: int = 0

class StudentAdminUpdateReq(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    dob: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    track: Optional[str] = None
    course_name: Optional[str] = None
    branch_center: Optional[str] = None
    branch_name: Optional[str] = None
    city: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    twitter_url: Optional[str] = None
    mcq_score: Optional[float] = None
    capstone_score: Optional[float] = None
    practical_score: Optional[float] = None
    experience_summary: Optional[str] = None
    bio: Optional[str] = None
    work_experience_years: Optional[int] = 0

class StudentConsentReq(BaseModel):
    student_id: str
    consent: bool

class AssessmentGenReq(BaseModel):
    topic: str
    difficulty: str = "Intermediate"
    institute_id: str = "INST-GLOBAL-01"
    num_questions: int = 10

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


# --- Dynamic Public Base URL Resolution ---

def get_public_base_url(request: Request = None) -> str:
    env_base = os.environ.get("APP_BASE_URL", "").rstrip("/")
    if env_base:
        return env_base
    if request:
        proto = request.headers.get("x-forwarded-proto", "http")
        host = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if host:
            return f"{proto}://{host}".rstrip("/")
        if hasattr(request, "base_url") and request.base_url:
            return str(request.base_url).rstrip("/")
    return "http://localhost:8000"

get_base_url = get_public_base_url

# --- REST API Endpoints ---

@app.get("/")
def root(request: Request = None):
    base_url = get_base_url(request)
    return {
        "status": "healthy",
        "service": "KaushalSetu: Autonomous Vocational Taskmaster Engine",
        "version": "4.1.0",
        "docs_url": f"{base_url}/docs",
        "health_url": f"{base_url}/health",
        "message": "Welcome to KaushalSetu Backend API. Open /docs for Interactive Swagger Documentation."
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "KaushalSetu: Autonomous Vocational Taskmaster Engine",
        "version": "4.1.0"
    }

# Standalone Portfolio HTML Route - Autonomous Gemini 2.5 AI Dossier Synthesizer
@app.get("/portfolio/{student_id}", response_class=HTMLResponse)
def get_student_portfolio(student_id: str, request: Request = None):
    from database import get_student_by_id
    from dossier_generator import generate_candidate_dossier_html

    student = get_student_by_id(student_id)
    if not student:
        student = {
            "student_id": student_id,
            "full_name": f"Candidate {student_id}",
            "course_name": "Vocational Technical Specialty",
            "branch_name": "Main Center Node",
            "email": f"{student_id.lower()}@kaushalsetu.internal",
            "skills_list": ["Practical Diagnostics", "System Testing", "Technical Compliance"],
            "bio": f"Certified candidate {student_id} evaluated under KaushalSetu Taskmaster Engine."
        }

    base_url = get_base_url(request)
    html_content = generate_candidate_dossier_html(student, base_url=base_url)
    return HTMLResponse(content=html_content, status_code=200)

# 1. Relational Governance Endpoints (Institutes -> Branches -> Courses)
@app.get("/api/institutes")
def api_get_all_institutes():
    return {"success": True, "data": get_all_institutes()}

@app.post("/api/institutes/create")
def api_create_institute(req: InstituteCreateReq):
    inst = create_institute(req.name, req.code, req.initial_branch_name, req.initial_city, req.num_mcqs_config, req.placement_threshold, req.max_interviews_cap)
    return {"success": True, "data": inst}

@app.post("/api/institute/config")
def api_update_institute_config(req: InstituteConfigReq):
    from database import update_institute_config, get_institute_by_id
    inst = update_institute_config(req.institute_id, req.num_mcqs_config, req.placement_threshold, req.max_interviews_cap)
    return {"success": True, "data": inst}

@app.get("/api/branches")
def api_get_branches(institute_id: str):
    return {"success": True, "data": get_branches_by_institute(institute_id)}

@app.post("/api/branches/create")
def api_create_branch(req: BranchCreateReq):
    branch = create_branch(req.institute_id, req.branch_name, req.city)
    return {"success": True, "data": branch}

class CourseSynthesizeReq(BaseModel):
    institute_id: str
    branch_id: str
    course_input: str

class SmartIngestReq(BaseModel):
    institute_id: str
    branch_id: str
    course_id: str
    branch_name: str
    course_name: str
    raw_text_or_url: str

@app.post("/api/courses/synthesize")
def api_synthesize_course(req: CourseSynthesizeReq):
    from agent_engine import synthesize_course_from_input
    data = synthesize_course_from_input(req.course_input)
    course = create_course(req.institute_id, req.branch_id, data['course_name'], data['curriculum_summary'])
    from database import log_agent_activity
    log_agent_activity("COURSE_SYNTHESIZED", f"AI Course Synthesizer generated course '{data['course_name']}'", institute_id=req.institute_id, branch_id=req.branch_id)
    return {"success": True, "data": course, "synthesis": data}

@app.post("/api/students/smart-ingest")
def api_smart_ingest_student(req: SmartIngestReq):
    from agent_engine import parse_resume_profile
    parsed = parse_resume_profile(req.raw_text_or_url)
    skills_str = ", ".join(parsed.get('skills_list', []))
    stu = add_student(
        req.institute_id, req.branch_id, req.course_id, req.branch_name, req.course_name,
        parsed.get('full_name', 'Student Candidate'), "2002-01-01", parsed.get('email', 'candidate@skillforge-edu.org'),
        parsed.get('phone', ''), parsed.get('bio', ''), "PAID", 1
    )
    from database import update_student_profile, log_agent_activity
    update_student_profile(
        stu['student_id'], parsed.get('full_name'), parsed.get('email'), parsed.get('phone'),
        parsed.get('bio'), "", skills_str, parsed.get('target_role_preference'),
        parsed.get('past_companies_text'), parsed.get('work_experience_years', 0)
    )
    log_agent_activity("STUDENT_SMART_INGESTED", f"Smart AI Ingestion created student {stu['full_name']} ({stu['student_id']})", institute_id=req.institute_id, branch_id=req.branch_id, student_id=stu['student_id'])
    return {"success": True, "data": stu, "parsed_profile": parsed}

@app.get("/api/courses")
def api_get_courses(branch_id: str):
    return {"success": True, "data": get_courses_by_branch(branch_id)}

@app.post("/api/courses")
async def create_course_endpoint(payload: dict):
    try:
        print("[DEBUG] Incoming Course Creation Payload:", payload)
        
        course_id = payload.get("id") or f"CRS-{uuid.uuid4().hex[:6].upper()}"
        inst_id = str(payload.get("institute_id", "")).strip()
        branch_id = str(payload.get("branch_id", "")).strip()
        course_name = str(payload.get("course_name", "Untitled Course")).strip()
        course_description = str(payload.get("course_description", "") or payload.get("curriculum_summary", "")).strip()
        default_mcq_count = int(payload.get("default_mcq_count", 10))

        # Normalize modules and skills to clean comma-separated strings
        raw_modules = payload.get("curriculum_sections", "")
        if isinstance(raw_modules, list):
            curriculum_sections_str = ", ".join(str(m) for m in raw_modules)
        else:
            curriculum_sections_str = str(raw_modules)

        raw_skills = payload.get("core_skills", "")
        if isinstance(raw_skills, list):
            core_skills_str = ", ".join(str(s) for s in raw_skills)
        else:
            core_skills_str = str(raw_skills)

        # Execute SQLite Insert with explicit lock timeout and foreign key safety
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verify branch and institute exist or fallback cleanly to prevent FK crash
        if inst_id:
            cursor.execute("SELECT id FROM institutes WHERE id = ?", (inst_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT OR IGNORE INTO institutes (id, name, code) VALUES (?, ?, ?)", 
                               (inst_id, "Default Institute Network", inst_id))

        if branch_id:
            cursor.execute("SELECT id FROM branches WHERE id = ?", (branch_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT OR IGNORE INTO branches (id, institute_id, branch_name, city) VALUES (?, ?, ?, ?)", 
                               (branch_id, inst_id or "INST-GLOBAL-01", "Main Center Node", "Delhi"))

        # Insert Course
        cursor.execute("""
            INSERT INTO courses (
                id, institute_id, branch_id, course_name, curriculum_summary,
                course_description, curriculum_sections, core_skills, default_mcq_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_id, inst_id, branch_id, course_name, course_description,
            course_description, curriculum_sections_str, core_skills_str, default_mcq_count
        ))
        conn.commit()
        conn.close()

        print(f"[SUCCESS] Course {course_id} created successfully.")
        return {
            "status": "success",
            "success": True,
            "course_id": course_id,
            "course_name": course_name,
            "data": {
                "id": course_id,
                "course_name": course_name,
                "curriculum_sections": curriculum_sections_str,
                "core_skills": core_skills_str
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Backend Error: {str(e)}")

@app.post("/api/courses/create")
def api_create_course(req: CourseCreateReq):
    from agent_engine import enrich_and_synthesize_course_input
    from database import log_agent_activity
    
    sections_raw = req.curriculum_sections
    if isinstance(sections_raw, list):
        sections_str = ", ".join(sections_raw)
    else:
        sections_str = str(sections_raw or "")

    skills_raw = req.core_skills
    if isinstance(skills_raw, list):
        skills_str = ", ".join(skills_raw)
    else:
        skills_str = str(skills_raw or "")

    # Run Gemini 3.5 AI Auto-Correction & Curriculum Enrichment
    enriched = enrich_and_synthesize_course_input(
        req.course_name, req.course_description or "", sections_str, skills_str
    )
    
    final_title = enriched.get("course_title", req.course_name)
    final_desc = enriched.get("course_description", req.course_description or req.curriculum_summary)
    final_sections = json.dumps(enriched.get("curriculum_sections", [])) if isinstance(enriched.get("curriculum_sections"), list) else str(enriched.get("curriculum_sections", sections_str))
    final_skills = json.dumps(enriched.get("core_skills", [])) if isinstance(enriched.get("core_skills"), list) else str(enriched.get("core_skills", skills_str))
    
    course = create_course(
        req.institute_id, req.branch_id, final_title, final_desc,
        final_desc, final_sections, final_skills, req.default_mcq_count
    )
    log_agent_activity("COURSE_AI_SYNTHESIZED", f"Gemini 3.5 Auto-Corrected & Synthesized course '{final_title}'", institute_id=req.institute_id, branch_id=req.branch_id)
    return {"success": True, "status": "success", "data": course, "enriched": enriched}

@app.put("/api/courses/{course_id}")
@app.post("/api/courses/update")
def api_update_course(course_id: Optional[str] = None, payload: Optional[Union[CourseUpdateReq, dict]] = None):
    try:
        if isinstance(payload, BaseModel):
            p_dict = payload.model_dump()
        else:
            p_dict = payload or {}

        target_id = str(course_id or p_dict.get("course_id") or p_dict.get("id") or "").strip()
        if not target_id:
            return {"status": "error", "success": False, "message": "Missing course_id parameter."}

        c_name = str(p_dict.get("course_name") or p_dict.get("title") or p_dict.get("course_title") or "Untitled Course").strip()
        topic = str(p_dict.get("topic") or "").strip()
        c_desc = str(p_dict.get("course_description") or p_dict.get("curriculum_summary") or topic or "").strip()
        
        modules = p_dict.get("curriculum_sections") or p_dict.get("modules") or []
        skills = p_dict.get("core_skills") or []
        mcqs = p_dict.get("mcqs") or []
        mcq_cnt = int(p_dict.get("default_mcq_count") or p_dict.get("num_mcqs") or (len(mcqs) if isinstance(mcqs, list) and mcqs else 10))

        from database import update_course, log_agent_activity
        updated = update_course(
            course_id=target_id,
            course_name=c_name,
            curriculum_summary=c_desc,
            course_description=c_desc,
            curriculum_sections=modules,
            core_skills=skills,
            default_mcq_count=mcq_cnt
        )

        log_agent_activity("COURSE_UPDATED", f"Updated course '{c_name}' ({target_id})")
        return {"status": "success", "success": True, "message": "Course updated successfully.", "course": updated, "data": updated}
    except Exception as e:
        print(f"[COURSE UPDATE EXCEPTION] {e}")
        return {"status": "error", "success": False, "message": f"Failed to update course: {str(e)}"}

@app.delete("/api/courses/{course_id}")
def api_delete_course(course_id: str):
    try:
        target_id = str(course_id).strip()
        from database import delete_course, get_course_by_id, log_agent_activity
        
        existing = get_course_by_id(target_id)
        if not existing:
            return {"status": "error", "success": False, "message": f"Course {target_id} not found."}

        delete_course(target_id)
        log_agent_activity("COURSE_DELETED", f"Deleted course {target_id}")
        return {"status": "success", "success": True, "message": f"Course {target_id} deleted successfully."}
    except Exception as e:
        print(f"[COURSE DELETE EXCEPTION] {e}")
        return {"status": "error", "success": False, "message": f"Failed to delete course: {str(e)}"}

# 2. Student Enrollment & CSV Bulk Upload
@app.get("/api/students")
def api_get_students(institute_id: Optional[str] = None, branch_id: Optional[str] = None):
    return {"success": True, "data": get_all_students(institute_id, branch_id)}

@app.post("/api/students")
async def register_single_student(payload: dict, request: Request = None):
    try:
        print("[DEBUG] Incoming Student Registration Payload:", payload)
        base = get_base_url(request)
        student_id = payload.get("student_id") or f"STU-{uuid.uuid4().hex[:6].upper()}"
        inst_id = str(payload.get("institute_id", "")).strip()
        branch_id = str(payload.get("branch_id", "")).strip()
        course_id = str(payload.get("course_id", "")).strip()
        branch_name = str(payload.get("branch_name", "Main Center Node")).strip()
        course_name = str(payload.get("course_name", "Vocational Course")).strip()
        full_name = str(payload.get("full_name", "Enrolled Candidate")).strip()
        dob = str(payload.get("dob", "2000-01-01")).strip()
        email = str(payload.get("email", f"{student_id.lower()}@skillforge.internal")).strip()
        phone = str(payload.get("phone", "+91 9876543210")).strip()
        bio = str(payload.get("bio", "Enrolled vocational candidate specializing in practical diagnostics.")).strip()
        github_url = str(payload.get("github_url", "https://github.com")).strip()
        portfolio_url = str(payload.get("portfolio_url") or f"{base}/portfolio/{student_id}").strip()
        target_role = str(payload.get("target_role_preference", "Specialist Engineer")).strip()
        
        skills_raw = payload.get("skills_list", "")
        if isinstance(skills_raw, list):
            skills_list_str = ", ".join(skills_raw)
        else:
            skills_list_str = str(skills_raw)

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Ensure foreign key records exist to avoid silent constraint drops
        if inst_id:
            cursor.execute("INSERT OR IGNORE INTO institutes (id, name, code) VALUES (?, ?, ?)", (inst_id, "Default Institute Network", inst_id))
        if branch_id:
            cursor.execute("INSERT OR IGNORE INTO branches (id, institute_id, branch_name, city) VALUES (?, ?, ?, ?)", (branch_id, inst_id or "INST-GLOBAL-01", branch_name, "Delhi"))
        if course_id:
            cursor.execute("INSERT OR IGNORE INTO courses (id, institute_id, branch_id, course_name) VALUES (?, ?, ?, ?)", (course_id, inst_id or "INST-GLOBAL-01", branch_id or "BR-NANGLOI", course_name))

        cursor.execute("""
            INSERT OR REPLACE INTO students (
                student_id, institute_id, branch_id, course_id,
                branch_name, course_name, full_name, dob, email, phone,
                bio, github_url, portfolio_url, target_role_preference,
                skills_list, past_companies_text, work_experience_years,
                fees_status, consent_given, exam_completed, portfolio_generated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, inst_id, branch_id, course_id,
            branch_name, course_name, full_name, dob, email, phone,
            bio, github_url, portfolio_url, target_role,
            skills_list_str, "N/A", 0, "PAID", 1, 0, 0
        ))
        conn.commit()
        conn.close()

        from database import log_agent_activity
        log_agent_activity("STUDENT_ENROLLED", f"Registered single candidate {full_name} ({student_id})", institute_id=inst_id, branch_id=branch_id, student_id=student_id)

        print(f"[SUCCESS] Student {student_id} ({full_name}) registered successfully.")
        return {
            "status": "success",
            "success": True,
            "student_id": student_id,
            "full_name": full_name,
            "course_name": course_name,
            "data": {
                "student_id": student_id,
                "full_name": full_name,
                "course_name": course_name
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database Insertion Failed: {str(e)}")

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
    from database import log_agent_activity
    log_agent_activity("STUDENT_ENROLLED", f"Enrolled candidate {stu['full_name']} ({stu['student_id']}) to {stu['branch_name']}", institute_id=stu['institute_id'], branch_id=stu['branch_id'], student_id=stu['student_id'])
    return {"success": True, "status": "success", "data": stu}

def normalize_dob(dob_raw: Any) -> str:
    """Normalizes DOB string (YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD, etc.) into YYYY-MM-DD format."""
    if not dob_raw:
        return ""
    cleaned = re.sub(r'[\s/.]+', '-', str(dob_raw).strip())
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return cleaned

@app.post("/api/auth/student-login")
@app.post("/api/student/verify-login")
def api_verify_student_login(payload: Union[StudentLoginRequest, dict]):
    try:
        if isinstance(payload, BaseModel):
            p_dict = payload.model_dump()
        else:
            p_dict = payload or {}

        s_id = str(p_dict.get("student_id") or p_dict.get("id") or "").strip()
        raw_dob = str(p_dict.get("dob") or "").strip()
        normalized_dob = normalize_dob(raw_dob)

        if not s_id or not raw_dob:
            return {
                "authenticated": False,
                "success": False,
                "status": "error",
                "message": "Student ID and Date of Birth are required.",
                "data": None
            }

        from database import verify_student_login
        stu = verify_student_login(s_id, raw_dob)

        if stu:
            exam_completed = bool(stu.get("exam_completed") or stu.get("mcq_score") or (stu.get("status_seal") and stu.get("status_seal") != "PENDING"))
            try:
                conn_chk = get_db_connection()
                c_chk = conn_chk.cursor()
                c_chk.execute("SELECT COUNT(*) FROM evaluations WHERE student_id = ? OR CAST(student_id AS TEXT) = ?", (str(s_id), str(s_id)))
                if c_chk.fetchone()[0] > 0:
                    exam_completed = True
                conn_chk.close()
            except Exception:
                pass

            student_out = {
                "id": stu.get("student_id") or stu.get("id") or s_id,
                "student_id": stu.get("student_id") or stu.get("id") or s_id,
                "name": stu.get("full_name") or stu.get("name") or "Candidate",
                "full_name": stu.get("full_name") or stu.get("name") or "Candidate",
                "dob": normalized_dob,
                "track": stu.get("course_name") or stu.get("track") or "General Track",
                "course_name": stu.get("course_name") or stu.get("track") or "General Track",
                "branch_name": stu.get("branch_name", "Main Center"),
                "email": stu.get("email", ""),
                "exam_completed": exam_completed
            }
            return {
                "authenticated": True,
                "success": True,
                "status": "success",
                "message": "Authentication successful",
                "student": student_out,
                "data": stu,
                "exam_completed": exam_completed
            }
        else:
            return {
                "authenticated": False,
                "success": False,
                "status": "error",
                "message": f"Authentication failed. Student ID '{s_id}' or Date of Birth ('{raw_dob}') does not match official record.",
                "data": None
            }
    except Exception as e:
        print(f"[AUTH EXCEPTION] {e}")
        return {
            "authenticated": False,
            "success": False,
            "status": "error",
            "message": f"Auth Server Exception: {str(e)}",
            "data": None
        }

@app.post("/api/admin/reset-database")
def api_reset_database():
    try:
        from database import reset_database_clean_slate, log_agent_activity
        res = reset_database_clean_slate()
        log_agent_activity("DATABASE_PURGED", "Admin executed clean-slate total database purge and schema re-initialization.")
        return {"status": "success", "success": True, "message": "Database completely purged and clean schema initialized."}
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e)}

@app.put("/api/students/{student_id}")
@app.post("/api/students/{student_id}/update")
def api_update_student_record(student_id: str, payload: Union[StudentAdminUpdateReq, dict]):
    from database import update_student_profile, get_student_by_id, log_agent_activity, normalize_dob
    if isinstance(payload, BaseModel):
        p_dict = payload.model_dump()
    else:
        p_dict = payload or {}

    clean_name = p_dict.get("full_name") or p_dict.get("name") or "Enrolled Candidate"
    clean_dob = normalize_dob(p_dict.get("dob") or "")
    clean_email = p_dict.get("email", "")
    clean_phone = p_dict.get("phone", "")
    clean_city = p_dict.get("city") or p_dict.get("branch_center") or ""
    clean_bio = p_dict.get("bio") or p_dict.get("experience_summary") or ""
    clean_github = p_dict.get("github_url", "")
    clean_linkedin = p_dict.get("linkedin_url", "")
    clean_website = p_dict.get("website_url", "")
    clean_twitter = p_dict.get("twitter_url", "")
    clean_exp_years = int(p_dict.get("work_experience_years", 0))

    stu = update_student_profile(
        student_id=student_id,
        full_name=clean_name,
        email=clean_email,
        phone=clean_phone,
        bio=clean_bio,
        github_url=clean_github,
        skills_list=p_dict.get("skills_list", ""),
        target_role_preference=p_dict.get("target_role_preference", ""),
        past_companies_text=p_dict.get("past_companies_text") or clean_bio,
        work_experience_years=clean_exp_years,
        dob=clean_dob,
        city=clean_city,
        linkedin_url=clean_linkedin,
        website_url=clean_website,
        twitter_url=clean_twitter
    )

    try:
        from dossier_generator import generate_candidate_dossier_html
        if stu:
            generate_candidate_dossier_html(stu)
    except Exception as ex:
        print(f"[DOSSIER REGEN WARNING] {ex}")

    log_agent_activity("STUDENT_RECORD_UPDATED", f"Institutional Admin updated candidate record for {clean_name} ({student_id})", student_id=student_id)
    return {"status": "success", "success": True, "message": "Candidate profile updated successfully", "data": stu, "student": stu}

@app.post("/api/student/update-profile")
def api_update_student_profile(req: StudentUpdateProfileReq):
    from database import update_student_profile, log_agent_activity
    stu = update_student_profile(
        req.student_id, req.full_name, req.email, req.phone, req.bio,
        req.github_url, req.skills_list, req.target_role_preference, req.past_companies_text, req.work_experience_years,
        req.dob, req.city, req.linkedin_url, req.website_url, req.twitter_url
    )
    log_agent_activity("PROFILE_UPDATED", f"Candidate {req.full_name} updated career preferences & skills", student_id=req.student_id)
    return {"success": True, "data": stu}

@app.post("/api/student/parse-resume")
async def api_parse_student_resume(file: UploadFile = File(...)):
    from agent_engine import parse_pdf_resume_with_gemini
    pdf_bytes = await file.read()
    extracted = parse_pdf_resume_with_gemini(pdf_bytes, filename=file.filename)
    return {"success": True, "data": extracted}

@app.delete("/api/student/{student_id}")
def api_delete_student(student_id: str):
    from database import delete_student, log_agent_activity
    delete_student(student_id)
    log_agent_activity("STUDENT_DELETED", f"Candidate {student_id} removed from roster", student_id=student_id)
    return {"success": True, "message": f"Student {student_id} deleted."}

@app.get("/api/agent/logs")
def api_get_agent_logs(branch_id: Optional[str] = None, institute_id: Optional[str] = None):
    from database import get_agent_activity_logs
    return {"success": True, "data": get_agent_activity_logs(branch_id, institute_id)}

@app.post("/api/students/consent")
def api_set_consent(req: StudentConsentReq):
    set_student_consent(req.student_id, req.consent)
    return {"success": True, "data": get_student_by_id(req.student_id)}

class JobApplyReq(BaseModel):
    student_id: str
    company_name: str
    role_title: str
    match_percentage: int = 85
    dossier_sent_url: str = ""

class AutoApplyReq(BaseModel):
    student_id: str
    auto_apply_mode: bool

class JobMatchReq(BaseModel):
    student_id: Optional[str] = "STU-1001"
    track: Optional[str] = "Full Stack Web Development"
    skills: Optional[List[str]] = None
    location: Optional[str] = "Delhi NCR / India"
    page: int = 1
    page_size: int = 30

@app.post("/api/jobs/match")
def api_match_jobs(req: JobMatchReq):
    try:
        from job_engine import crawl_live_grounded_jobs
        crawled_list = crawl_live_grounded_jobs(
            track=req.track or "Full Stack Web Development",
            skills=req.skills,
            location=req.location or "Delhi NCR / India",
            page=req.page,
            page_size=req.page_size
        )
        return {
            "status": "success",
            "success": True,
            "page": req.page,
            "page_size": req.page_size,
            "count": len(crawled_list),
            "jobs": crawled_list,
            "data": crawled_list
        }
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e), "jobs": [], "data": []}

@app.get("/api/jobs/discover")
def api_discover_jobs(
    course_name: str = "",
    query: str = "",
    city: str = "",
    min_match: int = 0
):
    try:
        from job_engine import search_live_jobs
        jobs = search_live_jobs(course_name=course_name, search_query=query, city=city, min_match_score=min_match)
        return {"status": "success", "success": True, "count": len(jobs), "data": jobs}
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e), "data": []}

@app.post("/api/jobs/apply")
def api_apply_job(req: JobApplyReq):
    try:
        from database import record_job_application, log_agent_activity
        app_id = record_job_application(
            student_id=req.student_id,
            company_name=req.company_name,
            role_title=req.role_title,
            match_percentage=req.match_percentage,
            dossier_sent_url=req.dossier_sent_url
        )
        log_agent_activity(
            "JOB_APPLICATION_DISPATCHED",
            f"1-Click AI Dossier dispatched to {req.company_name} for role '{req.role_title}' ({req.match_percentage}% match)",
            student_id=req.student_id
        )
        return {"status": "success", "success": True, "application_id": app_id, "message": f"Dossier dispatched to {req.company_name}"}
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e)}

@app.post("/api/students/auto-apply-mode")
def api_toggle_auto_apply(req: AutoApplyReq):
    try:
        from database import get_db_connection, log_agent_activity
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE students SET auto_apply_mode = ? WHERE student_id = ?", (1 if req.auto_apply_mode else 0, req.student_id))
            conn.commit()
        log_agent_activity(
            "AUTO_APPLY_TOGGLED",
            f"Autonomous Auto-Apply Engine set to {'ACTIVE' if req.auto_apply_mode else 'INACTIVE'}",
            student_id=req.student_id
        )
        return {"status": "success", "success": True, "auto_apply_mode": req.auto_apply_mode}
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e)}

from fastapi.responses import FileResponse, HTMLResponse

os.makedirs(os.path.join("backend", "resumes"), exist_ok=True)

@app.get("/api/students/{student_id}/resume")
async def download_student_resume(student_id: str):
    pdf_path = os.path.join("backend", "resumes", f"{student_id}_resume.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"{student_id}_Resume.pdf")
    raise HTTPException(status_code=404, detail="Resume PDF not uploaded yet.")

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
        from database import get_institute_by_id, log_agent_activity
        inst = get_institute_by_id(req.institute_id)
        num_q = req.num_questions or (inst.get("num_mcqs_config", 10) if inst else 10)
        exam = generate_assessment(req.topic, req.difficulty, req.institute_id, num_questions=num_q)
        log_agent_activity("ASSESSMENT_SYNTHESIZED", f"Assessment Synthesized for Course: {req.topic} (Questions: {len(exam.get('mcqs', []))})", institute_id=req.institute_id)
        return {"success": True, "data": exam}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Student Submission & Autonomous Background Dispatcher
@app.post("/api/student/evaluate-and-dispatch")
def api_student_pipeline(req: FullEvaluationReq, request: Request = None):
    try:
        base = get_base_url(request)
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
            image_base64=req.image_base64,
            base_url=base
        )
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Job Applications Ledger
@app.get("/api/placements/ledger")
def api_get_placements(branch_id: Optional[str] = None):
    return {"success": True, "data": get_job_applications(branch_id)}

class StudentAutoApplyReq(BaseModel):
    student_id: str
    auto_apply_mode: bool

class StudentRetestReq(BaseModel):
    student_id: str

class JobApplyReq(BaseModel):
    student_id: str
    company_name: str
    role_title: str
    match_percentage: int
    dossier_sent_url: Optional[str] = ''

@app.post("/api/jobs/apply")
def api_apply_job(req: JobApplyReq, request: Request = None):
    from database import record_job_application, log_agent_activity, get_student_by_id
    base = get_base_url(request)
    stu = get_student_by_id(req.student_id)
    b_id = stu['branch_id'] if stu else None
    app_id = record_job_application(
        student_id=req.student_id,
        company_name=req.company_name,
        role_title=req.role_title,
        match_percentage=req.match_percentage,
        dossier_sent_url=req.dossier_sent_url or f"{base}/portfolio/{req.student_id}",
        status="APPLIED_AND_DISPATCHED",
        interview_details="Application Dispatched via AI Career Agent"
    )
    log_agent_activity("JOB_APPLICATION_DISPATCHED", f"Application submitted for {req.company_name} ({req.role_title})", branch_id=b_id, student_id=req.student_id)
    return {"success": True, "data": {"application_id": app_id, "status": "APPLIED_AND_DISPATCHED"}}

# Admin Reset Database Clean Slate
@app.post("/api/admin/reset-db")
def api_reset_db_alias():
    from database import reset_database_clean_slate
    reset_database_clean_slate()
    return {"status": "success", "success": True, "message": "Database completely purged and clean schema initialized."}

# 6. Live Job Discovery & Retest Governance Endpoints
@app.get("/api/jobs/discover")
def api_discover_jobs(course_name: str = "Automotive & Hardware Diagnostics", skills: str = "ECU,Multimeter,Oscilloscope"):
    from job_discovery_agent import discover_live_jobs
    skill_list = [s.strip() for s in skills.split(",")]
    jobs = discover_live_jobs(course_name, skill_list)
    return {"success": True, "data": jobs}

@app.post("/api/students/auto-apply-mode")
def api_set_auto_apply_mode(req: StudentAutoApplyReq):
    from database import set_student_auto_apply_mode, get_student_by_id
    set_student_auto_apply_mode(req.student_id, req.auto_apply_mode)
    return {"success": True, "data": get_student_by_id(req.student_id)}

@app.post("/api/students/request-retest")
def api_request_retest(req: StudentRetestReq):
    from database import request_retest, get_student_by_id
    request_retest(req.student_id)
    return {"success": True, "data": get_student_by_id(req.student_id)}

@app.post("/api/students/approve-retest")
def api_approve_retest(req: StudentRetestReq):
    from database import approve_retest, get_student_by_id
    approve_retest(req.student_id)
    return {"success": True, "data": get_student_by_id(req.student_id)}

# 7. Verified Certificate Generator Endpoint
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
