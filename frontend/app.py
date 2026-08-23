import streamlit as st
import requests
import json
import time
import base64

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Institutional Ops Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ SkillForge Autonomous</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Institutional Vocational Operations, Multimodal Evaluation & Recruiter Outbox Engine</div>', unsafe_allow_html=True)

# Sidebar System Health & Node Selector
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Status & Centers")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            st.success("🟢 Operations Engine Connected (Port 8000)")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.error("🔴 Backend Unreachable")
        
    st.divider()
    
    # Load Centers from Module 1
    centers = []
    try:
        c_res = requests.get(f"{BACKEND_URL}/api/centers", timeout=2)
        if c_res.status_code == 200:
            centers = c_res.json()["data"]
    except Exception:
        pass
        
    selected_center_name = "All Centers"
    if centers:
        st.markdown("### Active Training Nodes")
        c_names = [f"{c['name']} ({c['location']})" for c in centers]
        selected_center_name = st.selectbox("Select Active Center Node", c_names)
        
    st.divider()
    st.markdown("### Stack & AI Models")
    st.markdown("- **Google GenAI SDK**")
    st.markdown("- **Gemini 3.5 Multimodal Vision**")
    st.markdown("- **Gemma Fast Pre-Screener**")
    st.markdown("- **FastAPI & SQLite Roster**")

tabs = st.tabs([
    "🎯 Center & Batch Assessment Hub",
    "⚡ Multimodal Evaluation & Autonomous Pipeline",
    "🤝 Hiring Partner Outbox & Live Placement Ledger"
])

