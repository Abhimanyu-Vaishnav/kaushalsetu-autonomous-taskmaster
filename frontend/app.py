import streamlit as st
import requests
import json
import time
import base64

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SkillForge Autonomous - Multi-Tenant Platform",
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
st.markdown('<div class="sub-header">Multi-Tenant Institutional Operations & Autonomous Placement Platform</div>', unsafe_allow_html=True)

# Sidebar System Health & Role Switcher
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=45)
    st.subheader("System Status")
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if res.status_code == 200:
            st.success("🟢 Platform Engine Live (v3.0.0)")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.error("🔴 Backend Unreachable")
        
    st.divider()
    st.markdown("### Active Role Selector")
    role_view = st.radio("Switch Dashboard View", ["🏢 Institute Admin Dashboard", "🎓 Student Exam & Evaluation Portal", "🤝 Autonomous Placement & Interview Ledger"])
    
    st.divider()
    st.markdown("### Stack & AI Models")
    st.markdown("- **Google GenAI SDK**")
    st.markdown("- **Gemini 3.5 Multimodal Vision**")
    st.markdown("- **Gemma Fast Pre-Screener**")
    st.markdown("- **SQLite Multi-Tenant DB**")

# --- ROLE 1: INSTITUTE ADMIN DASHBOARD ---
if role_view == "🏢 Institute Admin Dashboard":
    st.subheader("🏢 Institute Administration & Branch Governance")
    st.markdown("Configure placement thresholds, manage branches, and enroll student rosters.")
    
    # Fetch Institute Info
    inst_data = {}
    try:
        ires = requests.get(f"{BACKEND_URL}/api/institute/info", timeout=2)
        if ires.status_code == 200:
            inst_data = ires.json()["data"]
    except Exception:
        pass
        
    if inst_data:
        st.markdown(f"### **{inst_data.get('name', 'Institute')}**")
        
        # Configuration Settings Form
        with st.expander("⚙️ Institute Placement & Dispatch Policy Config", expanded=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                cur_thresh = inst_data.get("dispatch_threshold", 70)
                new_thresh = st.slider("Placement Dispatch Threshold (Score %)", 50, 95, cur_thresh)
            with col_c2:
                cur_cap = inst_data.get("interview_cap_limit", 3)
                new_cap = st.slider("Max Interview Cap per Student", 1, 5, cur_cap)
            with col_c3:
                st.write("")
                st.write("")
                if st.button("💾 Save Institute Policy Config", type="primary", use_container_width=True):
                    up_res = requests.post(f"{BACKEND_URL}/api/institute/config", json={
                        "institute_id": inst_data["id"],
                        "dispatch_threshold": new_thresh,
                        "interview_cap_limit": new_cap
                    })
                    if up_res.status_code == 200:
                        st.success("✅ Placement Policy Updated!")
                        st.rerun()
                        
        st.divider()
        
        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            st.markdown("#### 🏛️ Registered Branches")
            for b in inst_data.get("branches", []):
                st.info(f"**{b['name']}** (`{b['branch_id']}`) - Location: {b['city']}")
                
        with col_b2:
            st.markdown("#### 📚 Active Vocational Courses")
            for c in inst_data.get("courses_offered", []):
                st.write(f"- 🔹 **{c}**")
                
        st.divider()
        st.markdown("#### 👤 Student Roster & Enrollment")
        
        # Add New Student Form
        with st.expander("➕ Enroll New Candidate into Roster", expanded=False):
            with st.form("add_student_form"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    s_name = st.text_input("Full Name", value="Rohan Mehta")
                    s_email = st.text_input("Email Address", value="rohan.m@skillforge-edu.org")
                with sc2:
                    branch_opts = {b['name']: b['branch_id'] for b in inst_data.get("branches", [])}
                    s_branch_name = st.selectbox("Assign Branch", list(branch_opts.keys()))
                    s_course = st.selectbox("Assign Course", inst_data.get("courses_offered", []))
                    
                s_submit = st.form_submit_button("Enroll Candidate", type="primary")
                if s_submit:
                    b_id = branch_opts[s_branch_name]
                    a_res = requests.post(f"{BACKEND_URL}/api/students/add", json={
                        "full_name": s_name,
                        "email": s_email,
                        "branch_id": b_id,
                        "course_name": s_course,
                        "fees_status": "PAID",
                        "consent_given": 1
                    })
                    if a_res.status_code == 200:
                        st.success(f"✅ Candidate Enrolled! ID: `{a_res.json()['data']['student_id']}`")
                        st.rerun()
                        
        # Display Roster Table
        try:
            st_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
            if st_res.status_code == 200:
                students = st_res.json()["data"]
                st.dataframe(students, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load roster: {e}")

# --- ROLE 2: STUDENT PORTAL ---
elif role_view == "🎓 Student Exam & Evaluation Portal":
    st.subheader("🎓 Student Practical Assessment & Dual-AI Evaluation Portal")
    st.markdown("Submit your practical project diagnostic logs or hardware image artifacts for instant Gemma & Gemini 3.5 vision grading.")
    
    # Load Students
    students = []
    try:
        s_res = requests.get(f"{BACKEND_URL}/api/students", timeout=2)
        if s_res.status_code == 200:
            students = s_res.json()["data"]
    except Exception:
        pass
        
    if not students:
        st.warning("No enrolled students found. Please enroll candidates in the Admin Dashboard.")
    else:
        student_opts = {f"{s['full_name']} ({s['student_id']}) - {s['course_name']}": s['student_id'] for s in students}
        sel_student_label = st.selectbox("🔑 Select Student Login", list(student_opts.keys()))
        selected_student_id = student_opts[sel_student_label]
        
        # Get selected student detail
        stu_detail = next(s for s in students if s['student_id'] == selected_student_id)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.write(f"**Candidate:** {stu_detail['full_name']}")
            st.write(f"**Email:** `{stu_detail['email']}`")
        with col_s2:
            st.write(f"**Branch ID:** `{stu_detail['branch_id']}`")
            st.write(f"**Course:** {stu_detail['course_name']}")
        with col_s3:
            st.write(f"**Placement Consent:** {'Given ✅' if stu_detail['consent_given'] else 'No ❌'}")
            st.write(f"**Interview Count:** `{stu_detail['interview_count']} / 3`")
            
        st.divider()
        
        st.markdown("### 📝 Practical Exam Submission & Live Pipeline Execution")
        
        default_task = f"Complete diagnostic inspection and verification procedure for {stu_detail['course_name']}."
        default_rubric = ["Safety lockout procedure followed", "Diagnostic accuracy & measurement verified", "Documentation complete"]
        default_sub = (
            "First, I performed a full safety lockout procedure and verified system power status using a multimeter. "
            "Next, connected an oscilloscope to signal lines to measure voltage waveforms. "
            "Found signal degradation due to terminal connector corrosion. "
            "Cleaned terminal connector, replaced wiring splice adhering to standard procedure, and re-tested signal verification with clean differential."
        )
        
        with st.form("student_submission_form"):
            p_task = st.text_area("Practical Task Description", value=default_task, height=70)
            g_rubric_raw = st.text_area("Grading Rubric (1 per line)", value="\n".join(default_rubric), height=70)
            s_text = st.text_area("Your Practical Solution / Diagnostic Log", value=default_sub, height=110)
            uploaded_img = st.file_uploader("Attach Practical Artifact (Hardware Photo / Diagram / Output Screenshot)", type=["jpg", "png", "jpeg"])
            
            sub_btn = st.form_submit_button("🚀 Submit Exam & Trigger Placement Pipeline", type="primary", use_container_width=True)
            
        if sub_btn:
            img_b64 = None
            if uploaded_img is not None:
                img_b64 = base64.b64encode(uploaded_img.getvalue()).decode("utf-8")
                
            rubric_list = [r.strip() for r in g_rubric_raw.split("\n") if r.strip()]
            
            p_bar = st.progress(0, text="Submitting Practical Exam...")
            time.sleep(0.3)
            p_bar.progress(35, text="1. Running Gemma Fast Keyword/Syntax Pre-Screening...")
            time.sleep(0.4)
            p_bar.progress(70, text="2. Running Gemini 3.5 Multimodal Cognitive Vision Evaluation...")
            
            try:
                pipeline_res = requests.post(
                    f"{BACKEND_URL}/api/student/evaluate-and-dispatch",
                    json={
                        "student_id": selected_student_id,
                        "practical_task": p_task,
                        "grading_rubric": rubric_list,
                        "submission_text": s_text,
                        "image_base64": img_b64
                    },
                    timeout=30
                )
                p_bar.progress(100, text="Evaluation Complete!")
                
                if pipeline_res.status_code == 200:
                    data = pipeline_res.json()["data"]
                    eval_out = data["evaluation"]
                    dispatch_out = data["dispatch"]
                    
                    st.success("✅ Evaluation & Placement Pipeline Executed!")
                    
                    st.markdown("### 📊 Dual-AI Evaluation Report")
                    mc1, mc2, mc3 = st.columns(3)
                    with mc1:
                        st.metric("Gemma Fast Score", f"{eval_out['fast_screening']['structure_score']}/100")
                    with mc2:
                        st.metric("Gemini Final Score", f"{eval_out['total_score']}/100")
                    with mc3:
                        ready = eval_out['placement_ready']
                        st.metric("Placement Ready", "YES ✅" if ready else "REMEDIAL 🟠")
                        
                    st.divider()
                    
                    if ready:
                        st.markdown(f'<span class="badge-success">🚀 {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.markdown("#### 📬 Outbox Dispatch & Interview Scheduling Alerts")
                        st.markdown(f"**Matched Employer:** `{dispatch_out['hiring_partner']}`")
                        st.markdown(f"**Matched Role:** `{dispatch_out['role']}`")
                        st.markdown(f"**Verified Metric Hash:** <span class=\"hash-text\">{dispatch_out['verified_metric_hash']}</span>", unsafe_allow_html=True)
                        st.info(dispatch_out["alerts"]["student_notification"])
                        st.info(dispatch_out["alerts"]["branch_notification"])
                    else:
                        st.markdown(f'<span class="badge-remedial">🔄 {dispatch_out["status"]}</span>', unsafe_allow_html=True)
                        st.markdown("#### 📚 Personalized 7-Day Remedial Micro-Study Plan")
                        st.warning(f"Reason: {dispatch_out.get('reason')}")
                        
                        rem_sched = eval_out.get("remedial_schedule", {})
                        for day_task in rem_sched.get("daily_schedule", []):
                            st.markdown(f"**Day {day_task['day']}**: `{day_task['focus_topic']}`")
                            st.caption(f"Task: {day_task['practice_exercise']} ({day_task['estimated_hours']} hr)")
                else:
                    st.error(f"Pipeline error: {pipeline_res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- ROLE 3: AUTONOMOUS PLACEMENT & INTERVIEW LEDGER ---
elif role_view == "🤝 Autonomous Placement & Interview Ledger":
    st.subheader("🤝 Autonomous Recruiter Dispatch & Placement Audit Ledger")
    st.markdown("Real-time immutable ledger tracking candidate job applications, employer interview dispatches, and verification hashes.")
    
    try:
        l_res = requests.get(f"{BACKEND_URL}/api/placements/ledger", timeout=2)
        if l_res.status_code == 200:
            ledger = l_res.json()["data"]
            if ledger:
                st.dataframe(ledger, use_container_width=True)
            else:
                st.info("No dispatches logged yet. Complete a student exam submission in the Student Portal tab!")
    except Exception as e:
        st.error(f"Could not load placement ledger: {e}")
