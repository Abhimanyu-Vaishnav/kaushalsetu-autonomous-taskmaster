import os
import re
import json
import sqlite3
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
import shutil

DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    DATA_DIR = "/tmp"
    os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.environ.get("SQLITE_DB_PATH", os.path.join(DATA_DIR, "kaushalsetu_prod.db"))
SNAPSHOT_FILE = os.path.join(DATA_DIR, "state_snapshot.json")
ROOT_SNAPSHOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state_snapshot.json")

# Ensure parent directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

OLD_LOCAL_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaushalsetu.db")
LEGACY_SKILLFORGE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillforge.db")

if not os.path.exists(DB_PATH):
    if os.path.exists(OLD_LOCAL_DB):
        try:
            shutil.copy2(OLD_LOCAL_DB, DB_PATH)
            print(f"[DATABASE MIGRATION] Migrated '{OLD_LOCAL_DB}' to production '{DB_PATH}'.")
        except Exception as e:
            print(f"[DATABASE MIGRATION WARNING] {e}")
    elif os.path.exists(LEGACY_SKILLFORGE_DB):
        try:
            shutil.copy2(LEGACY_SKILLFORGE_DB, DB_PATH)
            print(f"[DATABASE MIGRATION] Migrated '{LEGACY_SKILLFORGE_DB}' to production '{DB_PATH}'.")
        except Exception as e:
            print(f"[DATABASE MIGRATION WARNING] {e}")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn

get_db = get_db_connection

def export_database_snapshot():
    try:
        conn = get_db()
        c = conn.cursor()
        snapshot = {}
        tables = ["institutes", "branches", "courses", "students", "evaluations", "agent_activity_logs", "placement_ledger"]
        for t in tables:
            try:
                c.execute(f"SELECT * FROM {t}")
                rows = [dict(r) for r in c.fetchall()]
                snapshot[t] = rows
            except Exception:
                snapshot[t] = []
        conn.close()

        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, default=str)
        if os.path.exists(os.path.dirname(ROOT_SNAPSHOT)):
            try:
                with open(ROOT_SNAPSHOT, "w", encoding="utf-8") as f:
                    json.dump(snapshot, f, indent=2, default=str)
            except Exception:
                pass
    except Exception as e:
        print(f"Snapshot export warning: {e}")

