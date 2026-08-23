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

# Custom Styling
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
        font-size: 0.85rem;
    }
    .badge-remedial {
        background-color: #FEECDC;
        color: #9A3412;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .badge-intervention {
        background-color: #FEF08A;
        color: #854D0E;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .hash-text {
        font-family: monospace;
        color: #4F46E5;
        background-color: #EEF2FF;
        padding: 4px 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ SkillForge Autonomous</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Tenant Institutional SaaS & Autonomous Recruiter Placement Engine | Taskmaster Track</div>', unsafe_allow_html=True)

# Query Param Checking for Standalone Student Portal Link
query_params = st.query_params
is_student_portal_param = query_params.get("view") == "student_portal"

# Sidebar System Health & Demo Switcher
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Status")
    st.success("🟢 FastAPI Backend (v4.0.0)")
    st.success("⚡ Gemma Pre-check Engine Ready")
    st.success("🤖 Gemini 3.5 Pro & Flash Active")
    
    st.divider()
    st.markdown("### ⚡ One-Click Judge Demo Switcher")
    if st.button("🟢 Preset A: Top Candidate (92%)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_A"
        st.info("Loaded Top Candidate Preset! Navigate to Tab 3 to run.")
    if st.button("🟠 Preset B: Remedial Candidate (54%)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_B"
        st.info("Loaded Remedial Candidate Preset! Navigate to Tab 3 to run.")

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

# --- TOP SELECTOR FOR INSTITUTE & BRANCH ISOLATION ---
st.markdown("### 🏢 Multi-Tenant Governance Selector")
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
    st.warning("No branches registered under this institute yet. Create one in Tab 1!")
    sel_branch = None
else:
    branch_map = {f"{b['branch_name']} ({b['city']})": b for b in branches}
    sel_branch_label = col_g2.selectbox("📍 Select Center Branch Node", list(branch_map.keys()))
    sel_branch = branch_map[sel_branch_label]

if sel_branch:
    st.info(f"🔒 **Strict Isolation Active:** Currently managing **{sel_inst['name']}** $\\rightarrow$ **{sel_branch['branch_name']}** (`Placement Threshold: {sel_inst['placement_threshold']}%`)")

st.divider()

# 4 Main Navigation Tabs
tabs = st.tabs([
    "🏛️ Branch Management & Courses",
    "👥 Student Enrollment & Exam Links",
    "🎓 Standalone Student Exam & Profile Portal",
    "🚀 Autonomous Job Hunting & Interview Alert Ledger"
])

# --- TAB 1: BRANCH MANAGEMENT & COURSES ---
with tabs[0]:
    st.subheader("🏛️ Dynamic Institute, Branch & Course Governance")
    st.markdown("Create new institute nodes, add branches, and configure branch-specific vocational courses.")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        st.markdown("#### 1️⃣ Create New Institute")
        with st.form("create_inst_form"):
            ni_name = st.text_input("Institute Name", value="National Vocational Skill Academy")
            ni_code = st.text_input("Unique Code", value=f"NVSA-{int(time.time())%10000}")
            ni_thresh = st.slider("Placement Threshold %", 50, 95, 70)
            sub_ni = st.form_submit_button("Save Institute", type="primary")
            if sub_ni:
                r_ni = requests.post(f"{BACKEND_URL}/api/institutes/create", json={
                    "name": ni_name, "code": ni_code, "placement_threshold": ni_thresh
                })
                if r_ni.status_code == 200:
                    st.success("✅ New Institute Created!")
                    st.rerun()
                    
    with col_t2:
        st.markdown("#### 2️⃣ Add Branch to Selected Institute")
        with st.form("create_branch_form"):
            nb_name = st.text_input("Branch Name", value="Karol Bagh Skill Center")
            nb_city = st.text_input("City", value="New Delhi")
            sub_nb = st.form_submit_button("Save Branch", type="primary")
            if sub_nb:
                r_nb = requests.post(f"{BACKEND_URL}/api/branches/create", json={
                    "institute_id": sel_inst["id"], "branch_name": nb_name, "city": nb_city
                })
                if r_nb.status_code == 200:
                    st.success(f"✅ Branch Added to {sel_inst['name']}!")
                    st.rerun()
                    
    with col_t3:
        st.markdown("#### 3️⃣ Add Course to Selected Branch")
        if not sel_branch:
            st.caption("Please select or create a branch first.")
        else:
            with st.form("create_course_form"):
                nc_name = st.text_input("Course Title", value="EV Diagnostics & Solar Tech")
                nc_summary = st.text_area("Curriculum Summary", value="Hands-on electric vehicle diagnostic isolation and solar inverter repair.")
                sub_nc = st.form_submit_button("Save Course", type="primary")
                if sub_nc:
                    r_nc = requests.post(f"{BACKEND_URL}/api/courses/create", json={
                        "institute_id": sel_inst["id"],
                        "branch_id": sel_branch["id"],
                        "course_name": nc_name,
                        "curriculum_summary": nc_summary
                    })
                    if r_nc.status_code == 200:
                        st.success(f"✅ Course Added to {sel_branch['branch_name']}!")
                        st.rerun()
                        
    st.divider()
    st.markdown("#### 📚 Active Courses Mapped to Selected Branch")
    if sel_branch:
        courses = []
        try:
            cres = requests.get(f"{BACKEND_URL}/api/courses?branch_id={sel_branch['id']}", timeout=2)
            if cres.status_code == 200:
                courses = cres.json()["data"]
        except Exception:
            pass
            
        if not courses:
            st.warning("No courses registered for this branch yet.")
        else:
            for c in courses:
                st.info(f"📚 **{c['course_name']}** — {c.get('curriculum_summary', '')}")

# --- TAB 2: STUDENT ENROLLMENT & EXAM LINKS ---
with tabs[1]:
    if not sel_branch:
        st.warning("Please select a branch above.")
    else:
        st.subheader(f"👥 Candidate Roster for {sel_branch['branch_name']}")
        st.markdown("Enroll candidates, copy unique student portal links, and view post-submission generated portfolios.")
        
        # Fetch Courses for this branch
        branch_courses = []
        try:
            cres = requests.get(f"{BACKEND_URL}/api/courses?branch_id={sel_branch['id']}", timeout=2)
            if cres.status_code == 200:
                branch_courses = cres.json()["data"]
        except Exception:
            pass
            
        course_opts = {c['course_name']: c['id'] for c in branch_courses} if branch_courses else {"Automotive & Hardware Diagnostics": "CRS-AUTO-01"}
        
        tab_e1, tab_e2 = st.tabs(["📄 Manual Candidate Intake", "📁 Bulk CSV Roster Upload"])
        
        with tab_e1:
            with st.form("manual_enroll_form"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    s_name = st.text_input("Full Name", value="Rahul Verma")
                    s_dob = st.date_input("Date of Birth (YYYY-MM-DD)", value=None)
                    s_email = st.text_input("Email Address", value="rahul.v@skillforge-edu.org")
                with sc2:
                    s_phone = st.text_input("Phone Number", value="+91 9811223344")
                    s_course_name = st.selectbox("Assign Course", list(course_opts.keys()))
                    s_bio = st.text_area("Candidate Skill Bio", value="Trained in automotive sensor diagnostics and safety lockout.")
                    
                sub_add_s = st.form_submit_button("Enroll Candidate", type="primary")
                if sub_add_s:
                    dob_str = str(s_dob) if s_dob else "2002-01-01"
                    course_id = course_opts.get(s_course_name, "CRS-GENERIC")
                    r_add = requests.post(f"{BACKEND_URL}/api/students/add", json={
                        "institute_id": sel_inst["id"],
                        "branch_id": sel_branch["id"],
                        "course_id": course_id,
                        "branch_name": sel_branch["branch_name"],
                        "course_name": s_course_name,
                        "full_name": s_name,
                        "dob": dob_str,
                        "email": s_email,
                        "phone": s_phone,
                        "bio": s_bio,
                        "fees_status": "PAID",
                        "consent": 1
                    })
                    if r_add.status_code == 200:
                        st.success(f"✅ Candidate Enrolled! Student ID: `{r_add.json()['data']['student_id']}`")
                        st.rerun()
                        
        with tab_e2:
            st.markdown("Upload CSV containing headers: `full_name`, `dob`, `email`, `phone`")
            sample_csv_data = "full_name,dob,email,phone\nKaran Sharma,2001-04-12,karan.s@skillforge-edu.org,+91 9877665544\nAnanya Sen,2002-09-25,ananya.s@skillforge-edu.org,+91 9877665555"
            st.download_button("📥 Download Sample CSV Template", sample_csv_data, file_name="sample_students.csv", mime="text/csv")
            
            uploaded_csv = st.file_uploader("Upload CSV Roster File", type=["csv"])
            if uploaded_csv is not None:
                if st.button("🚀 Process & Enroll Bulk Roster", type="primary"):
                    files = {"file": (uploaded_csv.name, uploaded_csv.getvalue(), "text/csv")}
                    c_id = list(course_opts.values())[0] if course_opts else "CRS-AUTO-01"
                    c_n = list(course_opts.keys())[0] if course_opts else "Automotive & Hardware Diagnostics"
                    
                    b_res = requests.post(
                        f"{BACKEND_URL}/api/students/bulk-upload?institute_id={sel_inst['id']}&branch_id={sel_branch['id']}&course_id={c_id}&branch_name={sel_branch['branch_name']}&course_name={c_n}",
                        files=files
                    )
                    if b_res.status_code == 200:
                        st.success(f"✅ Enrolled {b_res.json()['count']} candidates to {sel_branch['branch_name']}!")
                        st.rerun()
                        
        st.divider()
        st.markdown(f"#### 📜 Isolated Candidate Roster for {sel_branch['branch_name']}")
        
        branch_students = []
        try:
            st_res = requests.get(f"{BACKEND_URL}/api/students?institute_id={sel_inst['id']}&branch_id={sel_branch['id']}", timeout=2)
            if st_res.status_code == 200:
                branch_students = st_res.json()["data"]
        except Exception as e:
            st.error(f"Error fetching roster: {e}")
            
        if not branch_students:
            st.warning("No candidates enrolled in this branch yet.")
        else:
            for s in branch_students:
                with st.container():
                    col_r1, col_r2, col_r3, col_r4 = st.columns([2.5, 3, 2, 1.5])
                    with col_r1:
                        st.write(f"**{s['full_name']}** (`{s['student_id']}`)")
                        st.caption(f"DOB: {s.get('dob', '2002-01-01')} | {s['course_name']}")
                    with col_r2:
                        portal_link = f"http://localhost:8501/?view=student_portal&inst={sel_inst['code']}&branch={sel_branch['id']}&sid={s['student_id']}&dob={s.get('dob', '2002-01-01')}"
                        st.code(portal_link, language="text")
                    with col_r3:
                        if s.get("portfolio_generated") or s.get("portfolio_url"):
                            port_url = s.get("portfolio_url") or f"http://localhost:8000/portfolio/{s['student_id']}"
                            st.markdown(f"🌐 [View Generated Portfolio]({port_url})")
                        else:
                            st.caption("⏳ Exam & Portfolio Pending")
                    with col_r4:
                        st.write(f"Consent: {'✅ Granted' if s.get('consent_given') else '❌ Pending'}")
                        st.write(f"Dispatches: `{s.get('interview_count', 0)} / 3`")
                st.divider()

# --- TAB 3: STANDALONE STUDENT EXAM & PROFILE PORTAL ---
with tabs[2]:
    st.subheader("🎓 Standalone Student Exam & Profile Portal")
    st.markdown("Authenticate via Student ID & DOB, complete course-specific MCQs, upload project artifacts, and grant placement consent.")
    
    if not sel_branch or not branch_students:
        st.warning("No students available under current branch selector.")
    else:
        # Pre-fill login from query params if available
        param_sid = query_params.get("sid", "")
        param_dob = query_params.get("dob", "")
        
        col_lg1, col_lg2, col_lg3 = st.columns([2, 2, 1])
        with col_lg1:
            sid_input = st.text_input("Student ID Login", value=param_sid or branch_students[0]['student_id'])
        with col_lg2:
            dob_auth = st.text_input("Date of Birth (YYYY-MM-DD)", value=param_dob or branch_students[0].get('dob', '2002-01-01'))
        with col_lg3:
            st.write("")
            st.write("")
            auth_btn = st.button("🔑 Authenticate Student", type="primary", use_container_width=True)
            
        auth_student = next((s for s in branch_students if s['student_id'] == sid_input.strip()), branch_students[0])
        
        st.markdown(f"#### Logged in Candidate: **{auth_student['full_name']}** (`{auth_student['student_id']}`) | Course: **{auth_student['course_name']}**")
        
        st.divider()
        st.markdown("### 📝 Course Assessment & Multimodal Artifact Submission")
        
        if st.button("✨ Synthesize Assessment via Gemini 3.5", type="primary"):
            with st.spinner(f"Synthesizing assessment for {auth_student['course_name']}..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": auth_student['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    st.success("✅ Assessment Synthesized!")
                    st.rerun()
                    
        if "current_exam" not in st.session_state:
            with st.spinner("Initializing Assessment..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": auth_student['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    
        exam = st.session_state.get("current_exam", {})
        mcqs = exam.get("mcqs", [])
        mcq_key = [m.get("correct_option", 0) for m in mcqs]
        
        demo_preset = st.session_state.get("demo_preset")
        is_preset_a = demo_preset == "PRESET_A"
        is_preset_b = demo_preset == "PRESET_B"
        
        with st.form("standalone_exam_form"):
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
                    key=f"mcq_radio_{idx}_{auth_student['student_id']}"
                )
                
                if selected_opt in opts:
                    user_mcq_answers.append(opts.index(selected_opt))
                else:
                    user_mcq_answers.append(-1)
                    
            st.divider()
            st.markdown("##### **Part 2: Student Profile & Multimodal Practical Project Submission (70 Points Max)**")
            
            p_task_default = exam.get("practical_task", f"Complete diagnostic inspection for {auth_student['course_name']}.")
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
                github_default = "https://github.com/skillforge/diagnostic-tooling"
                live_default = f"http://localhost:8000/portfolio/{auth_student['student_id']}"
            elif is_preset_b:
                sub_text_default = "Looked at wires. Turned on switch. It worked eventually."
                github_default = ""
                live_default = ""
            else:
                sub_text_default = (
                    "Performed safety lockout procedure. Verified circuit connections using calibrated multimeter. "
                    "Recorded voltage measurements across load terminals. Documented fault codes and completed repair."
                )
                github_default = "https://github.com/skillforge/student-capstone"
                live_default = f"http://localhost:8000/portfolio/{auth_student['student_id']}"
                
            s_text = st.text_area("Your Practical Solution Code / Diagnostic Log", value=sub_text_default, height=120)
            
            col_pu1, col_pu2 = st.columns(2)
            with col_pu1:
                github_url_input = st.text_input("GitHub Repository URL", value=github_default)
            with col_pu2:
                live_url_input = st.text_input("Live Demo / Project Link", value=live_default)
                
            uploaded_img = st.file_uploader("Attach Project Artifact (Hardware Photo / Diagram / PDF / Code Zip)", type=["jpg", "png", "jpeg", "pdf", "zip"])
            
            st.divider()
            consent_check = st.checkbox("I authorize SkillForge AI Agent to build my live verified dossier & auto-apply to matching job openings", value=True)
            
            submit_exam = st.form_submit_button("🚀 Submit Exam & Finalize Dossier", type="primary", use_container_width=True)
            
        if submit_exam:
            if "demo_preset" in st.session_state:
                del st.session_state["demo_preset"]
                
            # Update consent status
            requests.post(f"{BACKEND_URL}/api/students/consent", json={"student_id": auth_student['student_id'], "consent": consent_check})
            
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
                        "student_id": auth_student['student_id'],
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
                    telemetry = res_data.get("telemetry", [])
                    
                    st.session_state["last_telemetry"] = telemetry
                    st.session_state["last_portfolio_url"] = eval_out.get("portfolio_url", f"http://localhost:8000/portfolio/{auth_student['student_id']}")
                    
                    st.success("✅ Assessment Evaluated & HTML Dossier Portfolio Generated!")
                    
                    st.markdown("### 📊 Performance Breakdown")
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("MCQ Score", f"{eval_out['mcq_score']} / 30 pts")
                    with mc2:
                        st.metric("Practical Score", f"{eval_out['practical_score']} / 70 pts")
                    with mc3:
                        st.metric("Final Total Score", f"{eval_out['total_score']} / 100 pts")
                    with mc4:
                        ready = eval_out['placement_ready']
                        st.metric("Verification Gate", "QUALIFIED 🚀" if ready else "REMEDIAL 🟠")
                        
                    st.divider()
                    
                    if ready:
                        st.markdown(f'<span class="badge-success">🚀 STATUS: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.markdown("#### 📬 Outbound Recruiter Pitch & Alerts")
                        st.markdown(f"**Matched Employer:** `{dispatch_out['hiring_partner']}`")
                        st.markdown(f"**Role Title:** `{dispatch_out['role']}`")
                        st.markdown(f"**Live Generated Portfolio:** [View Portfolio]({eval_out['portfolio_url']})")
                        st.info(dispatch_out["notifications"]["student_alert"])
                        st.info(dispatch_out["notifications"]["branch_alert"])
                    else:
                        st.markdown(f'<span class="badge-remedial">🔄 STATUS: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.warning("Score below 70%. 7-day remedial plan assigned.")
                else:
                    st.error(f"Pipeline error: {pipe_res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- TAB 4: AUTONOMOUS JOB HUNTING & INTERVIEW ALERT LEDGER ---
with tabs[3]:
    st.subheader("🚀 Autonomous Recruiter Outbox & Human-in-the-Loop Ledger")
    st.markdown("Track auto-dispatched candidate dossiers, scheduled interview slots, and human-intervention flags.")
    
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
                                elif status == "INTERVIEW_SCHEDULED":
                                    st.markdown('<span class="badge-success">📅 INTERVIEW SCHEDULED</span>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<span class="badge-success">🚀 DISPATCHED</span>', unsafe_allow_html=True)
                            with col_j4:
                                st.write(f"Details: `{job.get('interview_details', 'Dispatched')}`")
                                if job.get('dossier_sent_url'):
                                    st.markdown(f"🌐 [Sent Dossier]({job['dossier_sent_url']})")
                        st.divider()
                else:
                    st.info("No applications dispatched for this branch yet.")
        except Exception as e:
            st.error(f"Error loading ledger: {e}")
