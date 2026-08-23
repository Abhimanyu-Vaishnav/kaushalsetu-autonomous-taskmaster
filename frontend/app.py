import streamlit as st
import requests
import json
import time
import base64
import io

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Enterprise Platform",
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
st.markdown('<div class="sub-header">Enterprise Multi-Tenant Vocational Operations & Autonomous Placement Platform</div>', unsafe_allow_html=True)

# Sidebar System Status & Role Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Status")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            st.success("🟢 Platform Engine Live (v3.6.0)")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.error("🔴 Backend Unreachable")
        
    st.divider()
    st.markdown("### Operational Views")
    role_view = st.radio("Navigate View", [
        "🏛️ Institute & Branch Admin Hub",
        "🎓 Student Portal & Practical Assessment",
        "🚀 Autonomous Placement & Recruiter Ledger"
    ])
    
    st.divider()
    st.markdown("### Technology Stack")
    st.markdown("- **Google GenAI SDK (Gemini 3.5)**")
    st.markdown("- **Gemma Fast Pre-Screener**")
    st.markdown("- **SQLite WAL Thread-Safe Engine**")
    st.markdown("- **FastAPI & Streamlit**")

# --- TAB 1: INSTITUTE & BRANCH ADMIN HUB ---
if role_view == "🏛️ Institute & Branch Admin Hub":
    st.subheader("🏛️ Institute & Branch Governance Hub")
    st.markdown("Configure placement thresholds, manage branches/courses, and bulk enroll students.")
    
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
        
        # Policy Settings
        with st.expander("⚙️ Placement Threshold & Interview Policy Config", expanded=True):
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
                        st.success("✅ Placement Policy Updated Successfully!")
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
        st.markdown("#### 👥 Candidate Roster & Bulk Student Intake")
        
        tab_a1, tab_a2 = st.tabs(["📄 Single Candidate Add", "📁 Bulk CSV Roster Upload"])
        
        with tab_a1:
            with st.form("single_add_form"):
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
                        st.success(f"✅ Candidate Enrolled! Student ID: `{a_res.json()['data']['student_id']}`")
                        st.rerun()
                        
        with tab_a2:
            st.markdown("Upload a CSV file containing headers: `full_name`, `email`, `phone`, `branch_name`, `course_name`, `fees_status`")
            sample_csv_data = "full_name,email,phone,branch_name,course_name,fees_status\nVikram Rathore,vikram.r@skillforge-edu.org,+91 9811122233,Nangloi Center,Automotive & Hardware Diagnostics,PAID\nSneha Gupta,sneha.g@skillforge-edu.org,+91 9822233344,Yamuna Vihar Center,Full Stack Web Development,PAID"
            st.download_button("📥 Download Sample CSV Template", sample_csv_data, file_name="sample_students.csv", mime="text/csv")
            
            uploaded_csv = st.file_uploader("Upload CSV Roster File", type=["csv"])
            if uploaded_csv is not None:
                if st.button("🚀 Process & Enroll Bulk Roster", type="primary"):
                    files = {"file": (uploaded_csv.name, uploaded_csv.getvalue(), "text/csv")}
                    b_res = requests.post(f"{BACKEND_URL}/api/students/bulk-upload?institute_id={inst_data['id']}", files=files)
                    if b_res.status_code == 200:
                        count = b_res.json()["count"]
                        st.success(f"✅ Successfully processed and enrolled {count} candidates into database!")
                        st.rerun()
                        
        st.divider()
        st.markdown("#### 📜 Live Institute Student Roster")
        try:
            st_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
            if st_res.status_code == 200:
                students = st_res.json()["data"]
                st.dataframe(students, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load student roster: {e}")

# --- TAB 2: STUDENT PORTAL & INTERACTIVE PRACTICAL ASSESSMENT ---
elif role_view == "🎓 Student Portal & Practical Assessment":
    st.subheader("🎓 Interactive Student Exam & Real-Time Dynamic Grading Portal")
    st.markdown("Take interactive 5-MCQ exams with unselected radios, submit your practical code/logs, and test dynamic scoring.")
    
    # Load Students
    students = []
    try:
        s_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
        if s_res.status_code == 200:
            students = s_res.json()["data"]
    except Exception:
        pass
        
    if not students:
        st.warning("No students found. Please enroll candidates in the Admin Hub.")
    else:
        stu_opts = {f"{s['full_name']} ({s['student_id']}) - {s['course_name']}": s['student_id'] for s in students}
        sel_label = st.selectbox("🔑 Select Student Account Login", list(stu_opts.keys()))
        selected_student_id = stu_opts[sel_label]
        
        stu_detail = next(s for s in students if s['student_id'] == selected_student_id)
        
        # Student Profile Card & Consent Toggle
        st.markdown("#### 👤 Student Profile & Placement Consent Gate")
        col_sp1, col_sp2, col_sp3 = st.columns(3)
        with col_sp1:
            st.write(f"**Name:** {stu_detail['full_name']}")
            st.write(f"**Email:** `{stu_detail['email']}`")
        with col_sp2:
            st.write(f"**Branch:** `{stu_detail['branch_name']}`")
            st.write(f"**Course:** {stu_detail['course_name']}")
        with col_sp3:
            cur_consent = bool(stu_detail.get('consent_for_job_dispatch', 1))
            st.write(f"**Interview Count:** `{stu_detail.get('interview_count', 0)} / 3`")
            new_consent = st.checkbox("Authorize AI Agent to Auto-Dispatch Job Applications", value=cur_consent)
            if new_consent != cur_consent:
                requests.post(f"{BACKEND_URL}/api/students/consent", json={"student_id": selected_student_id, "consent": new_consent})
                st.success("✅ Consent status updated!")
                st.rerun()
                
        st.divider()
        
        # Quick Presets for Demo Testing
        st.markdown("#### ⚡ Quick Demo Test Presets")
        preset_col1, preset_col2 = st.columns(2)
        with preset_col1:
            if st.button("🟢 Load High-Scoring Pass Preset (100% MCQs + Full Practical)", use_container_width=True):
                st.session_state["preset_type"] = "HIGH"
                st.rerun()
        with preset_col2:
            if st.button("🟠 Load Low-Scoring Remedial Preset (20% MCQs + Minimal Practical)", use_container_width=True):
                st.session_state["preset_type"] = "LOW"
                st.rerun()
                
        st.divider()
        st.markdown("### 📝 Interactive Exam & Real-Time Grading Test")
        
        # Exam Generation Button
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
                    
        # Load or Fallback Exam
        if "current_exam" not in st.session_state:
            # Generate initial default assessment
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
        
        # Interactive Student Test Form
        with st.form("interactive_exam_form"):
            st.markdown(f"#### 📋 **{exam.get('title', 'Vocational Exam')}**")
            st.markdown("##### **Part 1: Multiple Choice Questions (30 Points Max)**")
            
            user_mcq_answers = []
            is_high_preset = st.session_state.get("preset_type") == "HIGH"
            is_low_preset = st.session_state.get("preset_type") == "LOW"
            
            for idx, mcq in enumerate(mcqs, 1):
                st.markdown(f"**Question {idx}: {mcq['question']}**")
                opts = mcq['options']
                
                # Determine default index
                default_idx = None
                if is_high_preset:
                    default_idx = mcq['correct_option']
                elif is_low_preset:
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
            
            p_task_default = exam.get("practical_task", f"Complete diagnostic inspection and log for {stu_detail['course_name']}.")
            st.info(f"**Task Description:** {p_task_default}")
            
            rubric_default = exam.get("grading_rubric", ["Safety lockout procedure followed", "Diagnostic accuracy verified", "Documentation complete"])
            st.caption("Grading Rubric Parameters: " + " | ".join(rubric_default))
            
            if is_high_preset:
                sub_text_default = (
                    "First, performed a full safety lockout procedure and verified system power status using a multimeter. "
                    "Next, connected an oscilloscope to signal lines to measure voltage waveforms. "
                    "Found ground signal degradation due to terminal connector corrosion. "
                    "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean differential voltage."
                )
            elif is_low_preset:
                sub_text_default = "Looked at the wires. Turned on the switch. It worked eventually."
            else:
                sub_text_default = (
                    "Performed safety lockout procedure. Verified circuit connections using calibrated multimeter. "
                    "Recorded voltage measurements across load terminals. Documented fault codes and completed repair."
                )
                
            s_text = st.text_area("Your Practical Solution Code / Diagnostic Log", value=sub_text_default, height=130)
            uploaded_img = st.file_uploader("Attach Practical Artifact Image (Hardware Photo / Circuit Diagram / Code Screenshot)", type=["jpg", "png", "jpeg"])
            
            submit_exam = st.form_submit_button("🚀 Submit My Exam for Dynamic Real-Time Grading", type="primary", use_container_width=True)
            
        if submit_exam:
            # Clear preset flag after submission
            if "preset_type" in st.session_state:
                del st.session_state["preset_type"]
                
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
                    
                    st.markdown("### 📊 Real-Time Scorecard Breakdown")
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("MCQ Score", f"{eval_out['mcq_score']} / 30 pts", f"{eval_out['mcq_correct_count']}/{eval_out['mcq_total_questions']} Correct")
                    with mc2:
                        st.metric("Practical Score", f"{eval_out['practical_score']} / 70 pts")
                    with mc3:
                        st.metric("Final Combined Score", f"{eval_out['total_score']} / 100 pts")
                    with mc4:
                        ready = eval_out['placement_ready']
                        st.metric("Verification Gate", "PASSED 🚀" if ready else "REMEDIAL 🟠")
                        
                    st.divider()
                    
                    if ready:
                        st.markdown(f'<span class="badge-success">🚀 ACTION: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.markdown("#### 📬 Outbound Application & Notification Alerts")
                        st.markdown(f"**Matched Employer:** `{dispatch_out['hiring_partner']}`")
                        st.markdown(f"**Role Title:** `{dispatch_out['role']}`")
                        st.markdown(f"**Verified Hash:** <span class=\"hash-text\">{dispatch_out['verified_metric_hash']}</span>", unsafe_allow_html=True)
                        st.info(dispatch_out["notifications"]["student_alert"])
                        st.info(dispatch_out["notifications"]["branch_alert"])
                    else:
                        st.markdown(f'<span class="badge-remedial">🔄 ACTION: {dispatch_out["status"]}</span>', unsafe_allow_html=True)
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

# --- TAB 3: AUTONOMOUS PLACEMENT & RECRUITER LEDGER ---
elif role_view == "🚀 Autonomous Placement & Recruiter Ledger":
    st.subheader("🚀 Autonomous Placement & Dispatch Audit Ledger")
    st.markdown("Immutable audit ledger tracking auto-dispatched job applications, candidate verification hashes, and interview alerts.")
    
    try:
        l_res = requests.get(f"{BACKEND_URL}/api/placements/ledger", timeout=2)
        if l_res.status_code == 200:
            ledger = l_res.json()["data"]
            if ledger:
                st.dataframe(ledger, use_container_width=True)
            else:
                st.info("No job dispatches logged yet. Complete an exam submission in the Student Portal tab!")
    except Exception as e:
        st.error(f"Could not load placement ledger: {e}")
