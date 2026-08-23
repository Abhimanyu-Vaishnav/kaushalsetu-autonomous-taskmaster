import os
import json
import sqlite3
import hashlib
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillforge.db")

def init_recruiter_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Hiring Partners Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hiring_partners (
        partner_id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        industry TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        webhook_url TEXT NOT NULL
    )
    """)
    
    # Partner Requisitions (Active Role Openings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requisitions (
        req_id TEXT PRIMARY KEY,
        partner_id TEXT NOT NULL,
        role_title TEXT NOT NULL,
        min_score INTEGER DEFAULT 80,
        required_skills TEXT NOT NULL,
        min_salary TEXT NOT NULL,
        FOREIGN KEY(partner_id) REFERENCES hiring_partners(partner_id)
    )
    """)
    
    # Dispatch Audit Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dispatch_ledger (
        dispatch_id TEXT PRIMARY KEY,
        candidate_name TEXT NOT NULL,
        role_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        match_percentage INTEGER NOT NULL,
        metric_hash TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    
    # Seed default hiring partners & roles if empty
    cursor.execute("SELECT COUNT(*) FROM hiring_partners")
    if cursor.fetchone()[0] == 0:
        seed_recruiter_data(conn)
        
    conn.close()

def seed_recruiter_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    partners = [
        ("PARTNER-01", "Tata Motors Technical Services", "Automotive & Heavy Equipment", "recruitment@tatamotors.com", "https://api.tatamotors.com/webhooks/skillforge-hiring"),
        ("PARTNER-02", "Infosys Skilling & BPM Division", "Information Technology & Software", "careers@infosys.com", "https://api.infosys.com/webhooks/talent-intake"),
        ("PARTNER-03", "Schneider Electric Industrial Solutions", "Electrical & Hardware Engineering", "hiring@schneider-electric.com", "https://api.schneider.com/webhooks/candidates")
    ]
    cursor.executemany("INSERT INTO hiring_partners VALUES (?, ?, ?, ?, ?)", partners)
    
    reqs = [
        ("REQ-101", "PARTNER-01", "Automotive Systems Technician", 80, "CAN Bus, Oscilloscope Diagnostics, Circuit Wiring, Safety Isolation", "INR 4.5 LPA"),
        ("REQ-102", "PARTNER-02", "Full Stack Developer Trainee", 80, "Python, React/HTML, REST API, SQL, Git", "INR 5.2 LPA"),
        ("REQ-103", "PARTNER-03", "Electrical & Diagnostics Specialist", 82, "Multimeter Diagnostics, Circuit Diagrams, Safety Lockout, Motor Control", "INR 4.8 LPA")
    ]
    cursor.executemany("INSERT INTO requisitions VALUES (?, ?, ?, ?, ?, ?)", reqs)
    
    conn.commit()

def get_hiring_partners() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hiring_partners")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_requisitions() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, hp.company_name, hp.contact_email, hp.webhook_url 
        FROM requisitions r 
        JOIN hiring_partners hp ON r.partner_id = hp.partner_id
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def log_dispatch_ledger(candidate_name: str, role_title: str, company_name: str, match_pct: int, metric_hash: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    dispatch_id = f"DISPATCH-{hashlib.md5(f'{candidate_name}{role_title}'.encode()).hexdigest()[:8].upper()}"
    cursor.execute("""
        INSERT INTO dispatch_ledger (dispatch_id, candidate_name, role_title, company_name, match_percentage, metric_hash, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (dispatch_id, candidate_name, role_title, company_name, match_pct, metric_hash, status))
    conn.commit()
    conn.close()

def get_dispatch_ledger() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dispatch_ledger ORDER BY timestamp DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# Initialize DB on module load
init_recruiter_db()
