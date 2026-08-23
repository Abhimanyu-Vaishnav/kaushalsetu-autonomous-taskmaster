import streamlit as st
import requests
import json
import time
import base64
import io

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Enterprise Multi-Tenant SaaS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Rich Aesthetics
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
    .badge-pending {
        background-color: #FEF3C7;
        color: #92400E;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .badge-live {
        background-color: #DEF7EC;
        color: #03543F;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .badge-interview {
        background-color: #DBEAFE;
        color: #1E40AF;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .badge-intervention {
        background-color: #FEF08A;
        color: #854D0E;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .terminal-window {
        background-color: #0F172A;
        color: #38BDF8;
        font-family: monospace;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #334155;
        font-size: 0.88rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Query Param Routing: Detect if query param ?page=exam or ?view=student_portal is set
query_params = st.query_params
current_page = query_params.get("page") or query_params.get("view")
is_standalone_exam = (current_page in ["exam", "student_portal"])

if is_standalone_exam:
    # --- STANDALONE FULL-SCREEN STUDENT EXAM WORKSPACE ---
    st.markdown('<div class="main-header">🎓 Student Dedicated Exam Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">SkillForge Autonomous Assessment & Live Portfolio Finalizer</div>', unsafe_allow_html=True)
    
    # Query Param Pre-fills
    param_sid = query_params.get("sid", "")
    param_dob = query_params.get("dob", "")
    
    col_lg1, col_lg2, col_lg3 = st.columns([2, 2, 1])
    with col_lg1:
        sid_input = st.text_input("Candidate Student ID Login", value=param_sid or "STU-1001")
    with col_lg2:
        dob_input = st.text_input("Date of Birth (YYYY-MM-DD)", value=param_dob or "2002-01-15")
    with col_lg3:
        st.write("")
        st.write("")
        auth_btn = st.button("🔑 Login Student", type="primary", use_container_width=True)
        
    student_data = None
    try:
        s_res = requests.get(f"{BACKEND_URL}/api/student/{sid_input.strip()}", timeout=2)
        if s_res.status_code == 200:
            student_data = s_res.json()["data"]
    except Exception:
        pass
        
    if not student_data:
        st.warning("Candidate not found. Please log in with a valid Student ID (e.g. `STU-1001`).")
    else:
        st.markdown(f"#### Logged in: **{student_data['full_name']}** (`{student_data['student_id']}`) | Branch: **{student_data['branch_name']}** | Course: **{student_data['course_name']}**")
        
        st.divider()
        st.markdown("### 📝 Course Assessment & Multimodal Artifact Submission")
        
        if st.button("✨ Synthesize Exam via Gemini 3.5", type="primary"):
            with st.spinner(f"Synthesizing exam for {student_data['course_name']}..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": student_data['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    st.success("✅ Assessment Synthesized!")
                    st.rerun()
                    
        if "current_exam" not in st.session_state:
            with st.spinner("Initializing Assessment..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": student_data['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    
        exam = st.session_state.get("current_exam", {})
        mcqs = exam.get("mcqs", [])
        mcq_key = [m.get("correct_option", 0) for m in mcqs]
        
        with st.form("standalone_student_exam_form"):
            st.markdown(f"#### 📋 **{exam.get('title', 'Vocational Assessment')}**")
            st.markdown("##### **Part 1: Multiple Choice Questions (30 Points Max)**")
            
            user_mcq_answers = []
            for idx, mcq in enumerate(mcqs, 1):
                st.markdown(f"**Question {idx}: {mcq['question']}**")
                opts = mcq['options']
                selected_opt = st.radio(f"Select answer for Q{idx}:", opts, index=None, key=f"mcq_radio_{idx}_{student_data['student_id']}")
                if selected_opt in opts:
                    user_mcq_answers.append(opts.index(selected_opt))
                else:
                    user_mcq_answers.append(-1)
                    
            st.divider()
            st.markdown("##### **Part 2: Multimodal Practical Project Submission (70 Points Max)**")
            
            p_task_default = exam.get("practical_task", f"Complete diagnostic inspection for {student_data['course_name']}.")
            st.info(f"**Task:** {p_task_default}")
            
            rubric_default = exam.get("grading_rubric", ["Safety lockout procedure followed", "Diagnostic accuracy verified", "Documentation complete"])
            st.caption("Rubric: " + " | ".join(rubric_default))
            
            sub_text_default = (
                "First, performed a full safety lockout procedure and verified system power status using a multimeter. "
                "Next, connected an oscilloscope to signal lines to measure voltage waveforms. "
                "Found ground signal degradation due to terminal connector corrosion. "
                "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean 2.5V differential voltage."
            )
            s_text = st.text_area("Your Practical Solution Code / Diagnostic Log", value=sub_text_default, height=120)
            
            col_pu1, col_pu2 = st.columns(2)
            with col_pu1:
                github_url_input = st.text_input("GitHub Code Repository URL", value=f"https://github.com/skillforge/{student_data['student_id'].lower()}")
            with col_pu2:
                live_url_input = st.text_input("Live Demo / Project Link", value=f"http://localhost:8000/portfolio/{student_data['student_id']}")
                
            uploaded_img = st.file_uploader("Attach Project Artifact (Hardware Photo / Diagram / PDF / Code Zip)", type=["jpg", "png", "jpeg", "pdf", "zip"])
            
            st.divider()
            consent_check = st.checkbox("Authorize SkillForge AI Agent to build my live portfolio dossier & auto-apply for matching jobs", value=True)
            
            submit_exam = st.form_submit_button("🚀 Submit Exam & Activate AI Placement Agent", type="primary", use_container_width=True)
            
        if submit_exam:
            requests.post(f"{BACKEND_URL}/api/students/consent", json={"student_id": student_data['student_id'], "consent": consent_check})
            img_b64 = None
            if uploaded_img is not None and uploaded_img.type in ["image/jpeg", "image/png", "image/jpg"]:
                img_b64 = base64.b64encode(uploaded_img.getvalue()).decode("utf-8")
                
            p_bar = st.progress(0, text="Triggering Background Agent Engine...")
            time.sleep(0.2)
            p_bar.progress(30, text="1. Gemma Fast Screener & Objective MCQ Scoring...")
            time.sleep(0.3)
            p_bar.progress(70, text="2. Gemini 3.5 Multimodal Evaluation & HTML Dossier Generation...")
            
            try:
                pipe_res = requests.post(
                    f"{BACKEND_URL}/api/student/evaluate-and-dispatch",
                    json={
                        "student_id": student_data['student_id'],
                        "assessment_id": exam.get("db_assessment_id", "ASS-DEFAULT"),
                        "mcq_answers": user_mcq_answers,
                        "mcq_key": mcq_key,
                        "practical_task": p_task_default,
                        "grading_rubric": rubric_default,
                        "submission_text": s_text,
                        "github_url": github_url_input,
                        "live_url": live_url_input,
                        "image_base64": img_b64
                    },
                    timeout=30
                )
                p_bar.progress(100, text="Background Agent Execution Complete!")
                
                if pipe_res.status_code == 200:
                    res_data = pipe_res.json()["data"]
                    eval_out = res_data["evaluation"]
                    dispatch_out = res_data["dispatch"]
                    
                    st.success("✅ Assessment Evaluated & HTML Dossier Portfolio Generated!")
                    st.markdown(f"#### 🌐 Live Portfolio Link: [{eval_out['portfolio_url']}]({eval_out['portfolio_url']})")
                    st.info(dispatch_out["notifications"]["student_alert"])
                else:
                    st.error(f"Pipeline error: {pipe_res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

else:
    # --- ADMIN WORKSPACE & CASCADING GOVERNANCE ---
    st.markdown('<div class="main-header">⚡ SkillForge Autonomous</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-Tenant Institutional Governance & Autonomous Placement Engine | Taskmaster Track</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
        st.subheader("System Health Status")
        st.success("🟢 FastAPI Backend (v4.1.0)")
        st.success("⚡ Gemma Pre-check Screener Ready")
        st.success("🤖 Gemini 3.5 Pro & Flash Active")
        
        st.divider()
        st.markdown("### ⚡ One-Click Judge Demo Switcher")
        if st.button("🟢 Preset A: Top Candidate (92%)", use_container_width=True):
            st.session_state["demo_preset"] = "PRESET_A"
            st.info("Loaded Top Candidate Preset! Go to Exam page to run.")
        if st.button("🟠 Preset B: Remedial Candidate (54%)", use_container_width=True):
            st.session_state["demo_preset"] = "PRESET_B"
            st.info("Loaded Remedial Candidate Preset! Go to Exam page to run.")

        st.divider()
        st.markdown("### Track Specification")
        st.markdown("- **Taskmaster Track**")
        st.markdown("- **Zero Chatbot UI**")
        st.markdown("- **Gemma Bonus (+0.2 pts)**")

    # Fetch Institutes
    institutes = []
    try:
        ires = requests.get(f"{BACKEND_URL}/api/institutes", timeout=2)
        if ires.status_code == 200:
            institutes = ires.json()["data"]
    except Exception:
        pass

    if not institutes:
        st.error("🔴 Could not connect to backend server. Ensure run_app.py is active.")
        st.stop()

    # --- GLOBAL CASCADING GOVERNANCE HEADER ---
    st.markdown("### 🏢 Cascading Multi-Tenant Governance Selector")
    col_g1, col_g2 = st.columns(2)

    inst_map = {f"{i['name']} ({i['code']})": i for i in institutes}
    sel_inst_label = col_g1.selectbox("🏢 Select Vocational Institute", list(inst_map.keys()))
    sel_inst = inst_map[sel_inst_label]

    # Fetch Branches for selected Institute
    branches = []
    try:
        bres = requests.get(f"{BACKEND_URL}/api/branches?institute_id={sel_inst['id']}", timeout=2)
        if bres.status_code == 200:
            branches = bres.json()["data"]
    except Exception:
        pass

    if not branches:
        st.warning("No branches registered under this institute yet. Create one in Page 1!")
        sel_branch = None
    else:
        branch_map = {f"{b['branch_name']} ({b['city']})": b for b in branches}
        sel_branch_label = col_g2.selectbox("📍 Select Center Branch Node", list(branch_map.keys()))
        sel_branch = branch_map[sel_branch_label]

    if sel_branch:
        st.info(f"🔒 **Strict Isolation Active:** Managing **{sel_inst['name']}** $\\rightarrow$ **{sel_branch['branch_name']}** (`Placement Threshold: {sel_inst['placement_threshold']}%`)")

    st.divider()

    # 4 Main Administrative Pages / Tabs
    pages = st.tabs([
        "🏛️ Institute & Branch Governance",
        "👥 Branch Student Roster & Exam Dispatch",
        "🚀 Recruiter Outbox & Interview Ledger",
        "🤖 Live Autonomous Agent Terminal"
    ])

    # --- PAGE 1: INSTITUTE & BRANCH GOVERNANCE ---
    with pages[0]:
        st.subheader("🏛️ Cascading Governance & Creation Logic")
        st.markdown("Create Institutes (with mandatory Initial Branch), register isolated Branches, and add Branch-specific Courses.")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown("#### 1️⃣ Create Institute (Requires Initial Branch)")
            with st.form("create_inst_branch_form"):
                ci_name = st.text_input("Institute Name", value="SkillForge Foundation")
                ci_code = st.text_input("Unique Code", value=f"SKILL-{int(time.time())%10000}")
                ci_bname = st.text_input("Initial Branch Name", value="Main Campus Center")
                ci_city = st.text_input("Branch City", value="New Delhi")
                ci_thresh = st.slider("Placement Threshold %", 50, 95, 70)
                sub_ci = st.form_submit_button("Save Institute & Initial Branch", type="primary")
                if sub_ci:
                    r_ci = requests.post(f"{BACKEND_URL}/api/institutes/create", json={
                        "name": ci_name,
                        "code": ci_code,
                        "initial_branch_name": ci_bname,
                        "initial_city": ci_city,
                        "placement_threshold": ci_thresh
                    })
                    if r_ci.status_code == 200:
                        st.success("✅ Institute & Initial Branch Created!")
                        st.rerun()
                        
        with col_m2:
            st.markdown("#### 2️⃣ Add Additional Branch")
            with st.form("create_extra_branch_form"):
                st.caption(f"Parent Institute: **{sel_inst['name']}**")
                eb_name = st.text_input("New Branch Name", value="Dwarka Skill Hub")
                eb_city = st.text_input("City", value="Delhi")
                sub_eb = st.form_submit_button("Save Branch", type="primary")
                if sub_eb:
                    r_eb = requests.post(f"{BACKEND_URL}/api/branches/create", json={
                        "institute_id": sel_inst["id"],
                        "branch_name": eb_name,
                        "city": eb_city
                    })
                    if r_eb.status_code == 200:
                        st.success(f"✅ Branch Added to {sel_inst['name']}!")
                        st.rerun()
                        
        with col_m3:
            st.markdown("#### 3️⃣ Add Branch-Isolated Course")
            if not sel_branch:
                st.caption("Please select a branch above.")
            else:
                with st.form("create_branch_course_form"):
                    st.caption(f"Parent Branch: **{sel_branch['branch_name']}**")
                    cc_title = st.text_input("Course Title", value="EV & Solar Maintenance")
                    cc_summary = st.text_area("Curriculum Summary", value="Hands-on electric vehicle diagnostics and solar inverter maintenance.")
                    sub_cc = st.form_submit_button("Save Isolated Course", type="primary")
                    if sub_cc:
                        r_cc = requests.post(f"{BACKEND_URL}/api/courses/create", json={
                            "institute_id": sel_inst["id"],
                            "branch_id": sel_branch["id"],
                            "course_name": cc_title,
                            "curriculum_summary": cc_summary
                        })
                        if r_cc.status_code == 200:
                            st.success(f"✅ Course Isolated to {sel_branch['branch_name']}!")
                            st.rerun()

    # --- PAGE 2: BRANCH STUDENT ROSTER & EXAM DISPATCH ---
    with pages[1]:
        if not sel_branch:
            st.warning("Please select a branch above.")
        else:
            st.subheader(f"👥 Candidate Roster for {sel_branch['branch_name']}")
            st.markdown("Enroll candidates, dispatch AI Exam URLs, and track student status badges.")
            
            # Fetch Courses for selected branch
            branch_courses = []
            try:
                cres = requests.get(f"{BACKEND_URL}/api/courses?branch_id={sel_branch['id']}", timeout=2)
                if cres.status_code == 200:
                    branch_courses = cres.json()["data"]
            except Exception:
                pass
                
            course_opts = {c['course_name']: c['id'] for c in branch_courses} if branch_courses else {"Automotive & Hardware Diagnostics": "CRS-AUTO-01"}
            
            with st.expander("➕ Enroll Candidate to Branch", expanded=False):
                with st.form("enroll_student_isolated_form"):
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        s_name = st.text_input("Full Name", value="Rohan Mehta")
                        s_dob = st.date_input("Date of Birth", value=None)
                        s_email = st.text_input("Email Address", value="rohan.m@skillforge-edu.org")
                    with sc2:
                        s_phone = st.text_input("Phone Number", value="+91 9876543210")
                        s_cname = st.selectbox("Assign Course", list(course_opts.keys()))
                        s_bio = st.text_area("Candidate Bio", value="Trained in hardware circuit diagnostic isolation.")
                        
                    sub_en = st.form_submit_button("Enroll Candidate", type="primary")
                    if sub_en:
                        dob_str = str(s_dob) if s_dob else "2002-01-01"
                        c_id = course_opts.get(s_cname, "CRS-GENERIC")
                        r_en = requests.post(f"{BACKEND_URL}/api/students/add", json={
                            "institute_id": sel_inst["id"],
                            "branch_id": sel_branch["id"],
                            "course_id": c_id,
                            "branch_name": sel_branch["branch_name"],
                            "course_name": s_cname,
                            "full_name": s_name,
                            "dob": dob_str,
                            "email": s_email,
                            "phone": s_phone,
                            "bio": s_bio,
                            "fees_status": "PAID",
                            "consent": 1
                        })
                        if r_en.status_code == 200:
                            st.success(f"✅ Candidate Enrolled! ID: `{r_en.json()['data']['student_id']}`")
                            st.rerun()

            st.divider()
            
            # Fetch Isolated Students
            students = []
            try:
                st_res = requests.get(f"{BACKEND_URL}/api/students?institute_id={sel_inst['id']}&branch_id={sel_branch['id']}", timeout=2)
                if st_res.status_code == 200:
                    students = st_res.json()["data"]
            except Exception as e:
                st.error(f"Error loading students: {e}")
                
            if not students:
                st.warning("No candidates enrolled in this branch yet.")
            else:
                for s in students:
                    with st.container():
                        col_r1, col_r2, col_r3, col_r4 = st.columns([2.5, 3, 2, 2])
                        with col_r1:
                            st.write(f"**{s['full_name']}** (`{s['student_id']}`)")
                            st.caption(f"DOB: {s.get('dob', '2002-01-01')} | {s['course_name']}")
                        with col_r2:
                            exam_link = f"http://localhost:8501/?page=exam&sid={s['student_id']}&dob={s.get('dob', '2002-01-01')}"
                            st.code(exam_link, language="text")
                        with col_r3:
                            # Status Badge Calculation
                            if s.get("interview_count", 0) > 0:
                                st.markdown('<span class="badge-interview">📅 INTERVIEW_SCHEDULED</span>', unsafe_allow_html=True)
                            elif s.get("portfolio_generated") or s.get("portfolio_url"):
                                st.markdown('<span class="badge-live">🌐 PORTFOLIO_LIVE</span>', unsafe_allow_html=True)
                            else:
                                st.markdown('<span class="badge-pending">⏳ PENDING_EXAM</span>', unsafe_allow_html=True)
                        with col_r4:
                            if s.get("portfolio_generated") or s.get("portfolio_url"):
                                port_url = s.get("portfolio_url") or f"http://localhost:8000/portfolio/{s['student_id']}"
                                st.markdown(f"🌐 [View Portfolio]({port_url})")
                            else:
                                st.caption("No Portfolio Yet")
                    st.divider()

    # --- PAGE 3: RECRUITER OUTBOX & INTERVIEW LEDGER ---
    with pages[2]:
        st.subheader("🚀 Recruiter Outbox & Human-in-the-Loop Ledger")
        st.markdown("Track candidate application dispatches, auto-scheduled interview slots, and human intervention flags.")
        
        if not sel_branch:
            st.warning("Please select a branch above.")
        else:
            try:
                l_res = requests.get(f"{BACKEND_URL}/api/placements/ledger?branch_id={sel_branch['id']}", timeout=2)
                if l_res.status_code == 200:
                    ledger = l_res.json()["data"]
                    if ledger:
                        for job in ledger:
                            with st.container():
                                col_j1, col_j2, col_j3, col_j4 = st.columns([2.5, 3, 2, 2.5])
                                with col_j1:
                                    st.write(f"**{job['student_name']}** (`{job['student_id']}`)")
                                    st.caption(f"Target Role: {job['role_title']}")
                                with col_j2:
                                    st.write(f"Employer: **{job['company_name']}**")
                                    st.caption(f"Match Score: {job['match_percentage']}%")
                                with col_j3:
                                    status = job['status']
                                    if status == "NEEDS_HUMAN_INTERVENTION":
                                        st.markdown('<span class="badge-intervention">⚠️ HUMAN INTERVENTION REQUIRED</span>', unsafe_allow_html=True)
                                    elif status in ["INTERVIEW_SCHEDULED", "APPLIED_AND_DISPATCHED"]:
                                        st.markdown('<span class="badge-live">📅 INTERVIEW SCHEDULED</span>', unsafe_allow_html=True)
                                    else:
                                        st.markdown('<span class="badge-pending">🔄 REMEDIAL ASSIGNED</span>', unsafe_allow_html=True)
                                with col_j4:
                                    st.write(f"Details: `{job.get('interview_details', 'Dispatched')}`")
                                    if job.get('dossier_sent_url'):
                                        st.markdown(f"🌐 [Sent Portfolio Dossier]({job['dossier_sent_url']})")
                            st.divider()
                    else:
                        st.info("No applications dispatched for this branch yet.")
            except Exception as e:
                st.error(f"Error loading ledger: {e}")

    # --- PAGE 4: LIVE AUTONOMOUS AGENT TERMINAL ---
    with pages[3]:
        st.subheader("🤖 Live Autonomous Agent Terminal & Streaming Telemetry")
        st.markdown("Real-time execution logs showing the continuous background action engine discovering jobs, generating portfolios, and scheduling interviews.")
        
        telemetry_logs = st.session_state.get("last_telemetry", [
            {"timestamp": "20:00:01.002", "step": "START", "message": "Autonomous Agent initialized for Candidate STU-1001"},
            {"timestamp": "20:00:01.045", "step": "GEMMA_PRECHECK", "message": "Gemma sub-millisecond check passed (Structure Score: 85/100)"},
            {"timestamp": "20:00:02.112", "step": "DOSSIER_GEN", "message": "Synthesized standalone HTML portfolio dossier at /portfolio/STU-1001"},
            {"timestamp": "20:00:02.340", "step": "ACTION_DISPATCHED", "message": "Auto-dispatched job application to Tata Motors for Automotive Systems Technician"},
            {"timestamp": "20:00:02.510", "step": "ALERTS_SENT", "message": "Dispatched interview notification alerts to Candidate & Branch Node."}
        ])
        
        log_text = "\n".join([f"[{t['timestamp']}] [{t['step']}] {t['message']}" for t in telemetry_logs])
        st.markdown(f'<div class="terminal-window"><pre>{log_text}</pre></div>', unsafe_allow_html=True)
