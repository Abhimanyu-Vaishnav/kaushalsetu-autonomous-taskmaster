# DEVPOST SUBMISSION PACK: SKILLFORGE AUTONOMOUS
**Category Track:** Taskmaster Track (Continuous Action Engine, Zero Chatbot UI)  
**Hackathon:** Google All Things Agentic Hackathon  

---

## 📌 Project Title
**SkillForge Autonomous**: Enterprise Multi-Tenant Vocational Operations & Autonomous Placement Platform

## 💡 Elevator Pitch (1-Line Summary)
SkillForge Autonomous is a 24/7 continuous action engine that automates vocational exam synthesis, dual-AI multimodal grading (Gemma + Gemini 3.5), and zero-friction candidate job placements with cryptographic verification.

---

## 🛑 The BYOF Problem (Bring Your Own Friction)
Vocational skilling foundations and training institutes across Tier-2/3 cities and rural centers (teaching automotive repair, CNC machining, electrical diagnostics, and web development) face massive administrative bottlenecks:
1. **Curriculum Synthesis Overhead**: Manually drafting industry-compliant practical assessments, MCQs, and rubrics consumes weeks of instructor time.
2. **Evaluation Latency**: Instructors spend 20+ hours/week manually grading physical circuit diagnostic logs, code submissions, and hardware repair photos.
3. **Placement Pipeline Bottleneck**: Qualified candidates sit idle in administrative approval queues for weeks before recruiter dispatch, while low-scoring candidates receive no structured remediation.

---

## ⚡ What SkillForge Autonomous Does
SkillForge Autonomous operates as an **Autonomous Continuous Action Engine** replacing administrative latency with automated AI workflows:
- **1. Institute Governance & Multi-Tenant Management**: Multi-branch support (e.g. Nangloi, Yamuna Vihar, Jwalapur) with configurable placement thresholds (e.g., 70%), candidate interview caps, and CSV bulk roster intake.
- **2. Gemini 3.5 Exam Synthesizer**: Generates 5-MCQ exams + practical project challenges + 3-parameter rubrics on demand.
- **3. Dual-AI Dynamic Real-Time Grading**:
  - *Objective Scoring (30 pts)*: Evaluates MCQ selections dynamically.
  - *Subjective Vision Scoring (70 pts)*: Gemma fast syntax/keyword pre-check combined with Gemini 3.5 Multimodal vision grading on hardware photos and diagnostic logs.
- **4. Verification Gate & Recruiter Dispatcher**:
  - If Total Score $\ge 70\%$ & Consent Authorized: Auto-matches candidate to enterprise requisitions (Tata Motors, Infosys, Schneider Electric), generates a SHA-256 metric hash, dispatches outbox applications, fires candidate/branch alerts, and issues an official downloadable HTML/PDF Verified Skill Certificate.
  - If Total Score $< 70\%$: Automatically assigns a personalized 7-day remedial micro-study schedule.

---

## 🛠️ How We Built It
- **Dual-AI Model Pipeline**:
  - **Gemma Fast Pre-Screener**: Sub-millisecond deterministic structure check verifying technical keywords (+0.2 Hackathon Bonus Track).
  - **Google GenAI SDK (`google-genai`)**: Gemini 3.5 Pro & Flash cognitive engine for exam synthesis, multimodal vision grading, and recruiter pitch generation.
- **Backend Architecture**: FastAPI REST framework, Pydantic schema validation, SQLite WAL thread-safe database engine.
- **Frontend Dashboard**: Modern Streamlit UI with 4 distinct operational tabs, real-time OpenTelemetry trace logs, and one-click judge demo mode.
- **Deployment**: Docker containerization on Google Cloud Run serverless infrastructure (`deploy_cloudrun.sh`).

---

## 🏆 Accomplishments We're Proud Of
- Created a **100% Zero-Chatbot Taskmaster Engine** where every user submission triggers real background database state updates and outbox webhook dispatches.
- Combined **Gemma fast screening** with **Gemini 3.5 cognitive reasoning** for dynamic real-time scoring.
- Implemented **Cryptographic Verification Hashes (SHA-256)** guaranteeing immutable skill dossiers for hiring partners.

---

## 🔮 What's Next for SkillForge Autonomous
- Real-time WhatsApp/SMS webhook dispatch integration via Twitch/Twilio.
- On-device Gemma vision inference for offline rural center diagnostic grading.
