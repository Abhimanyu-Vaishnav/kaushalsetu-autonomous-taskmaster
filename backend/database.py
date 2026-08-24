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
            num_mcqs_config INTEGER DEFAULT 10,
            placement_threshold INTEGER DEFAULT 70,
            max_interviews_cap INTEGER DEFAULT 3,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Branches Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS branches (
            id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            branch_name TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id)
        )
        """)
        
        # 3. Courses Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            curriculum_summary TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id),
            FOREIGN KEY(branch_id) REFERENCES branches(id)
        )
        """)
        
        # 4. Students Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            branch_name TEXT NOT NULL,
            course_name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            dob TEXT DEFAULT '2002-01-01',
            email TEXT NOT NULL,
            phone TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            github_url TEXT DEFAULT '',
            portfolio_url TEXT DEFAULT '',
            project_zip_path TEXT DEFAULT '',
            fees_status TEXT DEFAULT 'PAID',
            consent_given INTEGER DEFAULT 0,
            consent_for_job_dispatch INTEGER DEFAULT 0,
            auto_apply_mode INTEGER DEFAULT 0,     -- Default 0 (OFF) as requested
            exam_completed INTEGER DEFAULT 0,
            portfolio_generated INTEGER DEFAULT 0,
            retest_requested INTEGER DEFAULT 0,
            retest_approved INTEGER DEFAULT 0,
            interview_count INTEGER DEFAULT 0,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id),
            FOREIGN KEY(branch_id) REFERENCES branches(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """)
        
        # 5. Assessments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            generated_exam TEXT NOT NULL,   -- JSON Gemini 3.5 output
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id)
        )
        """)
        
        # 6. Student Submissions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_submissions (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            assessment_id TEXT NOT NULL,
            mcq_answers TEXT,              -- JSON
            mcq_score REAL DEFAULT 0.0,
            practical_submission_text TEXT NOT NULL,
            practical_score REAL DEFAULT 0.0,
            total_score INTEGER NOT NULL,
            strengths TEXT,                -- JSON
            skill_gaps TEXT,               -- JSON
            artifact_image_base64 TEXT,
            gemma_screening_result TEXT NOT NULL, -- JSON
            gemini_evaluation TEXT NOT NULL,       -- JSON
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(assessment_id) REFERENCES assessments(id)
        )
        """)
        
        # 7. Autonomous Job Applications Ledger Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            match_percentage INTEGER NOT NULL,
            dossier_sent_url TEXT DEFAULT '',
            status TEXT NOT NULL,             -- 'DISPATCHED', 'INTERVIEW_SCHEDULED', 'NEEDS_HUMAN_INTERVENTION', 'REMEDIAL_ASSIGNED'
            interview_details TEXT DEFAULT '',
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
    inst_name = "SkillForge Vocational Foundation"
    
    cursor.execute("""
        INSERT OR IGNORE INTO institutes (id, name, code, placement_threshold, max_interviews_cap)
        VALUES (?, ?, ?, ?, ?)
    """, (inst_id, inst_name, code, 70, 3))
    
    branches_data = [
        ("BR-NANGLOI", inst_id, "Nangloi Center", "Delhi"),
        ("BR-YAMUNAVIHAR", inst_id, "Yamuna Vihar Center", "Delhi"),
        ("BR-JWALAPUR", inst_id, "Jwalapur Center", "Haridwar")
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO branches (id, institute_id, branch_name, city)
        VALUES (?, ?, ?, ?)
    """, branches_data)
    
    courses_data = [
        ("CRS-AUTO-01", inst_id, "BR-NANGLOI", "Automotive & Hardware Diagnostics", "Automotive ECU diagnostics & oscilloscope waveform analysis"),
        ("CRS-WEB-01", inst_id, "BR-NANGLOI", "Full Stack Web Development", "React, Node.js, Python FastAPI & SQLite full stack SaaS engineering"),
        ("CRS-TALLY-01", inst_id, "BR-YAMUNAVIHAR", "Accounting & Financial Tally", "GST tax compliance, corporate ledger auditing & Tally ERP"),
        ("CRS-AUTO-02", inst_id, "BR-JWALAPUR", "Automotive & Hardware Diagnostics", "Industrial vehicle diagnostics & sensor splice repair")
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO courses (id, institute_id, branch_id, course_name, curriculum_summary)
        VALUES (?, ?, ?, ?, ?)
    """, courses_data)
    
    students_data = [
        ("STU-1001", inst_id, "BR-NANGLOI", "CRS-AUTO-01", "Nangloi Center", "Automotive & Hardware Diagnostics", "Alex Mercer", "2002-01-15", "alex.mercer@skillforge-edu.org", "+91 9876543210", "Automotive technician candidate specializing in ECU waveform diagnostics", "https://github.com/skillforge/alex-mercer", "", "", "PAID", 1, 1, 0, 0, 0),
        ("STU-1002", inst_id, "BR-NANGLOI", "CRS-WEB-01", "Nangloi Center", "Full Stack Web Development", "Priya Sundaram", "2001-05-20", "priya.s@skillforge-edu.org", "+91 9876543211", "Full stack developer proficient in React and Python backend architectures", "https://github.com/skillforge/priya-web", "", "", "PAID", 1, 1, 0, 0, 0),
        ("STU-1003", inst_id, "BR-YAMUNAVIHAR", "CRS-TALLY-01", "Yamuna Vihar Center", "Accounting & Financial Tally", "Jordan Smith", "2000-11-10", "jordan.s@skillforge-edu.org", "+91 9876543212", "Financial tally accountant with GST compliance verification expertise", "", "", "", "PAID", 1, 1, 0, 0, 0),
        ("STU-1004", inst_id, "BR-JWALAPUR", "CRS-AUTO-02", "Jwalapur Center", "Automotive & Hardware Diagnostics", "Amitabh Choudhury", "1999-08-04", "amitabh.c@skillforge-edu.org", "+91 9876543213", "Diagnostics engineer trained on heavy electrical wiring & safety lockout", "", "", "", "PAID", 1, 1, 0, 0, 0)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO students 
        (student_id, institute_id, branch_id, course_id, branch_name, course_name, full_name, dob, email, phone, bio, github_url, portfolio_url, project_zip_path, fees_status, consent_given, consent_for_job_dispatch, exam_completed, portfolio_generated, interview_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, students_data)
    
    conn.commit()

# --- Relational CRUD Helper Functions ---

def get_all_institutes() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institutes ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]

def get_institute_by_id(inst_id: str = "INST-GLOBAL-01") -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institutes WHERE id = ?", (inst_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_institute(inst_id: str = "INST-GLOBAL-01") -> Dict[str, Any]:
    inst = get_institute_by_id(inst_id)
    return inst if inst else {}

def get_institute_by_code(code: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institutes WHERE code = ?", (code,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_institute(name: str, code: str, initial_branch_name: str = "Main Center", initial_city: str = "Delhi", num_mcqs: int = 10, threshold: int = 70, cap: int = 3) -> Dict[str, Any]:
    inst_id = f"INST-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO institutes (id, name, code, num_mcqs_config, placement_threshold, max_interviews_cap)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (inst_id, name, code, num_mcqs, threshold, cap))
        
        # Create mandatory initial branch
        branch_id = f"BR-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute("""
            INSERT INTO branches (id, institute_id, branch_name, city)
            VALUES (?, ?, ?, ?)
        """, (branch_id, inst_id, initial_branch_name, initial_city))
        conn.commit()
    return get_institute_by_id(inst_id)

def update_institute_config(institute_id: str, num_mcqs: int, threshold: int, cap: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE institutes
            SET num_mcqs_config = ?, placement_threshold = ?, max_interviews_cap = ?
            WHERE id = ?
        """, (num_mcqs, threshold, cap, institute_id))
        conn.commit()
    return get_institute_by_id(institute_id)

