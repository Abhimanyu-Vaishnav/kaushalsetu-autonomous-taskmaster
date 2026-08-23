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
            branches TEXT NOT NULL,          -- JSON list of branches
            courses_offered TEXT NOT NULL,   -- JSON list of courses
            interview_cap_limit INTEGER DEFAULT 3,
            dispatch_threshold INTEGER DEFAULT 70
        )
        """)
        
        # 2. Students Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            fees_status TEXT DEFAULT 'PAID',
            consent_given INTEGER DEFAULT 1,
            interview_count INTEGER DEFAULT 0
        )
        """)
        
        # 3. Assessments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            generated_exam TEXT NOT NULL,   -- JSON Gemini 3.5 output
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 4. Student Submissions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_submissions (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            assessment_id TEXT NOT NULL,
            submission_content TEXT NOT NULL,
            image_base64 TEXT,
            gemma_score INTEGER NOT NULL,
            gemini_evaluation TEXT NOT NULL, -- JSON evaluation output
            total_score INTEGER NOT NULL,
            placement_ready INTEGER NOT NULL,
            evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(assessment_id) REFERENCES assessments(id)
        )
        """)
        
        # 5. Job Applications Ledger Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            hiring_partner TEXT NOT NULL,
            role TEXT NOT NULL,
            match_score INTEGER NOT NULL,
            status TEXT NOT NULL,             -- 'DISPATCHED', 'INTERVIEW_SCHEDULED', 'OFFER_MADE'
            interview_count INTEGER DEFAULT 1,
            metric_hash TEXT NOT NULL,
            dispatched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    
    # Default Institute
    inst_id = "INST-GLOBAL-01"
    branches = json.dumps([
        {"branch_id": "BR-DEL-01", "name": "Nangloi Center", "city": "Delhi North-West"},
        {"branch_id": "BR-DEL-02", "name": "Yamuna Vihar Center", "city": "Delhi East"},
        {"branch_id": "BR-HAR-01", "name": "Jwalapur Center", "city": "Haridwar"}
    ])
    courses = json.dumps([
        "Full Stack Web Development",
        "Accounting & Financial Tally",
        "Automotive & Hardware Diagnostics"
    ])
    
    cursor.execute("""
        INSERT OR IGNORE INTO institutes (id, name, branches, courses_offered, interview_cap_limit, dispatch_threshold)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (inst_id, "SkillForge Vocational Foundation", branches, courses, 3, 70))
    
    # Default Students
    students = [
        ("STU-1001", "Alex Mercer", "alex.mercer@skillforge-edu.org", "BR-DEL-01", "Automotive & Hardware Diagnostics", "PAID", 1, 0),
        ("STU-1002", "Priya Sundaram", "priya.s@skillforge-edu.org", "BR-DEL-01", "Full Stack Web Development", "PAID", 1, 0),
        ("STU-1003", "Jordan Smith", "jordan.s@skillforge-edu.org", "BR-DEL-02", "Accounting & Financial Tally", "PAID", 1, 0),
        ("STU-1004", "Amitabh Choudhury", "amitabh.c@skillforge-edu.org", "BR-HAR-01", "Automotive & Hardware Diagnostics", "PAID", 1, 0)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO students (student_id, full_name, email, branch_id, course_name, fees_status, consent_given, interview_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, students)
    
    conn.commit()

# --- Helper Query Functions ---

def get_institute(inst_id: str = "INST-GLOBAL-01") -> Dict[str, Any]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institutes WHERE id = ?", (inst_id,))
        row = cursor.fetchone()
        if row:
            res = dict(row)
            res["branches"] = json.loads(res["branches"])
            res["courses_offered"] = json.loads(res["courses_offered"])
            return res
        return {}

def update_institute_config(inst_id: str, threshold: int, cap_limit: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE institutes SET dispatch_threshold = ?, interview_cap_limit = ? WHERE id = ?
        """, (threshold, cap_limit, inst_id))
        conn.commit()
        return True

def get_all_students() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY student_id ASC")
        return [dict(r) for r in cursor.fetchall()]

def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_student(full_name: str, email: str, branch_id: str, course_name: str, fees_status: str = "PAID", consent_given: int = 1) -> Dict[str, Any]:
    student_id = f"STU-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (student_id, full_name, email, branch_id, course_name, fees_status, consent_given, interview_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (student_id, full_name, email, branch_id, course_name, fees_status, consent_given))
        conn.commit()
    return get_student_by_id(student_id)

def get_assessments() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
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
        cursor.execute("SELECT * FROM job_applications ORDER BY dispatched_at DESC")
        return [dict(r) for r in cursor.fetchall()]

# Initialize DB on load
init_db()
