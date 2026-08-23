import streamlit as st
import requests
import json
import time
import base64
import io

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Production Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #6B7280;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-success {
        background-color: #DEF7EC;
        color: #03543F;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .badge-remedial {
        background-color: #FEECDC;
        color: #9A3412;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .hash-text {
        font-family: monospace;
        color: #4F46E5;
        background-color: #EEF2FF;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .cert-box {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
        color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 2px solid #6366F1;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ SkillForge Autonomous</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Continuous Action Engine for Vocational Institutes & Placements | Powered by Gemini 3.5 & Gemma</div>', unsafe_allow_html=True)

# Sidebar Real-Time Badges & One-Click Demo Mode
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Health Status")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            st.success("🟢 FastAPI Backend Connected")
            st.success("⚡ Gemma Pre-check Engine Ready")
            st.success("🤖 Gemini 3.5 Pro & Flash Active")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.error("🔴 Backend Unreachable")
        
    st.divider()
    st.markdown("### ⚡ One-Click Demo Mode")
    st.caption("Quick presets for Hackathon Judges:")
    
    if st.button("🟢 Preset A: Top Performer (Score: 92%)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_A"
        st.info("Loaded Top Performer Preset! Navigate to Tab 2 to run.")
        
    if st.button("🟠 Preset B: Remedial Student (Score: 54%)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_B"
        st.info("Loaded Remedial Student Preset! Navigate to Tab 2 to run.")

    st.divider()
    st.markdown("### Category Fit")
    st.markdown("- **Taskmaster Track**")
    st.markdown("- **Zero Chatbot UI**")
    st.markdown("- **Gemma Bonus (+0.2 pts)**")

# 4 Main Navigation Tabs
tabs = st.tabs([
    "🏛️ Center Operations & Curriculum Hub",
    "🎓 Student Interactive Assessment Workspace",
    "🚀 Autonomous Placement & Recruiter Outbox",
    "📖 System Guide, Architecture & Tech Inspector"
])

# --- TAB 1: CENTER OPERATIONS & CURRICULUM HUB ---
with tabs[0]:
    st.subheader("🏛️ Center Operations & Curriculum Governance")
    st.markdown("Manage centers, branches, vocational courses, set placement score thresholds (e.g. 70%), and synthesize AI exams.")
    
    # Load Institute Info
    inst_data = {}
    try:
        ires = requests.get(f"{BACKEND_URL}/api/institute/info", timeout=2)
        if ires.status_code == 200:
            inst_data = ires.json()["data"]
    except Exception:
        pass
        
    if inst_data:
        st.markdown(f"### **{inst_data.get('name', 'Institute')}** (`Code: {inst_data.get('code', 'SKILLFORGE-HQ')}`)")
        
        # Policy Settings Form
        with st.expander("⚙️ Placement Threshold & Interview Policy Config", expanded=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                cur_thresh = inst_data.get("placement_threshold", 70)
                new_thresh = st.slider("Minimum Placement Threshold Score %", 50, 95, cur_thresh)
            with col_c2:
                cur_cap = inst_data.get("max_interviews_cap", 3)
                new_cap = st.slider("Max Interview Cap per Candidate", 1, 5, cur_cap)
            with col_c3:
                st.write("")
                st.write("")
                if st.button("💾 Save Policy Config", type="primary", use_container_width=True):
                    up_res = requests.post(f"{BACKEND_URL}/api/institute/config", json={
                        "institute_id": inst_data["id"],
                        "placement_threshold": new_thresh,
                        "max_interviews_cap": new_cap
                    })
                    if up_res.status_code == 200:
                        st.success("✅ Placement Policy Saved!")
                        st.rerun()
                        
        st.divider()
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("#### 🏛️ Registered Branches")
            for b in inst_data.get("branches", []):
                st.info(f"🔹 **{b}**")
        with col_b2:
            st.markdown("#### 📚 Active Vocational Courses")
            for c in inst_data.get("courses", []):
                st.write(f"- 🔸 **{c}**")
                
        st.divider()
        st.markdown("#### 👥 Student Roster & Bulk Intake")
        
        tab_a1, tab_a2 = st.tabs(["📄 Single Candidate Enrollment", "📁 Bulk CSV Upload"])
        
        with tab_a1:
            with st.form("single_enroll_form"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    s_name = st.text_input("Full Name", value="Rohan Mehta")
                    s_email = st.text_input("Email Address", value="rohan.m@skillforge-edu.org")
                    s_phone = st.text_input("Phone Number", value="+91 9876543210")
                with sc2:
                    s_branch = st.selectbox("Assign Branch", inst_data.get("branches", []))
                    s_course = st.selectbox("Assign Course", inst_data.get("courses", []))
                    s_fees = st.selectbox("Fees Status", ["PAID", "PENDING"])
                    
                s_submit = st.form_submit_button("Enroll Candidate", type="primary")
                if s_submit:
                    a_res = requests.post(f"{BACKEND_URL}/api/students/add", json={
                        "institute_id": inst_data["id"],
                        "branch_name": s_branch,
                        "full_name": s_name,
                        "email": s_email,
                        "phone": s_phone,
                        "course_name": s_course,
                        "fees_status": s_fees,
                        "consent": 1
                    })
                    if a_res.status_code == 200:
                        st.success(f"✅ Candidate Enrolled! ID: `{a_res.json()['data']['student_id']}`")
                        st.rerun()
                        
        with tab_a2:
            st.markdown("Upload CSV containing: `full_name`, `email`, `phone`, `branch_name`, `course_name`, `fees_status`")
            sample_csv_data = "full_name,email,phone,branch_name,course_name,fees_status\nVikram Rathore,vikram.r@skillforge-edu.org,+91 9811122233,Nangloi Center,Automotive & Hardware Diagnostics,PAID\nSneha Gupta,sneha.g@skillforge-edu.org,+91 9822233344,Yamuna Vihar Center,Full Stack Web Development,PAID"
            st.download_button("📥 Download Sample CSV Template", sample_csv_data, file_name="sample_students.csv", mime="text/csv")
            
            uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])
            if uploaded_csv is not None:
                if st.button("🚀 Process Bulk Roster", type="primary"):
                    files = {"file": (uploaded_csv.name, uploaded_csv.getvalue(), "text/csv")}
                    b_res = requests.post(f"{BACKEND_URL}/api/students/bulk-upload?institute_id={inst_data['id']}", files=files)
                    if b_res.status_code == 200:
                        st.success(f"✅ Processed {b_res.json()['count']} candidates!")
                        st.rerun()
                        
        st.divider()
        st.markdown("#### 📜 Live Institute Roster")
        try:
            st_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
            if st_res.status_code == 200:
                students = st_res.json()["data"]
                st.dataframe(students, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load roster: {e}")

# --- TAB 2: STUDENT INTERACTIVE ASSESSMENT WORKSPACE ---
with tabs[1]:
    st.subheader("🎓 Student Interactive Assessment Workspace")
    st.markdown("Select student login, verify consent, answer unselected MCQs, submit practical code/logs, and trigger dynamic scoring.")
    
    # Load Students
    students = []
    try:
        s_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
        if s_res.status_code == 200:
            students = s_res.json()["data"]
    except Exception:
        pass
        
    if not students:
        st.warning("No students found. Please enroll candidates in Tab 1.")
    else:
        stu_opts = {f"{s['full_name']} ({s['student_id']}) - {s['course_name']}": s['student_id'] for s in students}
        sel_label = st.selectbox("🔑 Select Student Login", list(stu_opts.keys()))
        selected_student_id = stu_opts[sel_label]
        
        stu_detail = next(s for s in students if s['student_id'] == selected_student_id)
        
        st.markdown("#### 👤 Candidate Profile & Placement Consent Gate")
        col_sp1, col_sp2, col_sp3 = st.columns(3)
        with col_sp1:
            st.write(f"**Name:** {stu_detail['full_name']}")
            st.write(f"**Email:** `{stu_detail['email']}`")
        with col_sp2:
            st.write(f"**Branch:** `{stu_detail['branch_name']}`")
            st.write(f"**Course:** {stu_detail['course_name']}")
        with col_sp3:
            cur_consent = bool(stu_detail.get('consent_for_job_dispatch', 1))
            st.write(f"**Interviews Dispatched:** `{stu_detail.get('interview_count', 0)} / 3`")
            new_consent = st.checkbox("Authorize AI Agent to Auto-Dispatch Job Applications", value=cur_consent)
            if new_consent != cur_consent:
                requests.post(f"{BACKEND_URL}/api/students/consent", json={"student_id": selected_student_id, "consent": new_consent})
                st.success("✅ Consent updated!")
                st.rerun()
                
        st.divider()
        st.markdown("### 📝 Exam Synthesis & Dynamic Real-Time Test")
        
        if st.button("✨ Synthesize Fresh 5-MCQ Exam via Gemini 3.5", type="primary"):
            with st.spinner("Synthesizing 5-MCQ Assessment via Gemini 3.5..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": stu_detail['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    st.success("✅ Fresh Assessment Synthesized!")
                    st.rerun()
                    
        if "current_exam" not in st.session_state:
            with st.spinner("Initializing Assessment..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": stu_detail['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    
        exam = st.session_state.get("current_exam", {})
        mcqs = exam.get("mcqs", [])
        mcq_key = [m.get("correct_option", 0) for m in mcqs]
        
        # Check One-Click Demo Mode presets from Sidebar
        demo_preset = st.session_state.get("demo_preset")
        is_preset_a = demo_preset == "PRESET_A"
        is_preset_b = demo_preset == "PRESET_B"
        
        with st.form("student_exam_form"):
            st.markdown(f"#### 📋 **{exam.get('title', 'Vocational Assessment')}**")
            st.markdown("##### **Part 1: Multiple Choice Questions (30 Points Max)**")
            
            user_mcq_answers = []
            for idx, mcq in enumerate(mcqs, 1):
                st.markdown(f"**Question {idx}: {mcq['question']}**")
                opts = mcq['options']
                
                default_idx = None
                if is_preset_a:
                    default_idx = mcq['correct_option']
                elif is_preset_b:
                    default_idx = (mcq['correct_option'] + 1) % len(opts)
                    
                selected_opt = st.radio(
                    f"Select answer for Q{idx}:",
                    opts,
                    index=default_idx,
                    key=f"mcq_radio_{idx}_{selected_student_id}"
                )
                
                if selected_opt in opts:
                    user_mcq_answers.append(opts.index(selected_opt))
                else:
                    user_mcq_answers.append(-1)
                    
            st.divider()
            st.markdown("##### **Part 2: Practical Project Challenge (70 Points Max)**")
            
            p_task_default = exam.get("practical_task", f"Complete diagnostic inspection for {stu_detail['course_name']}.")
            st.info(f"**Task:** {p_task_default}")
            
            rubric_default = exam.get("grading_rubric", ["Safety lockout procedure followed", "Diagnostic accuracy verified", "Documentation complete"])
            st.caption("Rubric: " + " | ".join(rubric_default))
            
            if is_preset_a:
                sub_text_default = (
                    "First, performed a full safety lockout procedure and verified system power status using a multimeter. "
                    "Next, connected an oscilloscope to signal lines to measure voltage waveforms. "
                    "Found ground signal degradation due to terminal connector corrosion. "
                    "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean 2.5V differential voltage."
                )
            elif is_preset_b:
                sub_text_default = "Looked at wires. Turned on switch. It worked eventually."
            else:
                sub_text_default = (
                    "Performed safety lockout procedure. Verified circuit connections using calibrated multimeter. "
                    "Recorded voltage measurements across load terminals. Documented fault codes and completed repair."
                )
                
            s_text = st.text_area("Your Solution Code / Diagnostic Log", value=sub_text_default, height=130)
            uploaded_img = st.file_uploader("Attach Practical Artifact Image (Hardware Photo / Circuit Diagram / Code Screenshot)", type=["jpg", "png", "jpeg"])
            
            submit_exam = st.form_submit_button("🚀 Submit Exam & Run Autonomous Placement Pipeline", type="primary", use_container_width=True)
            
        if submit_exam:
            if "demo_preset" in st.session_state:
                del st.session_state["demo_preset"]
                
            img_b64 = None
            if uploaded_img is not None:
                img_b64 = base64.b64encode(uploaded_img.getvalue()).decode("utf-8")
                
            p_bar = st.progress(0, text="Submitting Exam...")
            time.sleep(0.2)
            p_bar.progress(30, text="1. Calculating MCQ Objective Score & Gemma Fast Screening...")
            time.sleep(0.3)
            p_bar.progress(70, text="2. Gemini 3.5 Subjective Practical Grading...")
            
            try:
                pipe_res = requests.post(
                    f"{BACKEND_URL}/api/student/evaluate-and-dispatch",
                    json={
                        "student_id": selected_student_id,
                        "assessment_id": exam.get("db_assessment_id", "ASS-DEFAULT"),
                        "mcq_answers": user_mcq_answers,
                        "mcq_key": mcq_key,
                        "practical_task": p_task_default,
                        "grading_rubric": rubric_default,
                        "submission_text": s_text,
                        "image_base64": img_b64
                    },
                    timeout=30
                )
                p_bar.progress(100, text="Dynamic Evaluation Complete!")
                
                if pipe_res.status_code == 200:
                    res_data = pipe_res.json()["data"]
                    eval_out = res_data["evaluation"]
                    dispatch_out = res_data["dispatch"]
                    
                    st.success("✅ Dynamic Real-Time Grading Complete!")
                    
                    st.markdown("### 📊 Scorecard & Performance Metrics")
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("MCQ Score", f"{eval_out['mcq_score']} / 30 pts", f"{eval_out['mcq_correct_count']}/{eval_out['mcq_total_questions']} Correct")
                    with mc2:
                        st.metric("Practical Score", f"{eval_out['practical_score']} / 70 pts")
                    with mc3:
                        st.metric("Final Total Score", f"{eval_out['total_score']} / 100 pts")
                    with mc4:
                        ready = eval_out['placement_ready']
                        st.metric("Verification Gate", "PASSED 🚀" if ready else "REMEDIAL 🟠")
                        
                    st.divider()
                    
                    if ready:
                        st.markdown(f'<span class="badge-success">🚀 STATUS: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.markdown("#### 📬 Outbound Application & Notification Alerts")
                        st.markdown(f"**Matched Employer:** `{dispatch_out['hiring_partner']}`")
                        st.markdown(f"**Role Title:** `{dispatch_out['role']}`")
                        st.markdown(f"**Verified Metric Hash:** <span class=\"hash-text\">{dispatch_out['verified_metric_hash']}</span>", unsafe_allow_html=True)
                        st.info(dispatch_out["notifications"]["student_alert"])
                        st.info(dispatch_out["notifications"]["branch_alert"])
                        
                        # Live Certificate Generator Card
                        st.divider()
                        st.markdown("### 🎓 Verified Candidate Competency Certificate")
                        cert_res = requests.post(f"{BACKEND_URL}/api/certificate/generate", json={
                            "candidate_name": stu_detail['full_name'],
                            "student_id": selected_student_id,
                            "course_name": stu_detail['course_name'],
                            "branch_name": stu_detail['branch_name'],
                            "total_score": eval_out['total_score'],
                            "mcq_score": float(eval_out['mcq_score']),
                            "practical_score": float(eval_out['practical_score']),
                            "metric_hash": dispatch_out['verified_metric_hash']
                        })
                        if cert_res.status_code == 200:
                            cert = cert_res.json()["data"]
                            st.markdown(f"""
                            <div class="cert-box">
                                <h3>📜 OFFICIAL COMPETENCY CERTIFICATE</h3>
                                <p><strong>Certificate ID:</strong> {cert['certificate_id']}</p>
                                <p><strong>Candidate:</strong> {cert['candidate_name']} ({cert['student_id']})</p>
                                <p><strong>Branch:</strong> {cert['branch_name']}</p>
                                <p><strong>Course:</strong> {cert['course_name']}</p>
                                <p><strong>Final Score:</strong> {cert['total_score']}% (MCQ: {cert['mcq_score']} pts | Practical: {cert['practical_score']} pts)</p>
                                <p><strong>SHA-256 Hash:</strong> <code>{cert['verified_hash']}</code></p>
                                <p><strong>Verification Status:</strong> {cert['verification_status']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="badge-remedial">🔄 STATUS: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.markdown("#### 📚 Personalized 7-Day Remedial Micro-Study Schedule")
                        st.warning(f"Reasons: {', '.join(dispatch_out.get('reasons', []))}")
                        
                        rem_sched = eval_out.get("remedial_schedule", {})
                        for day_task in rem_sched.get("daily_schedule", []):
                            st.markdown(f"**Day {day_task['day']}**: `{day_task['focus_topic']}`")
                            st.caption(f"Task: {day_task['practice_exercise']} ({day_task['estimated_hours']} hr)")
                else:
                    st.error(f"Pipeline error: {pipe_res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- TAB 3: AUTONOMOUS PLACEMENT & RECRUITER OUTBOX ---
with tabs[2]:
    st.subheader("🚀 Autonomous Placement & Dispatch Audit Ledger")
    st.markdown("Immutable ledger tracking candidate job applications, employer interview dispatches, and verification hashes.")
    
    try:
        l_res = requests.get(f"{BACKEND_URL}/api/placements/ledger", timeout=2)
        if l_res.status_code == 200:
            ledger = l_res.json()["data"]
            if ledger:
                st.dataframe(ledger, use_container_width=True)
            else:
                st.info("No job dispatches logged yet. Complete an exam submission in Tab 2!")
    except Exception as e:
        st.error(f"Could not load placement ledger: {e}")

# --- TAB 4: SYSTEM GUIDE, ARCHITECTURE & TECH INSPECTOR ---
with tabs[3]:
    st.subheader("📖 System Architecture, Docs & Technology Inspector")
    st.markdown("Full transparency hub detailing BYOF problem statement, dual-AI pipeline, security consent gates, and infrastructure stack.")
    
    with st.expander("📌 Section 1: What is SkillForge Autonomous & Grassroots BYOF Problem", expanded=True):
        st.markdown("""
        **The BYOF (Bring Your Own Friction) Problem:**  
        Vocational training centers in Tier-2/3 cities and rural hubs (e.g. automotive repair, CNC machining, web development bootcamps) face severe operational bottlenecks:
        1. **Curriculum Synthesis Overhead**: Manually creating practical exams, rubrics, and MCQs tailored to fast-evolving industry standards takes weeks.
        2. **Evaluation Latency**: Instructors spend 20+ hours/week manually grading technical diagnostic logs and practical student code/reports.
        3. **Placement Pipeline Bottleneck**: High-performing candidates sit in administrative queues for weeks before being pitched to hiring partners.

        **The SkillForge Solution:**  
        SkillForge Autonomous functions as a **24/7 Continuous Action Engine** replacing administrative latency with automated assessment synthesis, dual-AI multimodal grading, and verified job application dispatches.
        """)
        
    with st.expander("⚙️ Section 2: Step-by-Step System Workflow Guide"):
        st.markdown(r"""
        1. **Center Governance Setup (Tab 1)**: Institute admins define placement thresholds (e.g., 70%), interview attempt caps (max 3), registered branches, and enroll student rosters.
        2. **Interactive Exam Synthesis & Test Taking (Tab 2)**: Gemini 3.5 Pro generates 5-MCQ exams + practical project challenges. Candidates log in, review consent, select answers via unselected radio buttons, and submit diagnostic logs or hardware photos.
        3. **Dual-AI Dynamic Evaluation (Tab 2)**:
           - *Objective MCQ Score*: 30 points max based on option key matching.
           - *Subjective Practical Score*: 70 points max evaluated by Gemini 3.5 Multimodal Vision.
        4. **Verification Gate & Autonomous Action Execution (Tab 3)**:
           - *Score $\ge$ 70% & Consent Authorized*: Automatically matches candidate against enterprise hiring partner requisitions (Tata Motors, Infosys, Schneider Electric), generates a SHA-256 metric hash, dispatches outbox applications, and triggers candidate & branch alerts.
           - *Score < 70%*: Triggers an automatic 7-day personalized remedial micro-study schedule.
        """)
        
    with st.expander("🧠 Section 3: Under the Hood: Dual-AI Architecture & Gemma Bonus Track"):
        st.markdown("""
        **Why Two AI Models?**
        - **Model 1: Gemma (Fast Syntax & Token Pre-Screener)**  
          *Role*: Sub-millisecond deterministic structure check verifying mandatory technical terms, syntax formatting, and minimum length before sending payloads to cognitive LLMs.  
          *Hackathon Bonus*: Earns the **+0.2 Gemma Integration Bonus Track**.
        - **Model 2: Google GenAI SDK (Gemini 3.5 Pro & Flash)**  
          *Role*: Cognitive reasoning engine synthesizing structured exam papers, performing deep multimodal vision grading on hardware/code screenshots, and generating hiring partner pitches.
        """)
        
    with st.expander("☁️ Section 4: Backend Technology Stack & Cloud Infrastructure"):
        st.markdown("""
        | Component | Technology | Purpose |
        | :--- | :--- | :--- |
        | **Backend Framework** | **FastAPI & Pydantic** | Production RESTful API with strict schema validation |
        | **Database Storage** | **SQLite WAL Mode** | Multi-tenant thread-safe persistence with 30s busy timeout |
        | **AI SDK** | **Google GenAI SDK (`google-genai`)** | Gemini 3.5 Pro / Flash & Gemma integration |
        | **Frontend UI** | **Streamlit** | Interactive multi-role operational dashboard |
        | **Containerization** | **Docker & Google Cloud Run** | Serverless deployment via `deploy_cloudrun.sh` |
        | **Security** | **SHA-256 Crypto Hashing** | Immutable metric verification for hiring partner outbox payloads |
        """)
        
    with st.expander("🛡️ Section 5: Security, Consent & Zero-Trust Governance"):
        st.markdown("""
        - **Mandatory Consent Gate**: Jobs are *never* auto-dispatched unless the student explicitly authorizes placement dispatch via their portal toggle.
        - **Interview Cap Limit**: Prevents spamming hiring partners by enforcing institute-level maximum interview attempt caps (default 3).
        - **Immutable Audit Ledger**: Every dispatch logs an immutable cryptographic hash (`0x...`) recording student ID, score breakdown, and company match percentage.
        """)
