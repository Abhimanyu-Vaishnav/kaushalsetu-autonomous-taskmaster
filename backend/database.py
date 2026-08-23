import os
import json
import sqlite3
import uuid
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillforge.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Institutes Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS institutes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            branches TEXT NOT NULL,          -- JSON list of branch names
            courses TEXT NOT NULL,           -- JSON list of course names
            placement_threshold INTEGER DEFAULT 70,
            max_interviews_cap INTEGER DEFAULT 3,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Students Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            branch_name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            dob TEXT DEFAULT '2002-01-01',
            email TEXT NOT NULL,
            phone TEXT DEFAULT '',
            course_name TEXT NOT NULL,
            fees_status TEXT DEFAULT 'PAID',
            consent_for_job_dispatch INTEGER DEFAULT 0,
            interview_count INTEGER DEFAULT 0,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id)
        )
        """)
        
        # 3. Assessments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            generated_exam TEXT NOT NULL,   -- JSON Gemini 3.5 output (5 MCQs, 1 practical, rubric)
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id)
        )
        """)
        
        # 4. Student Submissions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_submissions (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            assessment_id TEXT NOT NULL,
            submission_text TEXT NOT NULL,
            artifact_image_base64 TEXT,
            gemma_screening_result TEXT NOT NULL, -- JSON
            gemini_evaluation TEXT NOT NULL,       -- JSON
            final_score INTEGER NOT NULL,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(assessment_id) REFERENCES assessments(id)
        )
        """)
        
        # 5. Job Applications Ledger Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            match_percentage INTEGER NOT NULL,
            status TEXT NOT NULL,             -- 'APPLIED_AND_DISPATCHED', 'INTERVIEW_SCHEDULED', 'REMEDIAL_ASSIGNED'
            student_notified INTEGER DEFAULT 1,
            branch_notified INTEGER DEFAULT 1,
            metric_hash TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
        """)
        
        conn.commit()
        
        # Seed initial data if institutes empty
        cursor.execute("SELECT COUNT(*) FROM institutes")
        if cursor.fetchone()[0] == 0:
            seed_initial_data(conn)

def seed_initial_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    inst_id = "INST-GLOBAL-01"
    code = "SKILLFORGE-HQ"
    branches = json.dumps(["Nangloi Center", "Yamuna Vihar Center", "Jwalapur Center"])
    courses = json.dumps([
        "Full Stack Web Development",
        "Accounting & Financial Tally",
        "Automotive & Hardware Diagnostics"
    ])
    
    cursor.execute("""
        INSERT OR IGNORE INTO institutes (id, name, code, branches, courses, placement_threshold, max_interviews_cap)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (inst_id, "SkillForge Vocational Foundation", code, branches, courses, 70, 3))
    
    students = [
        ("STU-1001", inst_id, "Nangloi Center", "Alex Mercer", "2002-01-15", "alex.mercer@skillforge-edu.org", "+91 9876543210", "Automotive & Hardware Diagnostics", "PAID", 1, 0),
        ("STU-1002", inst_id, "Nangloi Center", "Priya Sundaram", "2001-05-20", "priya.s@skillforge-edu.org", "+91 9876543211", "Full Stack Web Development", "PAID", 1, 0),
        ("STU-1003", inst_id, "Yamuna Vihar Center", "Jordan Smith", "2000-11-10", "jordan.s@skillforge-edu.org", "+91 9876543212", "Accounting & Financial Tally", "PAID", 1, 0),
        ("STU-1004", inst_id, "Jwalapur Center", "Amitabh Choudhury", "1999-08-04", "amitabh.c@skillforge-edu.org", "+91 9876543213", "Automotive & Hardware Diagnostics", "PAID", 1, 0)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO students (student_id, institute_id, branch_name, full_name, dob, email, phone, course_name, fees_status, consent_for_job_dispatch, interview_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, students)
    
    conn.commit()

# --- Helper Functions ---

def get_all_institutes() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institutes ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            r["branches"] = json.loads(r["branches"])
            r["courses"] = json.loads(r["courses"])
        return rows

def get_institute(inst_id: str = "INST-GLOBAL-01") -> Dict[str, Any]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institutes WHERE id = ?", (inst_id,))
        row = cursor.fetchone()
        if row:
            res = dict(row)
            res["branches"] = json.loads(res["branches"])
            res["courses"] = json.loads(res["courses"])
            return res
        return {}

def update_institute_config(inst_id: str, threshold: int, cap_limit: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE institutes SET placement_threshold = ?, max_interviews_cap = ? WHERE id = ?
        """, (threshold, cap_limit, inst_id))
        conn.commit()
        return True

def create_institute(name: str, code: str, branches: List[str], courses: List[str], threshold: int = 70, cap: int = 3) -> Dict[str, Any]:
    inst_id = f"INST-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO institutes (id, name, code, branches, courses, placement_threshold, max_interviews_cap)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (inst_id, name, code, json.dumps(branches), json.dumps(courses), threshold, cap))
        conn.commit()
    return get_institute(inst_id)

def get_all_students(institute_id: Optional[str] = None, branch_name: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if institute_id and branch_name:
            cursor.execute("SELECT * FROM students WHERE institute_id = ? AND branch_name = ? ORDER BY registered_at DESC", (institute_id, branch_name))
        elif institute_id:
            cursor.execute("SELECT * FROM students WHERE institute_id = ? ORDER BY registered_at DESC", (institute_id,))
        else:
            cursor.execute("SELECT * FROM students ORDER BY registered_at DESC")
        return [dict(r) for r in cursor.fetchall()]

def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_student(institute_id: str, branch_name: str, full_name: str, email: str, phone: str, course_name: str, dob: str = "2002-01-01", fees_status: str = "PAID", consent: int = 1) -> Dict[str, Any]:
    student_id = f"STU-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (student_id, institute_id, branch_name, full_name, dob, email, phone, course_name, fees_status, consent_for_job_dispatch, interview_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (student_id, institute_id, branch_name, full_name, dob, email, phone, course_name, fees_status, consent))
        conn.commit()
    return get_student_by_id(student_id)

def set_student_consent(student_id: str, consent: bool) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET consent_for_job_dispatch = ? WHERE student_id = ?", (1 if consent else 0, student_id))
        conn.commit()
        return True

def get_assessments(institute_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if institute_id:
            cursor.execute("SELECT * FROM assessments WHERE institute_id = ? ORDER BY created_at DESC", (institute_id,))
        else:
            cursor.execute("SELECT * FROM assessments ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            r["generated_exam"] = json.loads(r["generated_exam"])
        return rows

def save_assessment(institute_id: str, course_name: str, difficulty: str, generated_exam: Dict[str, Any]) -> str:
    ass_id = f"ASS-{uuid.uuid4().hex[:8].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assessments (id, institute_id, course_name, difficulty, generated_exam)
            VALUES (?, ?, ?, ?, ?)
        """, (ass_id, institute_id, course_name, difficulty, json.dumps(generated_exam)))
        conn.commit()
    return ass_id

def get_job_applications() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.*, s.full_name as student_name, s.email as student_email, s.branch_name
            FROM job_applications j
            JOIN students s ON j.student_id = s.student_id
            ORDER BY j.timestamp DESC
        """)
        return [dict(r) for r in cursor.fetchall()]

# Initialize DB on import
init_db()
