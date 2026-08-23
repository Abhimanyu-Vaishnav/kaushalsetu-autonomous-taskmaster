import streamlit as st
import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Operations Dashboard",
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
    .card {
        background-color: #F9FAFB;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E5E7EB;
        margin-bottom: 15px;
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
""", unsafe_allow_cookies=True, unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ SkillForge Autonomous</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Continuous Action Engine for Vocational Training Institutes | Powered by Gemini 3.5 & Gemma</div>', unsafe_allow_html=True)

# Sidebar System Health & Info
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=50)
    st.subheader("System Status")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            st.success("🟢 Backend Connected (Port 8000)")
            data = res.json()
            st.caption(f"Service: {data.get('service', 'SkillForge Engine')}")
            st.caption(f"Engine Step: {data.get('step', '2')}")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.error("🔴 Backend Unreachable")
        st.info("Ensure `python backend/main.py` is running on port 8000.")
        
    st.divider()
    st.markdown("### Hackathon Stack")
    st.markdown("- **Google GenAI SDK**")
    st.markdown("- **Gemini 3.5 Pro & Flash**")
    st.markdown("- **Gemma Fast Pre-Screener**")
    st.markdown("- **FastAPI & Pydantic**")

tabs = st.tabs(["🎯 Curriculum & Assessment Synthesizer", "⚡ Candidate Evaluation & Recruiter Outbox"])

# --- TAB 1: CURRICULUM SYNTHESIZER ---
with tabs[0]:
    st.subheader("Automated Assessment Generation Engine")
    st.markdown("Synthesize structured vocational training assessments with MCQs, practical hands-on tasks, and rubric parameters.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic_input = st.text_input("Vocational Topic / Skill Area", value="CNC Machine Operations & Precision Diagnostics")
    with col2:
        difficulty_input = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced", "Master Technician"])
        
    if st.button("✨ Synthesize Assessment", type="primary", use_container_width=True):
        with st.spinner("Synthesizing Assessment via Gemini 3.5..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/assessment/generate",
                    json={"topic": topic_input, "difficulty": difficulty_input},
                    timeout=30
                )
                if resp.status_code == 200:
                    result = resp.json()["data"]
                    st.success("✅ Assessment Synthesized Successfully!")
                    
                    st.markdown(f"### 📋 {result.get('title', 'Assessment')}")
                    st.caption(f"Exam ID: `{result.get('exam_id')}`")
                    
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

# --- TAB 2: CANDIDATE EVALUATION & RECRUITER OUTBOX ---
with tabs[1]:
    st.subheader("Dual-AI Submission Evaluation & Autonomous Recruiter Dispatch")
    st.markdown("Runs fast Gemma pre-screening, Gemini deep cognitive evaluation, and triggers autonomous recruiter outbox or remedial retraining actions.")
    
    # Preset sample selector
    st.markdown("**Quick-Fill Sample Submissions:**")
    sample_col1, sample_col2 = st.columns(2)
    
    default_name = "Alex Mercer"
    default_role = "Senior Automotive Diagnostic Technician"
    default_task = "Diagnose intermittent CAN bus signal degradation and perform safety isolation."
    default_rubric = ["Safety lockout procedure followed", "Accurate voltage drop & oscilloscope measurement", "Proper circuit repair documentation"]
    default_submission = (
        "First, I performed a full safety lockout procedure and verified system power status using a multimeter. "
        "Next, connected an oscilloscope to CAN-H and CAN-L lines to measure voltage waveforms. "
        "Found ground signal degradation due to corrosion on terminal connector J-12. "
        "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean 2.5V differential."
    )
    
    if "cand_name" not in st.session_state:
        st.session_state["cand_name"] = default_name
        st.session_state["target_role"] = default_role
        st.session_state["task_desc"] = default_task
        st.session_state["rubric_text"] = "\n".join(default_rubric)
        st.session_state["sub_text"] = default_submission
        
    with sample_col1:
        if st.button("🟢 Load High-Scoring Sample (Pass Case)", use_container_width=True):
            st.session_state["cand_name"] = "Alex Mercer"
            st.session_state["target_role"] = "Senior Automotive Diagnostic Technician"
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
            st.session_state["target_role"] = "Junior Electronics Technician"
            st.session_state["task_desc"] = "Diagnose circuit failure on motor control board."
            st.session_state["rubric_text"] = "Safety lockout procedure followed\nFault isolation accuracy\nRepair documentation"
            st.session_state["sub_text"] = "Looked at the motor board. The fuse looked fine. Wiggled wires until it started working again."
            st.rerun()
            
    st.divider()
    
    with st.form("eval_form"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            c_name = st.text_input("Candidate Name", value=st.session_state["cand_name"])
            c_role = st.text_input("Target Role", value=st.session_state["target_role"])
        with f_col2:
            p_task = st.text_area("Practical Task", value=st.session_state["task_desc"], height=80)
            g_rubric_raw = st.text_area("Grading Rubric (1 per line)", value=st.session_state["rubric_text"], height=80)
            
        s_text = st.text_area("Student Practical Submission Text", value=st.session_state["sub_text"], height=120)
        
        submit_eval = st.form_submit_button("🚀 Run Autonomous Pipeline", type="primary", use_container_width=True)

    if submit_eval:
        rubric_list = [r.strip() for r in g_rubric_raw.split("\n") if r.strip()]
        
        progress_bar = st.progress(0, text="Initiating Dual-AI Pipeline...")
        
        # Step 1 Progress: Gemma Pre-Check
        time.sleep(0.3)
        progress_bar.progress(30, text="1. Running Gemma Fast Keyword/Syntax Pre-Screening...")
        
        # Step 2 Progress: Gemini Deep Evaluation
        time.sleep(0.4)
        progress_bar.progress(70, text="2. Running Gemini 3.5 Cognitive Evaluation & Scoring...")
        
        try:
            resp = requests.post(
                f"{BACKEND_URL}/api/submission/evaluate-and-dispatch",
                json={
                    "candidate_name": c_name,
                    "target_role": c_role,
                    "practical_task": p_task,
                    "grading_rubric": rubric_list,
                    "submission_text": s_text
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
                
                # Step 3: Autonomous Action State Output
                action_tag = dispatch_data["action_tag"]
                payload = dispatch_data["payload"]
                
                if ready:
                    st.markdown(f'<span class="badge-success">🚀 {action_tag}</span>', unsafe_allow_html=True)
                    st.markdown("#### 📬 Outbox Dispatch Payload (Hiring Network Webhook / Email)")
                    
                    st.markdown(f"**Verified Metric Hash:** <span class=\"hash-text\">{payload['verified_metric_hash']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Recipient:** `{payload['outbox_action']['recipient']}`")
                    st.markdown(f"**Subject:** `{payload['outbox_action']['subject']}`")
                    st.markdown(f"**Interview Requested:** `{payload['outbox_action']['interview_invite_requested']}`")
                    st.markdown(f"**Recruiter Pitch:** *\"{payload['scorecard']['recruiter_pitch']}\"*")
                    
                    with st.expander("View Full Raw Outbox Payload JSON"):
                        st.json(payload)
                else:
                    st.markdown(f'<span class="badge-remedial">🔄 {action_tag}</span>', unsafe_allow_html=True)
                    st.markdown("#### 📚 Remedial Retraining Pipeline Payload")
                    
                    st.markdown(f"**Verified Metric Hash:** <span class=\"hash-text\">{payload['verified_metric_hash']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Assigned Module:** `{payload['remedial_action']['assigned_module']}`")
                    st.markdown(f"**Retest Scheduled:** In `{payload['remedial_action']['retest_scheduled_days']} days`")
                    st.markdown("**Identified Skill Gaps:**")
                    for gap in eval_data.get("skill_gaps", []):
                        st.markdown(f"- 🔸 {gap}")
                        
                    with st.expander("View Full Remedial Payload JSON"):
                        st.json(payload)
                        
            else:
                st.error(f"Pipeline error: {resp.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
