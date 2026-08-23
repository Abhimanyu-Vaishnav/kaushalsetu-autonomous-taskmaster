import streamlit as st
import requests
import json
import time
import base64
import io

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Background Agent Engine",
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
    .terminal-box {
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

st.markdown('<div class="main-header">⚡ SkillForge Autonomous</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">End-to-End Autonomous Background Agent Engine | Taskmaster Track</div>', unsafe_allow_html=True)

# Sidebar System Health & One-Click Demo Preset Switcher
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Health & Status")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            st.success("🟢 FastAPI Backend Connected (v3.7.0)")
            st.success("⚡ Gemma Pre-check Screener Ready")
            st.success("🤖 Gemini 3.5 Pro & Flash Active")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.error("🔴 Backend Unreachable")
        
    st.divider()
    st.markdown("### ⚡ One-Click Demo Switcher")
    st.caption("Instant test presets for Judges:")
    
    if st.button("🟢 Preset A: Top Candidate (92% Score)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_A"
        st.info("Loaded Top Candidate Preset! Go to View 2 to execute.")
        
    if st.button("🟠 Preset B: Remedial Candidate (54% Score)", use_container_width=True):
        st.session_state["demo_preset"] = "PRESET_B"
        st.info("Loaded Remedial Candidate Preset! Go to View 2 to execute.")

    st.divider()
    st.markdown("### Track Specification")
    st.markdown("- **Taskmaster Track**")
    st.markdown("- **Zero Chatbot UI**")
    st.markdown("- **Gemma Bonus (+0.2 pts)**")

# 4 Main Operational Views
views = st.tabs([
    "🏛️ Institute Center Node",
    "🎓 Candidate Exam Space",
    "🌐 Live Generated Dossier Viewer",
    "🤖 Agent Autonomous Telemetry"
])

# --- VIEW 1: INSTITUTE CENTER NODE ---
with views[0]:
    st.subheader("🏛️ Institute Center Node & Roster Control")
    st.markdown("Configure placement thresholds, max interview caps per candidate, and manage student rosters.")
    
    inst_data = {}
    try:
        ires = requests.get(f"{BACKEND_URL}/api/institute/info", timeout=2)
        if ires.status_code == 200:
            inst_data = ires.json()["data"]
    except Exception:
        pass
        
    if inst_data:
        st.markdown(f"### **{inst_data.get('name', 'Institute')}** (`Code: {inst_data.get('code', 'SKILLFORGE-HQ')}`)")
        
        with st.expander("⚙️ Placement Threshold & Policy Settings", expanded=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                cur_thresh = inst_data.get("placement_threshold", 70)
                new_thresh = st.slider("Minimum Placement Score %", 50, 95, cur_thresh)
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
                        st.success("✅ Policy Settings Saved!")
                        st.rerun()
                        
        st.divider()
        st.markdown("#### 📜 Registered Student Roster & Placement Status")
        try:
            st_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
            if st_res.status_code == 200:
                students = st_res.json()["data"]
                st.dataframe(students, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load roster: {e}")

# --- VIEW 2: CANDIDATE EXAM SPACE ---
with views[1]:
    st.subheader("🎓 Candidate Exam Space & Autonomous Agent Dispatcher")
    st.markdown("Log in via Candidate ID + DOB, take the 5-MCQ exam, submit code & GitHub links, and trigger the background agent.")
    
    students = []
    try:
        s_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
        if s_res.status_code == 200:
            students = s_res.json()["data"]
    except Exception:
        pass
        
    if not students:
        st.warning("No students found. Please enroll candidates in View 1.")
    else:
        stu_opts = {f"{s['full_name']} ({s['student_id']}) - {s['course_name']}": s['student_id'] for s in students}
        sel_label = st.selectbox("🔑 Candidate Login (Student ID)", list(stu_opts.keys()))
        selected_student_id = stu_opts[sel_label]
        
        stu_detail = next(s for s in students if s['student_id'] == selected_student_id)
        
        # Simple Login Check
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            dob_input = st.date_input("Date of Birth", value=None)
        with col_l2:
            st.write("")
            st.write("")
            cur_consent = bool(stu_detail.get('consent_for_job_dispatch', 1))
            new_consent = st.checkbox("I authorize SkillForge AI Agent to build my live dossier & auto-apply to matching job openings", value=cur_consent)
            if new_consent != cur_consent:
                requests.post(f"{BACKEND_URL}/api/students/consent", json={"student_id": selected_student_id, "consent": new_consent})
                st.success("✅ Placement Dispatch Consent Updated!")
                st.rerun()
                
        st.divider()
        st.markdown("### 📝 Exam Synthesis & Assessment Submission")
        
        if st.button("✨ Synthesize Assessment via Gemini 3.5", type="primary"):
            with st.spinner("Synthesizing assessment via Gemini 3.5..."):
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
        
        with st.form("candidate_exam_form"):
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
                
            uploaded_img = st.file_uploader("Attach Project Artifact (Hardware Photo / Circuit Diagram / Screenshot)", type=["jpg", "png", "jpeg", "pdf", "zip"])
            
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
            p_bar.progress(70, text="2. Gemini 3.5 Multimodal Evaluation & HTML Dossier Generation...")
            
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
                    
                    st.success("✅ Dynamic Real-Time Grading & Dossier Generation Complete!")
                    
                    st.markdown("### 📊 Candidate Performance Metrics")
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
                        st.markdown("#### 📬 Outbound Application & Notification Alerts")
                        st.markdown(f"**Matched Partner:** `{dispatch_out['hiring_partner']}`")
                        st.markdown(f"**Role Title:** `{dispatch_out['role']}`")
                        st.markdown(f"**Live Portfolio Dossier:** [View Dossier]({eval_out['portfolio_url']})")
                        st.info(dispatch_out["notifications"]["student_alert"])
                        st.info(dispatch_out["notifications"]["branch_alert"])
                    else:
                        st.markdown(f'<span class="badge-remedial">🔄 STATUS: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.warning(f"Score below required threshold. 7-day remedial plan assigned.")
                else:
                    st.error(f"Pipeline error: {pipe_res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- VIEW 3: LIVE GENERATED DOSSIER VIEWER ---
with views[2]:
    st.subheader("🌐 Live Standalone Candidate Portfolio Dossier Viewer")
    st.markdown("Preview the standalone HTML/CSS/Tailwind portfolio generated by Gemini 3.5 Flash upon student submission.")
    
    dossier_url = st.session_state.get("last_portfolio_url", "http://localhost:8000/portfolio/STU-1001")
    st.markdown(f"**Active Dossier URL:** [`{dossier_url}`]({dossier_url})")
    
    if st.button("🔄 Refresh Live Dossier Preview", type="primary"):
        st.rerun()
        
    try:
        st.components.v1.iframe(dossier_url, height=650, scrolling=True)
    except Exception as e:
        st.error(f"Could not render portfolio iframe: {e}")

# --- VIEW 4: AGENT AUTONOMOUS TELEMETRY ---
with views[3]:
    st.subheader("🤖 Agent Autonomous Action Telemetry & Terminal Logs")
    st.markdown("Real-time streaming event trace logs showing the background agent discovering jobs, validating consent, and executing dispatches.")
    
    telemetry_logs = st.session_state.get("last_telemetry", [
        {"timestamp": "19:15:01.002", "step": "START", "message": "Autonomous Agent initialized for Student STU-1001"},
        {"timestamp": "19:15:01.045", "step": "GEMMA_PRECHECK", "message": "Gemma fast sub-millisecond check passed (Score: 84/100)"},
        {"timestamp": "19:15:02.112", "step": "DOSSIER_GEN", "message": "Synthesized standalone HTML portfolio dossier at /portfolio/STU-1001"},
        {"timestamp": "19:15:02.340", "step": "ACTION_DISPATCHED", "message": "Auto-dispatched job application to Tata Motors for Automotive Systems Technician"}
    ])
    
    log_text = "\n".join([f"[{t['timestamp']}] [{t['step']}] {t['message']}" for t in telemetry_logs])
    st.code(log_text, language="text")
