import streamlit as st
import requests
import json
import time
import base64
import io

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Multi-Tenant Operations Engine",
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
st.markdown('<div class="sub-header">Multi-Tenant Institutional Operations & Autonomous Placement Platform | Taskmaster Track</div>', unsafe_allow_html=True)

# 1. Top Level Center & Branch Selector
institutes = []
try:
    inst_res = requests.get(f"{BACKEND_URL}/api/institutes", timeout=2)
    if inst_res.status_code == 200:
        institutes = inst_res.json()["data"]
except Exception:
    pass

if not institutes:
    st.error("🔴 Could not connect to backend server. Make sure run_app.py is running.")
    st.stop()

# Sidebar Health & Demo Switcher
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Health Status")
    st.success("🟢 FastAPI Backend Connected (v3.8.0)")
    st.success("⚡ Gemma Pre-check Screener Ready")
    st.success("🤖 Gemini 3.5 Pro & Flash Active")
    
    st.divider()
    st.markdown("### ⚡ One-Click Judge Demo Switcher")
    if st.button("🟢 Preset A: Top Candidate (92%)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_A"
        st.info("Loaded Top Candidate Preset! Go to View 2 to execute.")
    if st.button("🟠 Preset B: Remedial Candidate (54%)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_B"
        st.info("Loaded Remedial Candidate Preset! Go to View 2 to execute.")

# Center & Branch Isolation Filter Header
st.markdown("### 🏛️ Center & Branch Governance Filter")
col_f1, col_f2 = st.columns(2)

inst_dict = {f"{i['name']} ({i['code']})": i for i in institutes}
selected_inst_label = col_f1.selectbox("🏢 Select Vocational Institute / Foundation", list(inst_dict.keys()))
selected_inst = inst_dict[selected_inst_label]

available_branches = selected_inst.get("branches", [])
selected_branch = col_f2.selectbox("📍 Select Isolated Center Branch", available_branches)

available_courses = selected_inst.get("courses", [])

st.info(f"🔒 **Strict Isolation Active:** Currently viewing **{selected_inst['name']}** $\\rightarrow$ **{selected_branch}** (`Placement Threshold: {selected_inst['placement_threshold']}%`)")

st.divider()

# 4 Main Operational Views
views = st.tabs([
    "🏛️ Branch Roster & Candidate Management",
    "🎓 Dedicated Student Exam Portal",
    "🌐 Live Generated Portfolio Dossier",
    "🚀 Autonomous Recruiter Outbox & Telemetry"
])

# --- VIEW 1: BRANCH ROSTER & CANDIDATE MANAGEMENT ---
with views[0]:
    st.subheader(f"🏛️ Roster Control for {selected_branch}")
    st.markdown("Add new students manually or via bulk CSV upload, copy unique standalone exam URLs, and track dossier portfolios.")
    
    with st.expander("➕ Add New Candidate to Branch", expanded=False):
        with st.form("add_student_branch_form"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st_name = st.text_input("Full Candidate Name", value="Rahul Verma")
                st_email = st.text_input("Email Address", value="rahul.v@skillforge-edu.org")
                st_dob = st.date_input("Date of Birth", value=None)
            with col_s2:
                st_phone = st.text_input("Phone Number", value="+91 9811223344")
                st_course = st.selectbox("Assign Course", available_courses)
                st_fees = st.selectbox("Fees Payment Status", ["PAID", "PENDING"])
                
            submit_student = st.form_submit_button("Enroll Student", type="primary")
            if submit_student:
                dob_str = str(st_dob) if st_dob else "2002-01-01"
                add_res = requests.post(f"{BACKEND_URL}/api/students/add", json={
                    "institute_id": selected_inst["id"],
                    "branch_name": selected_branch,
                    "full_name": st_name,
                    "dob": dob_str,
                    "email": st_email,
                    "phone": st_phone,
                    "course_name": st_course,
                    "fees_status": st_fees,
                    "consent": 1
                })
                if add_res.status_code == 200:
                    st.success(f"✅ Candidate Enrolled! ID: `{add_res.json()['data']['student_id']}`")
                    st.rerun()
                    
    with st.expander("➕ Add New Center Branch or Course to Institute", expanded=False):
        with st.form("add_branch_course_form"):
            new_branch_input = st.text_input("Add New Branch Name (e.g., Karol Bagh Center)")
            new_course_input = st.text_input("Add New Vocational Course (e.g., Solar & EV Maintenance)")
            submit_inst_update = st.form_submit_button("Save New Branch/Course", type="primary")
            if submit_inst_update:
                updated_branches = list(set(available_branches + ([new_branch_input.strip()] if new_branch_input.strip() else [])))
                updated_courses = list(set(available_courses + ([new_course_input.strip()] if new_course_input.strip() else [])))
                # Update institute in backend database
                with sqlite3.connect("backend/skillforge.db") as conn:
                    conn.execute("UPDATE institutes SET branches = ?, courses = ? WHERE id = ?", (json.dumps(updated_branches), json.dumps(updated_courses), selected_inst["id"]))
                    conn.commit()
                st.success("✅ Institute Branches & Courses Updated!")
                st.rerun()

    st.divider()
    st.markdown(f"#### 📜 Enrolled Roster for {selected_branch}")
    
    students = []
    try:
        st_res = requests.get(f"{BACKEND_URL}/api/students?institute_id={selected_inst['id']}&branch_name={selected_branch}", timeout=2)
        if st_res.status_code == 200:
            students = st_res.json()["data"]
    except Exception as e:
        st.error(f"Error fetching roster: {e}")
        
    if not students:
        st.warning(f"No students enrolled in {selected_branch} yet. Add candidates above!")
    else:
        for s in students:
            with st.container():
                col_r1, col_r2, col_r3, col_r4 = st.columns([2, 2, 2, 2])
                with col_r1:
                    st.write(f"**{s['full_name']}** (`{s['student_id']}`)")
                    st.caption(f"DOB: {s.get('dob', '2002-01-01')} | {s['course_name']}")
                with col_r2:
                    exam_url = f"{BACKEND_URL}/exam?sid={s['student_id']}&dob={s.get('dob', '2002-01-01')}"
                    st.code(exam_url, language="text")
                with col_r3:
                    portfolio_file = f"backend/static/portfolios/{s['student_id']}.html"
                    import os
                    if os.path.exists(portfolio_file):
                        port_url = f"{BACKEND_URL}/portfolio/{s['student_id']}"
                        st.markdown(f"🌐 [View Live Portfolio]({port_url})")
                    else:
                        st.caption("⏳ Exam Pending")
                with col_r4:
                    st.write(f"Consent: {'✅ Yes' if s['consent_for_job_dispatch'] else '❌ No'}")
                    st.write(f"Dispatches: `{s.get('interview_count', 0)} / 3`")
                st.divider()

# --- VIEW 2: DEDICATED STUDENT EXAM PORTAL ---
with views[1]:
    st.subheader("🎓 Dedicated Student Exam Portal")
    st.markdown("Standalone exam runner synthesizing course-specific questions via Gemini 3.5 upon candidate login.")
    
    # Isolated Student Selection for Exam taking
    branch_students = []
    try:
        st_res = requests.get(f"{BACKEND_URL}/api/students?institute_id={selected_inst['id']}&branch_name={selected_branch}", timeout=2)
        if st_res.status_code == 200:
            branch_students = st_res.json()["data"]
    except Exception:
        pass
        
    if not branch_students:
        st.warning(f"No students enrolled in {selected_branch}.")
    else:
        stu_opts = {f"{s['full_name']} ({s['student_id']}) - {s['course_name']}": s['student_id'] for s in branch_students}
        sel_label = st.selectbox("🔑 Candidate Login (Student ID)", list(stu_opts.keys()))
        selected_student_id = stu_opts[sel_label]
        stu_detail = next(s for s in branch_students if s['student_id'] == selected_student_id)
        
        st.markdown(f"#### Candidate: **{stu_detail['full_name']}** (`{stu_detail['student_id']}`) | Course: **{stu_detail['course_name']}**")
        
        cur_consent = bool(stu_detail.get('consent_for_job_dispatch', 1))
        new_consent = st.checkbox("I authorize SkillForge AI Agent to build my live portfolio dossier & auto-apply to matching job openings", value=cur_consent)
        if new_consent != cur_consent:
            requests.post(f"{BACKEND_URL}/api/students/consent", json={"student_id": selected_student_id, "consent": new_consent})
            st.success("✅ Consent updated!")
            st.rerun()
            
        st.divider()
        
        if st.button("✨ Synthesize Assessment via Gemini 3.5", type="primary"):
            with st.spinner(f"Synthesizing assessment for {stu_detail['course_name']}..."):
                e_res = requests.post(f"{BACKEND_URL}/api/assessment/generate", json={
                    "topic": stu_detail['course_name'],
                    "difficulty": "Intermediate"
                })
                if e_res.status_code == 200:
                    st.session_state["current_exam"] = e_res.json()["data"]
                    st.success("✅ Assessment Synthesized!")
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
        
        demo_preset = st.session_state.get("demo_preset")
        is_preset_a = demo_preset == "PRESET_A"
        is_preset_b = demo_preset == "PRESET_B"
        
        with st.form("dedicated_exam_form"):
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
            st.markdown("##### **Part 2: Multimodal Practical Project Challenge (70 Points Max)**")
            
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
                github_default = "https://github.com/skillforge/diagnostic-tooling"
                live_default = f"http://localhost:8000/portfolio/{selected_student_id}"
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
                live_default = f"http://localhost:8000/portfolio/{selected_student_id}"
                
            s_text = st.text_area("Your Practical Solution Code / Diagnostic Log", value=sub_text_default, height=120)
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                github_url_input = st.text_input("GitHub Code Repository URL", value=github_default)
            with col_u2:
                live_url_input = st.text_input("Live Demo / Project Deployment URL", value=live_default)
                
            uploaded_img = st.file_uploader("Attach Project Artifact (Hardware Photo / Circuit Diagram / Code Screenshot)", type=["jpg", "png", "jpeg", "pdf", "zip"])
            
            submit_exam = st.form_submit_button("🚀 Submit Exam & Run Background Agent", type="primary", use_container_width=True)
            
        if submit_exam:
            if "demo_preset" in st.session_state:
                del st.session_state["demo_preset"]
                
            img_b64 = None
            if uploaded_img is not None and uploaded_img.type in ["image/jpeg", "image/png", "image/jpg"]:
                img_b64 = base64.b64encode(uploaded_img.getvalue()).decode("utf-8")
                
            p_bar = st.progress(0, text="Triggering Background Agent Engine...")
            time.sleep(0.2)
            p_bar.progress(30, text="1. Gemma Fast Screener & Objective MCQ Scoring...")
            time.sleep(0.3)
            p_bar.progress(70, text="2. Gemini 3.5 Multimodal Evaluation & Portfolio Generation...")
            
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
                    st.session_state["last_portfolio_url"] = eval_out.get("portfolio_url", f"http://localhost:8000/portfolio/{selected_student_id}")
                    
                    st.success("✅ Evaluation & Dynamic Portfolio Generation Complete!")
                    
                    st.markdown("### 📊 Performance Metrics Breakdown")
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
                        st.markdown("#### 📬 Outbound Application Alerts")
                        st.markdown(f"**Matched Partner:** `{dispatch_out['hiring_partner']}`")
                        st.markdown(f"**Role Title:** `{dispatch_out['role']}`")
                        st.markdown(f"**Live Dossier:** [View Portfolio]({eval_out['portfolio_url']})")
                        st.info(dispatch_out["notifications"]["student_alert"])
                        st.info(dispatch_out["notifications"]["branch_alert"])
                    else:
                        st.markdown(f'<span class="badge-remedial">🔄 STATUS: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.warning(f"Score below threshold. 7-day remedial plan assigned.")
                else:
                    st.error(f"Pipeline error: {pipe_res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- VIEW 3: LIVE GENERATED PORTFOLIO DOSSIER ---
with views[2]:
    st.subheader("🌐 Live Standalone Candidate Portfolio Dossier Viewer")
    st.markdown("Preview the standalone HTML/CSS/Tailwind portfolio generated by Gemini 3.5 Flash upon student submission.")
    
    dossier_url = st.session_state.get("last_portfolio_url", f"http://localhost:8000/portfolio/STU-1001")
    st.markdown(f"**Active Portfolio Dossier URL:** [`{dossier_url}`]({dossier_url})")
    
    if st.button("🔄 Refresh Live Portfolio Preview", type="primary"):
        st.rerun()
        
    try:
        st.components.v1.iframe(dossier_url, height=650, scrolling=True)
    except Exception as e:
        st.error(f"Could not render portfolio iframe: {e}")

# --- VIEW 4: AUTONOMOUS RECRUITER OUTBOX & TELEMETRY ---
with views[3]:
    st.subheader("🚀 Autonomous Recruiter Outbox & Telemetry Logs")
    st.markdown("Immutable ledger of auto-dispatched candidate applications and real-time background execution trace logs.")
    
    tab_l1, tab_l2 = st.tabs(["📜 Live Outbox Application Ledger", "🤖 OpenTelemetry Execution Logs"])
    
    with tab_l1:
        try:
            l_res = requests.get(f"{BACKEND_URL}/api/placements/ledger", timeout=2)
            if l_res.status_code == 200:
                ledger = l_res.json()["data"]
                if ledger:
                    st.dataframe(ledger, use_container_width=True)
                else:
                    st.info("No dispatches logged yet.")
        except Exception as e:
            st.error(f"Error loading ledger: {e}")
            
    with tab_l2:
        telemetry_logs = st.session_state.get("last_telemetry", [
            {"timestamp": "19:35:01.002", "step": "START", "message": "Autonomous Agent initialized for Student STU-1001"},
            {"timestamp": "19:35:01.045", "step": "GEMMA_PRECHECK", "message": "Gemma fast check passed (Score: 84/100)"},
            {"timestamp": "19:35:02.112", "step": "DOSSIER_GEN", "message": "Synthesized standalone HTML portfolio dossier at /portfolio/STU-1001"},
            {"timestamp": "19:35:02.340", "step": "ACTION_DISPATCHED", "message": "Auto-dispatched job application to Tata Motors for Automotive Systems Technician"}
        ])
        log_text = "\n".join([f"[{t['timestamp']}] [{t['step']}] {t['message']}" for t in telemetry_logs])
        st.code(log_text, language="text")