# --- TAB 1: CENTER & BATCH ASSESSMENT HUB ---
with tabs[0]:
    st.subheader("Multi-Center Batch Roster & Assessment Generator")
    st.markdown("Synthesize customized vocational exams tied directly to institutional centers, active course batches, and student rosters.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        topic_input = st.text_input("Vocational Topic / Skill Area", value="Automotive Diagnostic & CAN Bus Systems")
    with col_b:
        difficulty_input = st.selectbox("Exam Difficulty Level", ["Beginner", "Intermediate", "Advanced", "Master Technician"])
    with col_c:
        batch_code_input = st.text_input("Target Batch Code", value="BATCH-JWL-2026C")
        
    if st.button("✨ Synthesize & Schedule Assessment", type="primary", use_container_width=True):
        with st.spinner("Synthesizing Vocational Assessment via Gemini 3.5..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/assessment/generate",
                    json={
                        "topic": topic_input,
                        "difficulty": difficulty_input,
                        "batch_id": batch_code_input
                    },
                    timeout=30
                )
                if resp.status_code == 200:
                    result = resp.json()["data"]
                    st.success("✅ Assessment Synthesized & Assigned to Batch!")
                    
                    st.markdown(f"### 📋 {result.get('title', 'Assessment')}")
                    st.caption(f"Exam ID: `{result.get('exam_id')}` | Scheduled for Batch: `{batch_code_input}`")
                    
                    st.divider()
                    st.markdown("#### 1. Multiple-Choice Questions (MCQs)")
                    for idx, mcq in enumerate(result.get("mcqs", []), 1):
                        with st.expander(f"Question {idx}: {mcq['question']}", expanded=True):
                            for opt_idx, opt in enumerate(mcq['options']):
                                is_correct = (opt_idx == mcq['correct_option'])
                                prefix = "✅ " if is_correct else "⚪ "
                                st.write(f"{prefix} **Option {opt_idx+1}:** {opt}")
                                
                    st.divider()
                    st.markdown("#### 2. Practical Hands-On Task")
                    st.info(result.get("practical_task", "No task specified"))
                    
                    st.divider()
                    st.markdown("#### 3. Grading Rubric Parameters")
                    for rubric in result.get("grading_rubric", []):
                        st.markdown(f"- 🔹 {rubric}")
                        
                else:
                    st.error(f"Generation failed: {resp.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- TAB 2: MULTIMODAL EVALUATION & PIPELINE ---
with tabs[1]:
    st.subheader("Dual-AI Multimodal Vision Evaluation & Autonomous Dispatch")
    st.markdown("Runs Gemma pre-screening, Gemini 3.5 Multimodal Vision grading on text/image artifacts, and triggers autonomous recruiter outbox payloads.")
    
    st.markdown("**Quick-Fill Sample Scenarios:**")
    sample_col1, sample_col2 = st.columns(2)
    
    if "cand_name" not in st.session_state:
        st.session_state["cand_name"] = "Alex Mercer"
        st.session_state["target_role"] = "Automotive Systems Technician"
        st.session_state["task_desc"] = "Diagnose intermittent CAN bus signal degradation and perform safety isolation."
        st.session_state["rubric_text"] = "Safety lockout procedure followed\nAccurate voltage drop & oscilloscope measurement\nProper circuit repair documentation"
        st.session_state["sub_text"] = (
            "First, I performed a full safety lockout procedure and verified system power status using a multimeter. "
            "Next, connected an oscilloscope to CAN-H and CAN-L lines to measure voltage waveforms. "
            "Found ground signal degradation due to corrosion on terminal connector J-12. "
            "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean 2.5V differential."
        )
        
    with sample_col1:
        if st.button("🟢 Load High-Scoring Sample (Pass Case)", use_container_width=True):
            st.session_state["cand_name"] = "Alex Mercer"
            st.session_state["target_role"] = "Automotive Systems Technician"
            st.session_state["task_desc"] = "Diagnose intermittent CAN bus signal degradation and perform safety isolation."
            st.session_state["rubric_text"] = "Safety lockout procedure followed\nAccurate voltage drop & oscilloscope measurement\nProper circuit repair documentation"
            st.session_state["sub_text"] = (
                "First, I performed a full safety lockout procedure and verified system power status using a multimeter. "
                "Next, connected an oscilloscope to CAN-H and CAN-L lines to measure voltage waveforms. "
                "Found ground signal degradation due to corrosion on terminal connector J-12. "
                "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean 2.5V differential."
            )
            st.rerun()
            
    with sample_col2:
        if st.button("🟠 Load Low-Scoring Sample (Remedial Case)", use_container_width=True):
            st.session_state["cand_name"] = "Jordan Smith"
            st.session_state["target_role"] = "Full Stack Developer Trainee"
            st.session_state["task_desc"] = "Build a REST API authentication route with password hashing."
            st.session_state["rubric_text"] = "Input validation implemented\nSecure password hashing applied\nJWT token generated"
            st.session_state["sub_text"] = "Created basic route. Saved plain text passwords in dictionary. Could not get JWT working."
            st.rerun()
            
    st.divider()
    
    with st.form("eval_form"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            c_name = st.text_input("Candidate Name", value=st.session_state["cand_name"])
            c_role = st.text_input("Target Role", value=st.session_state["target_role"])
            uploaded_image = st.file_uploader("Upload Practical Artifact Image (Circuit / Hardware / Report)", type=["jpg", "png", "jpeg"])
        with f_col2:
            p_task = st.text_area("Practical Task", value=st.session_state["task_desc"], height=80)
            g_rubric_raw = st.text_area("Grading Rubric (1 per line)", value=st.session_state["rubric_text"], height=80)
            
        s_text = st.text_area("Student Submission Text / Diagnostic Log", value=st.session_state["sub_text"], height=120)
        
        submit_eval = st.form_submit_button("🚀 Run Autonomous Pipeline", type="primary", use_container_width=True)

    if submit_eval:
        rubric_list = [r.strip() for r in g_rubric_raw.split("\n") if r.strip()]
        
        # Convert image to base64 if provided
        img_b64 = None
        if uploaded_image is not None:
            bytes_data = uploaded_image.getvalue()
            img_b64 = base64.b64encode(bytes_data).decode("utf-8")
            
        progress_bar = st.progress(0, text="Initiating Dual-AI Pipeline...")
        time.sleep(0.3)
        progress_bar.progress(30, text="1. Running Gemma Fast Keyword/Syntax Pre-Screening...")
        time.sleep(0.4)
        progress_bar.progress(70, text="2. Running Gemini 3.5 Multimodal Cognitive Evaluation & Scoring...")
        
        try:
            resp = requests.post(
                f"{BACKEND_URL}/api/submission/evaluate-and-dispatch",
                json={
                    "candidate_name": c_name,
                    "target_role": c_role,
                    "practical_task": p_task,
                    "grading_rubric": rubric_list,
                    "submission_text": s_text,
                    "image_base64": img_b64
                },
                timeout=30
            )
            progress_bar.progress(100, text="Pipeline Execution Complete!")
            
            if resp.status_code == 200:
                res = resp.json()
                eval_data = res["evaluation"]
                dispatch_data = res["dispatch"]
                
                st.markdown("### 📊 Pipeline Results")
                
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Gemma Fast Score", f"{eval_data['fast_screening']['structure_score']}/100")
                with m_col2:
                    st.metric("Gemini Final Score", f"{eval_data['total_score']}/100")
                with m_col3:
                    ready = eval_data['placement_ready']
                    st.metric("Placement Ready", "YES ✅" if ready else "NO 🟠")
                    
                st.divider()
                
                action_tag = dispatch_data["action_tag"]
                payload = dispatch_data["payload"]
                
                if ready:
                    st.markdown(f'<span class="badge-success">🚀 {action_tag}</span>', unsafe_allow_html=True)
                    st.markdown("#### 📬 Recruiter Outbox Dispatch Payload (Employer Network Match)")
                    
                    st.markdown(f"**Matched Employer Partner:** `{payload.get('matched_partner', 'Partner Network')}`")
                    st.markdown(f"**Match Percentage:** `{payload.get('match_percentage', 90)}%`")
                    st.markdown(f"**Verified Metric Hash:** <span class=\"hash-text\">{payload['verified_metric_hash']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Recipient:** `{payload['outbox_action']['recipient']}`")
                    st.markdown(f"**Calendar Hook:** [{payload['outbox_action']['calendar_booking_url']}]({payload['outbox_action']['calendar_booking_url']})")
                    st.markdown(f"**Recruiter Pitch:** *\"{payload['scorecard']['recruiter_pitch']}\"*")
                    
                    with st.expander("View Full Raw Outbox Payload JSON"):
                        st.json(payload)
                else:
                    st.markdown(f'<span class="badge-remedial">🔄 {action_tag}</span>', unsafe_allow_html=True)
                    st.markdown("#### 📚 7-Day Personalized Remedial Study Schedule")
                    
                    st.markdown(f"**Verified Metric Hash:** <span class=\"hash-text\">{payload['verified_metric_hash']}</span>", unsafe_allow_html=True)
                    
                    rem_sched = eval_data.get("remedial_schedule", {})
                    for day_task in rem_sched.get("daily_schedule", []):
                        st.markdown(f"**Day {day_task['day']}**: `{day_task['focus_topic']}`")
                        st.caption(f"Task: {day_task['practice_exercise']} ({day_task['estimated_hours']} hr)")
                        
                    with st.expander("View Full Remedial Payload JSON"):
                        st.json(payload)
                        
            else:
                st.error(f"Pipeline error: {resp.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

# --- TAB 3: RECRUITER HUB & DISPATCH LEDGER ---
with tabs[2]:
    st.subheader("Active Hiring Partners & Live Dispatch Audit Ledger")
    st.markdown("Monitor real-time candidate dispatches to enterprise employer partners and view verified audit trails.")
    
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.markdown("#### 🏢 Registered Employer Partners")
        try:
            p_res = requests.get(f"{BACKEND_URL}/api/recruiter/partners", timeout=2)
            if p_res.status_code == 200:
                partners = p_res.json()["data"]
                for p in partners:
                    with st.expander(f"{p['company_name']} ({p['industry']})"):
                        st.write(f"**Contact Email:** `{p['contact_email']}`")
                        st.write(f"**Webhook Integration:** `{p['webhook_url']}`")
        except Exception as e:
            st.error(f"Could not load partners: {e}")
            
    with col_r:
        st.markdown("#### 💼 Open Role Requisitions")
        try:
            r_res = requests.get(f"{BACKEND_URL}/api/recruiter/requisitions", timeout=2)
            if r_res.status_code == 200:
                reqs = r_res.json()["data"]
                for r in reqs:
                    with st.expander(f"{r['role_title']} - {r['company_name']}"):
                        st.write(f"**Min Score Threshold:** `{r['min_score']}/100`")
                        st.write(f"**Required Skills:** {r['required_skills']}")
                        st.write(f"**Salary Offer Range:** `{r['min_salary']}`")
        except Exception as e:
            st.error(f"Could not load requisitions: {e}")
            
    st.divider()
    st.markdown("#### 📜 Live Dispatch Audit Ledger")
    try:
        ledger_res = requests.get(f"{BACKEND_URL}/api/recruiter/ledger", timeout=2)
        if ledger_res.status_code == 200:
            ledger_items = ledger_res.json()["data"]
            if ledger_items:
                st.dataframe(ledger_items, use_container_width=True)
            else:
                st.info("No dispatches logged yet. Run a candidate pipeline in Tab 2!")
    except Exception as e:
        st.error(f"Could not load ledger: {e}")