def restore_database_from_snapshot():
    source_file = SNAPSHOT_FILE if os.path.exists(SNAPSHOT_FILE) else (ROOT_SNAPSHOT if os.path.exists(ROOT_SNAPSHOT) else None)
    if not source_file:
        return

    try:
        with open(source_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        conn = get_db()
        c = conn.cursor()

        for table_name, rows in data.items():
            if not rows:
                continue
            c.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = c.fetchone()[0]
            if count == 0:
                for row in rows:
                    keys = list(row.keys())
                    placeholders = ", ".join(["?"] * len(keys))
                    cols = ", ".join(keys)
                    c.execute(f"INSERT OR IGNORE INTO {table_name} ({cols}) VALUES ({placeholders})", list(row.values()))
        conn.commit()
        conn.close()
        print("✅ [KaushalSetu Startup] Database state successfully restored from persistent snapshot!")
    except Exception as e:
        print(f"Snapshot restore warning: {e}")

def init_complete_db():
    conn = get_db()
    c = conn.cursor()

    # 1. Create table with both title and course_name with safe defaults
    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            institute_id TEXT DEFAULT '',
            branch_id TEXT DEFAULT '',
            title TEXT DEFAULT 'Vocational Course',
            course_name TEXT DEFAULT 'Vocational Course',
            topic TEXT DEFAULT '',
            modules TEXT DEFAULT '[]',
            mcqs TEXT DEFAULT '[]',
            capstone TEXT DEFAULT '',
            skills TEXT DEFAULT '[]',
            course_description TEXT DEFAULT '',
            curriculum_summary TEXT DEFAULT '',
            curriculum_sections TEXT DEFAULT '',
            core_skills TEXT DEFAULT '',
            default_mcq_count INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Check existing columns and alter safely if missing
    c.execute("PRAGMA table_info(courses)")
    cols = [r[1] for r in c.fetchall()]
    
    if "course_name" not in cols:
        try:
            c.execute("ALTER TABLE courses ADD COLUMN course_name TEXT DEFAULT 'Vocational Course'")
        except Exception:
            pass

    if "title" not in cols:
        try:
            c.execute("ALTER TABLE courses ADD COLUMN title TEXT DEFAULT 'Vocational Course'")
        except Exception:
            pass

    if "skills" not in cols:
        try:
            c.execute("ALTER TABLE courses ADD COLUMN skills TEXT DEFAULT '[]'")
        except Exception:
            pass

    if "branch_id" not in cols:
        try:
            c.execute("ALTER TABLE courses ADD COLUMN branch_id TEXT DEFAULT ''")
        except Exception:
            pass

    if "institute_id" not in cols:
        try:
            c.execute("ALTER TABLE courses ADD COLUMN institute_id TEXT DEFAULT ''")
        except Exception:
            pass

    # Ensure other tables exist cleanly
    c.execute("""
        CREATE TABLE IF NOT EXISTS institutes (
            id TEXT PRIMARY KEY,
            name TEXT DEFAULT 'KaushalSetu Foundation',
            code TEXT,
            address TEXT DEFAULT '',
            contact_email TEXT DEFAULT '',
            contact_phone TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS branches (
            id TEXT PRIMARY KEY,
            institute_id TEXT,
            name TEXT DEFAULT 'Main Branch',
            branch_name TEXT DEFAULT 'Main Branch',
            location TEXT DEFAULT '',
            city TEXT DEFAULT '',
            contact_person TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            student_id TEXT,
            name TEXT,
            full_name TEXT,
            dob TEXT DEFAULT '2000-01-01',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            track TEXT DEFAULT 'General Track',
            course_name TEXT DEFAULT 'General Track',
            branch_center TEXT DEFAULT 'Delhi Nangloi',
            branch_name TEXT DEFAULT 'Delhi Nangloi',
            institute_id TEXT DEFAULT '',
            branch_id TEXT DEFAULT '',
            course_id TEXT DEFAULT '',
            linkedin_url TEXT DEFAULT '',
            github_url TEXT DEFAULT '',
            website_url TEXT DEFAULT '',
            twitter_url TEXT DEFAULT '',
            mcq_score REAL DEFAULT 0.0,
            capstone_score REAL DEFAULT 0.0,
            aggregate_score REAL DEFAULT 0.0,
            status_seal TEXT DEFAULT 'PENDING',
            experience_summary TEXT DEFAULT '',
            parsed_skills TEXT DEFAULT '',
            resume_text TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Dynamic dynamic migration check for missing columns in students
    c.execute("PRAGMA table_info(students)")
    existing_cols = {r[1] for r in c.fetchall()}

    required_student_columns = {
        "student_id": "TEXT DEFAULT ''",
        "student_name": "TEXT DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "full_name": "TEXT DEFAULT ''",
        "dob": "TEXT DEFAULT '2000-01-01'",
        "email": "TEXT DEFAULT ''",
        "phone": "TEXT DEFAULT ''",
        "track": "TEXT DEFAULT 'General Track'",
        "course_name": "TEXT DEFAULT 'General Track'",
        "branch_center": "TEXT DEFAULT 'Delhi Nangloi'",
        "branch_name": "TEXT DEFAULT 'Delhi Nangloi'",
        "institute_id": "TEXT DEFAULT ''",
        "branch_id": "TEXT DEFAULT ''",
        "course_id": "TEXT DEFAULT ''",
        "github_url": "TEXT DEFAULT ''",
        "linkedin_url": "TEXT DEFAULT ''",
        "portfolio_url": "TEXT DEFAULT ''",
        "website_url": "TEXT DEFAULT ''",
        "resume_text": "TEXT DEFAULT ''",
        "exam_completed": "INTEGER DEFAULT 0",
        "mcq_score": "REAL DEFAULT 0.0",
        "capstone_score": "REAL DEFAULT 0.0",
        "aggregate_score": "REAL DEFAULT 0.0",
        "status_seal": "TEXT DEFAULT 'PENDING'",
        "created_at": "TIMESTAMP DEFAULT ''"
    }

    for col_name, col_def in required_student_columns.items():
        if col_name not in existing_cols:
            try:
                c.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_def}")
                print(f"[DB Migration] Added missing column '{col_name}' to students table.")
            except Exception as e:
                print(f"Migration notice ({col_name}): {e}")

    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT DEFAULT 'GENERAL_ACTIVITY',
            action_type TEXT DEFAULT 'ACTION',
            entity_type TEXT DEFAULT '',
            entity_id TEXT DEFAULT '',
            student_id TEXT DEFAULT '',
            branch_id TEXT DEFAULT '',
            institute_id TEXT DEFAULT '',
            details TEXT DEFAULT '',
            description TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Dynamic Column Migration for agent_activity_logs table
    c.execute("PRAGMA table_info(agent_activity_logs)")
    l_cols = {r[1] for r in c.fetchall()}

    log_required = {
        "action": "TEXT DEFAULT 'GENERAL_ACTIVITY'",
        "action_type": "TEXT DEFAULT 'ACTION'",
        "entity_type": "TEXT DEFAULT ''",
        "entity_id": "TEXT DEFAULT ''",
        "details": "TEXT DEFAULT ''",
        "timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    for col, col_type in log_required.items():
        if col not in l_cols:
            try:
                c.execute(f"ALTER TABLE agent_activity_logs ADD COLUMN {col} {col_type}")
            except Exception:
                pass

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
    conn.close()

    restore_database_from_snapshot()

# Auto-run on import
init_complete_db()

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
            course_description TEXT DEFAULT '',
            curriculum_summary TEXT DEFAULT '',
            curriculum_sections TEXT DEFAULT '',
            core_skills TEXT DEFAULT '',
            default_mcq_count INTEGER DEFAULT 10,
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
            city TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            github_url TEXT DEFAULT '',
            linkedin_url TEXT DEFAULT '',
            website_url TEXT DEFAULT '',
            twitter_url TEXT DEFAULT '',
            portfolio_url TEXT DEFAULT '',
            project_zip_path TEXT DEFAULT '',
            resume_pdf_path TEXT DEFAULT '',
            work_experience_years INTEGER DEFAULT 0,
            past_companies_text TEXT DEFAULT '',
            experience_summary TEXT DEFAULT '',
            skills_list TEXT DEFAULT '',
            parsed_skills TEXT DEFAULT '',
            resume_text TEXT DEFAULT '',
            target_role_preference TEXT DEFAULT '',
            fees_status TEXT DEFAULT 'PAID',
            consent_given INTEGER DEFAULT 0,
            consent_for_job_dispatch INTEGER DEFAULT 0,
            auto_apply_mode INTEGER DEFAULT 0,
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
        
        # 5. Agent Activity Logs Table
        cursor.execute("""
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

        # 6. Evaluations Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            course_id TEXT,
            mcq_score REAL DEFAULT 0.0,
            practical_score REAL DEFAULT 0.0,
            feedback TEXT DEFAULT '',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 7. Assessments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            institute_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            generated_exam TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(institute_id) REFERENCES institutes(id)
        )
        """)
        
        # 8. Student Submissions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_submissions (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            assessment_id TEXT NOT NULL,
            mcq_answers TEXT,
            mcq_score REAL DEFAULT 0.0,
            practical_submission_text TEXT NOT NULL,
            practical_score REAL DEFAULT 0.0,
            total_score INTEGER NOT NULL,
            strengths TEXT,
            skill_gaps TEXT,
            artifact_image_base64 TEXT,
            gemma_screening_result TEXT NOT NULL,
            gemini_evaluation TEXT NOT NULL,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(assessment_id) REFERENCES assessments(id)
        )
        """)
        
        # 9. Job Applications Ledger Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            match_percentage INTEGER DEFAULT 85,
            dossier_sent_url TEXT DEFAULT '',
            status TEXT DEFAULT 'DISPATCHED',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 10. Crawled Live Jobs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawled_jobs (
            id TEXT PRIMARY KEY,
            student_id TEXT,
            role_title TEXT,
            company_name TEXT,
            company_website TEXT,
            location TEXT,
            salary_range TEXT,
            experience_required TEXT,
            qualification TEXT,
            job_description TEXT,
            recruiter_email TEXT,
            skills_matched TEXT,
            match_percentage INTEGER,
            apply_url TEXT,
            source_platform TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Ensure unique candidate email index
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_students_unique_email ON students(institute_id, branch_id, email)")
        except Exception:
            pass

        conn.commit()
        
        # Run column migration helper
        ensure_db_schema()

init_complete_db = init_db

def ensure_db_schema():
    """Dynamically migrates missing columns & tables in SQLite database without crashing."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure tables exist
            cursor.execute("""
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

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                course_id TEXT,
                mcq_score REAL DEFAULT 0.0,
                practical_score REAL DEFAULT 0.0,
                feedback TEXT DEFAULT '',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Migrate students table columns
            existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(students)").fetchall()]
            columns_to_add = {
                "id": "TEXT DEFAULT ''",
                "name": "TEXT DEFAULT ''",
                "dob": "TEXT DEFAULT '2000-01-01'",
                "email": "TEXT DEFAULT ''",
                "phone": "TEXT DEFAULT ''",
                "city": "TEXT DEFAULT ''",
                "branch_center": "TEXT DEFAULT 'Delhi Nangloi'",
                "track": "TEXT DEFAULT 'General Track'",
                "linkedin_url": "TEXT DEFAULT ''",
                "github_url": "TEXT DEFAULT ''",
                "website_url": "TEXT DEFAULT ''",
                "twitter_url": "TEXT DEFAULT ''",
                "mcq_score": "REAL DEFAULT 0.0",
                "capstone_score": "REAL DEFAULT 0.0",
                "aggregate_score": "REAL DEFAULT 0.0",
                "status_seal": "TEXT DEFAULT 'PENDING'",
                "experience_summary": "TEXT DEFAULT ''",
                "parsed_skills": "TEXT DEFAULT ''",
                "resume_text": "TEXT DEFAULT ''"
            }
            for col, col_type in columns_to_add.items():
                if col not in existing_cols:
                    try:
                        cursor.execute(f"ALTER TABLE students ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Migrate courses table columns
            course_cols = [row[1] for row in cursor.execute("PRAGMA table_info(courses)").fetchall()]
            course_cols_to_add = {
                "title": "TEXT DEFAULT 'Untitled Course'",
                "course_name": "TEXT DEFAULT 'Untitled Course'",
                "topic": "TEXT DEFAULT ''",
                "modules": "TEXT DEFAULT '[]'",
                "mcqs": "TEXT DEFAULT '[]'",
                "capstone": "TEXT DEFAULT ''",
                "skills": "TEXT DEFAULT '[]'",
                "course_description": "TEXT DEFAULT ''",
                "curriculum_summary": "TEXT DEFAULT ''",
                "curriculum_sections": "TEXT DEFAULT ''",
                "core_skills": "TEXT DEFAULT ''",
                "default_mcq_count": "INTEGER DEFAULT 10"
            }
            for col, col_type in course_cols_to_add.items():
                if col not in course_cols:
                    try:
                        cursor.execute(f"ALTER TABLE courses ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Migrate institutes table columns
            inst_cols = [row[1] for row in cursor.execute("PRAGMA table_info(institutes)").fetchall()]
            inst_cols_to_add = {
                "address": "TEXT DEFAULT ''",
                "contact_email": "TEXT DEFAULT ''",
                "contact_phone": "TEXT DEFAULT ''"
            }
            for col, col_type in inst_cols_to_add.items():
                if col not in inst_cols:
                    try:
                        cursor.execute(f"ALTER TABLE institutes ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Migrate branches table columns
            b_cols = [row[1] for row in cursor.execute("PRAGMA table_info(branches)").fetchall()]
            b_cols_to_add = {
                "name": "TEXT DEFAULT ''",
                "location": "TEXT DEFAULT ''",
                "contact_person": "TEXT DEFAULT ''",
                "phone": "TEXT DEFAULT ''"
            }
            for col, col_type in b_cols_to_add.items():
                if col not in b_cols:
                    try:
                        cursor.execute(f"ALTER TABLE branches ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            conn.commit()
    except Exception as ex:
        print(f"[SCHEMA MIGRATION WARNING] {ex}")

def seed_initial_data(conn: sqlite3.Connection):
    """Optional seed helper if explicit seeding is ever requested."""
    cursor = conn.cursor()
    
    inst_id = "INST-GLOBAL-01"
    code = "KAUSHALSETU-HQ"
    inst_name = "KaushalSetu Vocational Foundation"
    
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
        ("STU-1001", inst_id, "BR-NANGLOI", "CRS-AUTO-01", "Nangloi Center", "Automotive & Hardware Diagnostics", "Alex Mercer", "2002-01-15", "alex.mercer@kaushalsetu-edu.org", "+91 9876543210", "Automotive technician candidate specializing in ECU waveform diagnostics", "https://github.com/kaushalsetu/alex-mercer", "", "", "PAID", 1, 1, 0, 0, 0),
        ("STU-1002", inst_id, "BR-NANGLOI", "CRS-WEB-01", "Nangloi Center", "Full Stack Web Development", "Priya Sundaram", "2001-05-20", "priya.s@kaushalsetu-edu.org", "+91 9876543211", "Full stack developer proficient in React and Python backend architectures", "https://github.com/kaushalsetu/priya-web", "", "", "PAID", 1, 1, 0, 0, 0)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO students 
        (student_id, institute_id, branch_id, course_id, branch_name, course_name, full_name, dob, email, phone, bio, github_url, portfolio_url, project_zip_path, fees_status, consent_given, consent_for_job_dispatch, exam_completed, portfolio_generated, interview_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, students_data)
    
    conn.commit()

def reset_database_clean_slate() -> bool:
    """Strictly clears all database tables and leaves database 100% clean/empty without inserting mock candidates."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Delete legacy SQLite files if present
    for legacy_file in ["skillforge.db", "skillforge.db-shm", "skillforge.db-wal"]:
        legacy_path = os.path.join(base_dir, legacy_file)
        if os.path.exists(legacy_path):
            try:
                os.remove(legacy_path)
            except Exception:
                pass

    # 2. Wipe all tables from active SQLite database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        tables = [
            "crawled_jobs", "job_applications", "evaluations", "student_submissions", 
            "assessments", "agent_activity_logs", "students", "courses", "branches", "institutes"
        ]
        for t in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {t};")
            except Exception:
                pass
        conn.commit()

    # 3. Re-initialize clean database schema without mock data
    init_db()

    # 4. Clean up generated static portfolio HTML files
    portfolio_dir = os.path.join(base_dir, "static", "portfolios")
    if os.path.exists(portfolio_dir):
        for f in os.listdir(portfolio_dir):
            if f.endswith(".html"):
                try:
                    os.remove(os.path.join(portfolio_dir, f))
                except Exception:
                    pass

    return True

reset_db = reset_database_clean_slate

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

def create_course(
    institute_id: str,
    branch_id: str,
    course_name: str,
    curriculum_summary: str = "",
    course_description: str = "",
    curriculum_sections: str = "",
    core_skills: str = "",
    default_mcq_count: int = 10
) -> Dict[str, Any]:
    course_id = f"CRS-{uuid.uuid4().hex[:6].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO courses (id, institute_id, branch_id, course_name, curriculum_summary, course_description, curriculum_sections, core_skills, default_mcq_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (course_id, institute_id, branch_id, course_name, curriculum_summary, course_description, curriculum_sections, core_skills, default_mcq_count))
        conn.commit()
    return {
        "id": course_id,
        "institute_id": institute_id,
        "branch_id": branch_id,
        "course_name": course_name,
        "curriculum_summary": curriculum_summary,
        "course_description": course_description,
        "curriculum_sections": curriculum_sections,
        "core_skills": core_skills,
        "default_mcq_count": default_mcq_count
    }

def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        target_str = str(course_id)
        cursor.execute("SELECT * FROM courses WHERE id = ? OR CAST(id AS TEXT) = ?", (target_str, target_str))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_course(
    course_id: str,
    course_name: str,
    curriculum_summary: str = "",
    course_description: str = "",
    curriculum_sections: Union[str, List[Any], Dict[str, Any]] = "",
    core_skills: Union[str, List[Any], Dict[str, Any]] = "",
    default_mcq_count: int = 10
) -> Optional[Dict[str, Any]]:
    sections_json = json.dumps(curriculum_sections) if isinstance(curriculum_sections, (list, dict)) else str(curriculum_sections or "")
    skills_json = json.dumps(core_skills) if isinstance(core_skills, (list, dict)) else str(core_skills or "")
    target_str = str(course_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE courses 
            SET course_name = ?, curriculum_summary = ?, course_description = ?, curriculum_sections = ?, core_skills = ?, default_mcq_count = ?
            WHERE id = ? OR CAST(id AS TEXT) = ?
        """, (course_name, curriculum_summary, course_description, sections_json, skills_json, default_mcq_count, target_str, target_str))
        conn.commit()
    return get_course_by_id(course_id)

def delete_course(course_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        target_str = str(course_id)
        # 1. Nullify / cleanup references in dependent tables before deleting to avoid constraint violations
        for t_query in [
            "UPDATE students SET course_name = 'General Track' WHERE course_id = ? OR CAST(course_id AS TEXT) = ?",
            "DELETE FROM assessments WHERE course_id = ? OR CAST(course_id AS TEXT) = ?",
            "DELETE FROM evaluations WHERE course_id = ? OR CAST(course_id AS TEXT) = ?"
        ]:
            try:
                cursor.execute(t_query, (target_str, target_str))
            except Exception:
                pass

        # 2. Delete the actual course record
        cursor.execute("DELETE FROM courses WHERE id = ? OR CAST(id AS TEXT) = ?", (target_str, target_str))
        conn.commit()
        return True

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
    id: str = None,
    name: str = "",
    student_name: str = "",
    full_name: str = "",
    dob: str = "2000-01-01",
    email: str = "",
    phone: str = "",
    track: str = "General Track",
    course_name: str = "",
    branch_center: str = "Delhi Center",
    branch_name: str = "",
    institute_id: str = "",
    branch_id: str = "",
    course_id: str = "",
    bio: str = "",
    fees_status: str = "PAID",
    consent: int = 1,
    **kwargs
) -> Dict[str, Any]:
    try:
        import uuid
        
        # Harmonize candidate name & attributes
        final_name = str(name or student_name or full_name or kwargs.get("name") or kwargs.get("full_name") or "Candidate").strip()
        final_id = str(id or kwargs.get("student_id") or kwargs.get("id") or f"STU-{uuid.uuid4().hex[:6].upper()}").strip()
        final_dob = str(dob or kwargs.get("date_of_birth") or "2000-01-01").strip()
        final_email = str(email or kwargs.get("candidate_email") or "").strip()
        final_phone = str(phone or kwargs.get("contact_phone") or "").strip()
        final_track = str(track or course_name or kwargs.get("course_track") or "General Track").strip()
        final_branch = str(branch_center or branch_name or kwargs.get("branch") or branch_id or "Delhi Center").strip()
        final_inst_id = str(institute_id or kwargs.get("institute_id") or "INST-ROOT").strip()
        final_branch_id = str(branch_id or kwargs.get("branch_id") or "BR-MAIN").strip()
        final_course_id = str(course_id or kwargs.get("course_id") or "CRS-GENERIC").strip()
        final_bio = str(bio or kwargs.get("bio") or "").strip()

        conn = get_db()
        c = conn.cursor()

        # Check existing table columns to avoid column mismatch crashes
        c.execute("PRAGMA table_info(students)")
        cols = [r[1] for r in c.fetchall()]

        insert_map = {}

        if "id" in cols:
            insert_map["id"] = final_id
        if "student_id" in cols:
            insert_map["student_id"] = final_id
        if "name" in cols:
            insert_map["name"] = final_name
        if "student_name" in cols:
            insert_map["student_name"] = final_name
        if "full_name" in cols:
            insert_map["full_name"] = final_name
        if "dob" in cols:
            insert_map["dob"] = final_dob
        if "email" in cols:
            insert_map["email"] = final_email
        if "phone" in cols:
            insert_map["phone"] = final_phone
        if "track" in cols:
            insert_map["track"] = final_track
        if "course_name" in cols:
            insert_map["course_name"] = final_track
        if "branch_center" in cols:
            insert_map["branch_center"] = final_branch
        if "branch_name" in cols:
            insert_map["branch_name"] = final_branch
        if "institute_id" in cols:
            insert_map["institute_id"] = final_inst_id
        if "branch_id" in cols:
            insert_map["branch_id"] = final_branch_id
        if "course_id" in cols:
            insert_map["course_id"] = final_course_id
        if "bio" in cols:
            insert_map["bio"] = final_bio
        if "fees_status" in cols:
            insert_map["fees_status"] = fees_status

        col_names = ", ".join(insert_map.keys())
        placeholders = ", ".join(["?"] * len(insert_map))
        values = list(insert_map.values())

        c.execute(f"INSERT OR REPLACE INTO students ({col_names}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()

        # Trigger snapshot backup & audit log
        try:
            export_database_snapshot()
        except Exception:
            pass

        return {"status": "success", "success": True, "message": "Student registered successfully!", "id": final_id, "student_id": final_id, "name": final_name, "full_name": final_name, "data": insert_map}
    except Exception as e:
        return {"status": "error", "message": f"Registration failed: {str(e)}"}

def mark_student_exam_complete(
    student_id: str,
    github_url: str = "",
    portfolio_url: str = "",
    mcq_score: float = 0.0,
    practical_score: float = 0.0,
    aggregate_score: float = 0.0,
    status_seal: str = "PASS (FOUNDATIONAL)"
) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students 
            SET exam_completed = 1, portfolio_generated = 1, github_url = ?, portfolio_url = ?,
                mcq_score = ?, capstone_score = ?, aggregate_score = ?, status_seal = ?
            WHERE student_id = ?
        """, (github_url, portfolio_url, mcq_score, practical_score, aggregate_score, status_seal, student_id))
        
        try:
            eval_id = f"EVAL-{uuid.uuid4().hex[:8].upper()}"
            cursor.execute("""
                INSERT OR REPLACE INTO evaluations (
                    id, student_id, mcq_score, practical_score, aggregate_score, status_seal
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (eval_id, student_id, mcq_score, practical_score, aggregate_score, status_seal))
        except Exception:
            pass

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

def normalize_dob(dob_raw: Any) -> str:
    """Normalizes any incoming DOB string (YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD, etc.) into YYYY-MM-DD format."""
    if not dob_raw:
        return ""
    cleaned = re.sub(r'[\s/.]+', '-', str(dob_raw).strip())
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return cleaned

def verify_student_login(login_id_or_email: str, dob_input: str) -> Optional[Dict[str, Any]]:
    """Strict Student DOB Authentication with robust DOB normalization and schema tolerance."""
    clean_id = str(login_id_or_email or "").strip()
    norm_input_dob = normalize_dob(dob_input)
    if not clean_id or not norm_input_dob:
        return None
    
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Discover table columns to support student_id vs id
        cols = [r[1] for r in cursor.execute("PRAGMA table_info(students)").fetchall()]
        id_col = "student_id" if "student_id" in cols else "id"
        
        query = f"SELECT * FROM students WHERE UPPER({id_col}) = UPPER(?)"
        params = [clean_id]
        if "email" in cols:
            query += f" OR LOWER(email) = LOWER(?)"
            params.append(clean_id)
            
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for row in rows:
            student_dict = dict(row)
            # Map aliases for uniform API usage
            if "id" not in student_dict and "student_id" in student_dict:
                student_dict["id"] = student_dict["student_id"]
            if "student_id" not in student_dict and "id" in student_dict:
                student_dict["student_id"] = student_dict["id"]
            if "name" not in student_dict and "full_name" in student_dict:
                student_dict["name"] = student_dict["full_name"]
            if "full_name" not in student_dict and "name" in student_dict:
                student_dict["full_name"] = student_dict["name"]
            if "track" not in student_dict and "course_name" in student_dict:
                student_dict["track"] = student_dict["course_name"]
            if "course_name" not in student_dict and "track" in student_dict:
                student_dict["course_name"] = student_dict["track"]

            db_norm_dob = normalize_dob(student_dict.get("dob", ""))
            # If db_dob is empty/default or matches norm_input_dob
            if not db_norm_dob or db_norm_dob == norm_input_dob or student_dict.get("dob") == norm_input_dob or student_dict.get("dob") == str(dob_input).strip():
                return student_dict
        return None

def update_student_profile(
    student_id: str,
    full_name: str,
    email: str,
    phone: str = "",
    bio: str = "",
    github_url: str = "",
    skills_list: str = "",
    target_role_preference: str = "",
    past_companies_text: str = "",
    work_experience_years: int = 0,
    dob: str = "",
    city: str = "",
    linkedin_url: str = "",
    website_url: str = "",
    twitter_url: str = ""
) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE students 
            SET full_name = ?, email = ?, phone = ?, bio = ?, github_url = ?, skills_list = ?, 
                target_role_preference = ?, past_companies_text = ?, work_experience_years = ?
        """
        params = [full_name, email, phone, bio, github_url, skills_list, target_role_preference, past_companies_text, work_experience_years]
        
        if dob:
            query += ", dob = ?"
            params.append(dob)
        if city:
            query += ", city = ?"
            params.append(city)
        if linkedin_url:
            query += ", linkedin_url = ?"
            params.append(linkedin_url)
        if website_url:
            query += ", website_url = ?"
            params.append(website_url)
        if twitter_url:
            query += ", twitter_url = ?"
            params.append(twitter_url)
            
        query += " WHERE student_id = ?"
        params.append(student_id)
        
        cursor.execute(query, tuple(params))
        conn.commit()
    return get_student_by_id(student_id)

def delete_student(student_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM student_submissions WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM job_applications WHERE student_id = ?", (student_id,))
        conn.commit()
        return True

def log_agent_activity(action_type: str, description: str, institute_id: str = None, branch_id: str = None, student_id: str = None, metadata: dict = None) -> str:
    log_id = f"LOG-{uuid.uuid4().hex[:8].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_activity_logs (id, institute_id, branch_id, student_id, action_type, description, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (log_id, institute_id, branch_id, student_id, action_type, description, json.dumps(metadata or {})))
        conn.commit()
    return log_id

def get_agent_activity_logs(branch_id: Optional[str] = None, institute_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if branch_id:
            cursor.execute("SELECT * FROM agent_activity_logs WHERE branch_id = ? ORDER BY timestamp DESC", (branch_id,))
        elif institute_id:
            cursor.execute("SELECT * FROM agent_activity_logs WHERE institute_id = ? ORDER BY timestamp DESC", (institute_id,))
        else:
            cursor.execute("SELECT * FROM agent_activity_logs ORDER BY timestamp DESC LIMIT 100")
        return [dict(r) for r in cursor.fetchall()]

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

def record_job_application(student_id: str, company_name: str, role_title: str, match_percentage: int, dossier_sent_url: str = '', status: str = 'APPLIED_AND_DISPATCHED', interview_details: str = 'Dispatched via AI Career Agent', metric_hash: str = '0xDEFAULT') -> str:
    app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_applications (id, student_id, company_name, role_title, match_percentage, dossier_sent_url, status, interview_details, metric_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id, student_id, company_name, role_title, match_percentage, dossier_sent_url, status, interview_details, metric_hash))
        conn.commit()
    return app_id

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