def get_branches_by_institute(institute_id: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM branches WHERE institute_id = ? ORDER BY created_at DESC", (institute_id,))
        return [dict(r) for r in cursor.fetchall()]

def create_branch(institute_id: str, branch_name: str, city: str) -> Dict[str, Any]:
    branch_id = f"BR-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO branches (id, institute_id, branch_name, city)
            VALUES (?, ?, ?, ?)
        """, (branch_id, institute_id, branch_name, city))
        conn.commit()
    return {"id": branch_id, "institute_id": institute_id, "branch_name": branch_name, "city": city}

def get_courses_by_branch(branch_id: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE branch_id = ? ORDER BY created_at DESC", (branch_id,))
        return [dict(r) for r in cursor.fetchall()]

def create_course(institute_id: str, branch_id: str, course_name: str, curriculum_summary: str = "") -> Dict[str, Any]:
    course_id = f"CRS-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO courses (id, institute_id, branch_id, course_name, curriculum_summary)
            VALUES (?, ?, ?, ?, ?)
        """, (course_id, institute_id, branch_id, course_name, curriculum_summary))
        conn.commit()
    return {"id": course_id, "institute_id": institute_id, "branch_id": branch_id, "course_name": course_name, "curriculum_summary": curriculum_summary}

def get_all_students(institute_id: Optional[str] = None, branch_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if institute_id and branch_id:
            cursor.execute("SELECT * FROM students WHERE institute_id = ? AND branch_id = ? ORDER BY registered_at DESC", (institute_id, branch_id))
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

def add_student(
    institute_id: str,
    branch_id: str,
    course_id: str,
    branch_name: str,
    course_name: str,
    full_name: str,
    dob: str,
    email: str,
    phone: str = "",
    bio: str = "",
    fees_status: str = "PAID",
    consent: int = 1
) -> Dict[str, Any]:
    branch_slug = "".join([c for c in branch_name if c.isalnum()]).upper()
    prefix = branch_slug[:3] if len(branch_slug) >= 3 else "GEN"
    student_id = f"STU-{prefix}-{uuid.uuid4().hex[:4].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students 
            (student_id, institute_id, branch_id, course_id, branch_name, course_name, full_name, dob, email, phone, bio, fees_status, consent_given, consent_for_job_dispatch, exam_completed, portfolio_generated, interview_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
        """, (student_id, institute_id, branch_id, course_id, branch_name, course_name, full_name, dob, email, phone, bio, fees_status, consent, consent))
        conn.commit()
    return get_student_by_id(student_id)

def mark_student_exam_complete(student_id: str, github_url: str = "", portfolio_url: str = "") -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students 
            SET exam_completed = 1, portfolio_generated = 1, github_url = ?, portfolio_url = ?
            WHERE student_id = ?
        """, (github_url, portfolio_url, student_id))
        conn.commit()
        return True

def set_student_consent(student_id: str, consent: bool) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET consent_given = ?, consent_for_job_dispatch = ? WHERE student_id = ?", (1 if consent else 0, 1 if consent else 0, student_id))
        conn.commit()
        return True

def set_student_auto_apply_mode(student_id: str, mode: bool) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET auto_apply_mode = ? WHERE student_id = ?", (1 if mode else 0, student_id))
        conn.commit()
        return True

def request_retest(student_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET retest_requested = 1, retest_approved = 0 WHERE student_id = ?", (student_id,))
        conn.commit()
        return True

def approve_retest(student_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET retest_approved = 1, exam_completed = 0 WHERE student_id = ?", (student_id,))
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

def get_job_applications(branch_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if branch_id:
            cursor.execute("""
                SELECT j.*, s.full_name as student_name, s.email as student_email, s.branch_name
                FROM job_applications j
                JOIN students s ON j.student_id = s.student_id
                WHERE s.branch_id = ?
                ORDER BY j.timestamp DESC
            """, (branch_id,))
        else:
            cursor.execute("""
                SELECT j.*, s.full_name as student_name, s.email as student_email, s.branch_name
                FROM job_applications j
                JOIN students s ON j.student_id = s.student_id
                ORDER BY j.timestamp DESC
            """)
        return [dict(r) for r in cursor.fetchall()]

# Initialize DB on import
init_db()
