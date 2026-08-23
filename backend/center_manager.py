import os
import json
import sqlite3
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
        
        # Centers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS centers (
            center_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
        """)
        
        # Batches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            batch_id TEXT PRIMARY KEY,
            center_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            instructor TEXT NOT NULL,
            FOREIGN KEY(center_id) REFERENCES centers(center_id)
        )
        """)
        
        # Candidates table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id TEXT PRIMARY KEY,
            batch_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY(batch_id) REFERENCES batches(batch_id)
        )
        """)
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM centers")
        if cursor.fetchone()[0] == 0:
            seed_default_data(conn)

def seed_default_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    centers = [
        ("CTR-DEL-01", "Nangloi Vocational Skilling Hub", "Delhi North-West", 150),
        ("CTR-DEL-02", "Yamuna Vihar Technical Center", "Delhi East", 120),
        ("CTR-HAR-01", "Jwalapur Automotive & Hardware Center", "Haridwar, Uttarakhand", 200)
    ]
    cursor.executemany("INSERT OR IGNORE INTO centers VALUES (?, ?, ?, ?)", centers)
    
    batches = [
        ("BATCH-NGL-2026A", "CTR-DEL-01", "Full Stack Web Development", "2026-01-15", "Instructor Rajesh Sharma"),
        ("BATCH-YMV-2026B", "CTR-DEL-02", "Accounting & Financial Tally", "2026-02-01", "Instructor Meenakshi Verma"),
        ("BATCH-JWL-2026C", "CTR-HAR-01", "Automotive & Hardware Diagnostics", "2026-01-10", "Instructor Vikram Singh")
    ]
    cursor.executemany("INSERT OR IGNORE INTO batches VALUES (?, ?, ?, ?, ?)", batches)
    
    candidates = [
        ("CAND-101", "BATCH-NGL-2026A", "Alex Mercer", "alex.mercer@skillforge-edu.org", "ACTIVE"),
        ("CAND-102", "BATCH-NGL-2026A", "Priya Sundaram", "priya.s@skillforge-edu.org", "ACTIVE"),
        ("CAND-103", "BATCH-YMV-2026B", "Jordan Smith", "jordan.s@skillforge-edu.org", "ACTIVE"),
        ("CAND-104", "BATCH-JWL-2026C", "Amitabh Choudhury", "amitabh.c@skillforge-edu.org", "ACTIVE")
    ]
    cursor.executemany("INSERT OR IGNORE INTO candidates VALUES (?, ?, ?, ?, ?)", candidates)
    
    conn.commit()

def get_centers() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM centers")
        return [dict(r) for r in cursor.fetchall()]

def get_batches(center_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if center_id:
            cursor.execute("SELECT * FROM batches WHERE center_id = ?", (center_id,))
        else:
            cursor.execute("SELECT * FROM batches")
        return [dict(r) for r in cursor.fetchall()]

def get_candidates(batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if batch_id:
            cursor.execute("SELECT * FROM candidates WHERE batch_id = ?", (batch_id,))
        else:
            cursor.execute("SELECT * FROM candidates")
        return [dict(r) for r in cursor.fetchall()]

# Initialize DB on module import
init_db()
