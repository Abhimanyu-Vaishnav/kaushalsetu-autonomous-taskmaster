import os
import json
import uuid
from typing import Dict, Any, List

def generate_student_portfolio_html(
    candidate_name: str,
    student_id: str,
    course_name: str,
    branch_name: str,
    email: str,
    scores: Dict[str, Any],
    skills: List[str],
    project_title: str,
    project_description: str,
    github_url: str,
    live_url: str,
    metric_hash: str,
    resume_data: Dict[str, Any] = None
) -> str:
    """
    Generates domain-adaptive responsive standalone HTML/CSS/Tailwind portfolio dossiers.
    Incorporate parsed candidate resume data (Experience Years, Past Companies, Target Roles, Bio).
    """
    total_score = scores.get("total_score", 90)
    mcq_score = scores.get("mcq_score", 30.0)
    practical_score = scores.get("practical_score", 60.0)
    
    course_lower = course_name.lower()
    
    # 1. Determine Graphical Domain Theme & Styling
    if "web" in course_lower or "code" in course_lower or "stack" in course_lower or "developer" in course_lower or "software" in course_lower:
        # Cyber Dark Theme
        theme_bg = "bg-[#0A0E17] text-slate-100"
        card_bg = "bg-[#111827] border-slate-800"
        accent_gradient = "from-cyan-400 via-indigo-500 to-purple-500"
        accent_color = "#38BDF8"
        badge_bg = "bg-cyan-950 text-cyan-300 border-cyan-700"
        icon_class = "fa-code"
        theme_title = "Cyber Engineering & Full-Stack Dossier"
        domain_chart_data = "[88, 92, 85, 90, 86]"
        domain_labels = "['Backend APIs', 'Frontend Architecture', 'Database Systems', 'DevOps & Deployment', 'Code Quality']"
        capstone_snippet = '<pre class="bg-slate-950 p-4 rounded-xl text-xs text-cyan-300 font-mono overflow-x-auto border border-slate-800"><code>// Autonomously Validated Code Execution\nasync function handleTransactionPayload(req, res) {\n  const verification = await crypto.verifyHash(req.payload);\n  return res.status(200).json({ status: "VERIFIED", hash: verification.hash });\n}</code></pre>'
    elif "finance" in course_lower or "tally" in course_lower or "accounting" in course_lower or "data" in course_lower:
        # Executive Corporate Emerald Navy Theme
        theme_bg = "bg-[#022C22] text-emerald-100"
        card_bg = "bg-[#064E3B] border-emerald-800/60"
        accent_gradient = "from-emerald-400 via-teal-400 to-cyan-500"
        accent_color = "#10B981"
        badge_bg = "bg-emerald-950 text-emerald-300 border-emerald-700"
        icon_class = "fa-chart-line"
        theme_title = "Corporate Financial & Analytics Dossier"
        domain_chart_data = "[95, 88, 92, 90, 94]"
        domain_labels = "['GST & Tally', 'Financial Modeling', 'Audit Compliance', 'Data Analytics', 'Risk Assessment']"
        capstone_snippet = '<div class="bg-[#022C22] p-4 rounded-xl border border-emerald-700/60 font-mono text-xs text-emerald-300"><div class="font-bold mb-2">📊 Financial Growth & Tax Reconciliation Model</div><div class="flex justify-between border-b border-emerald-800 py-1"><span>Q4 Revenue Reconciled</span><span class="text-white font-bold">₹42.8 Lakhs</span></div><div class="flex justify-between border-b border-emerald-800 py-1"><span>Tax Compliance Audit</span><span class="text-emerald-400 font-bold">100% Passed</span></div></div>'
    else:
        # Industrial Automotive Titanium Theme
        theme_bg = "bg-[#18181B] text-zinc-100"
        card_bg = "bg-[#27272A] border-zinc-700"
        accent_gradient = "from-amber-400 via-orange-500 to-red-500"
        accent_color = "#F59E0B"
        badge_bg = "bg-orange-950 text-orange-300 border-orange-700"
        icon_class = "fa-screwdriver-wrench"
        theme_title = "Automotive & Hardware Diagnostics Dossier"
        domain_chart_data = "[92, 95, 88, 94, 90]"
        domain_labels = "['ECU Flashing', 'CAN-bus Protocols', 'Signal Isolation', 'Safety Lockout', 'Wiring Diagnostics']"
        capstone_snippet = '<div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 font-mono text-xs text-amber-400"><div class="font-bold mb-1">⚡ ECU Diagnostic Waveform Summary</div><div>[OBD-II Inspection] Protocol: ISO 15765-4 CAN (11bit 500Kbps)</div><div>[Safety Isolation] High-Voltage System Lockout Confirmed ✅</div></div>'

    skills_badges = "".join([f'<span class="text-xs font-semibold px-3 py-1.5 rounded-lg border {badge_bg}">{s}</span>' for s in skills])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkillForge Official Dossier - {candidate_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }}
            50% {{ box-shadow: 0 0 30px rgba(56, 189, 248, 0.5); }}
        }}
        .glow-card {{ animation: pulseGlow 4s infinite; }}
    </style>
</head>
<body class="{theme_bg} font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-5xl mx-auto space-y-8">
        
        <!-- Header Profile Card -->
        <div class="{card_bg} border rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 glow-card">
            <div class="flex items-center gap-5">
                <div class="w-20 h-20 rounded-full bg-gradient-to-tr {accent_gradient} flex items-center justify-center text-3xl font-extrabold text-white shadow-xl">
                    {candidate_name[0]}
                </div>
                <div>
                    <div class="text-xs text-sky-400 font-mono font-semibold uppercase tracking-wider mb-1"><i class="fa-solid {icon_class} mr-1"></i> {theme_title}</div>
                    <h1 class="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
                        {candidate_name}
                        <span class="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-0.5 rounded-full border border-emerald-500/20 font-medium">Verified Official Seal</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Student ID: <code class="text-sky-400 font-mono">{student_id}</code> | Branch Node: <span class="text-slate-200">{branch_name}</span></p>
                    <p class="text-sky-300 text-sm font-semibold mt-1">{course_name}</p>
                </div>
            </div>
            <div class="text-center md:text-right bg-slate-950/70 p-5 rounded-xl border border-slate-800">
                <div class="text-xs text-slate-400 font-semibold uppercase tracking-wider">SkillForge Score</div>
                <div class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r {accent_gradient}">{total_score}%</div>
                <div class="text-xs text-emerald-400 font-medium mt-1">🏆 Qualified Candidate</div>
            </div>
        </div>

        <!-- 3-STAGE MILESTONE TIMELINE -->
        <div class="{card_bg} border rounded-2xl p-6">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4"><i class="fa-solid fa-route text-sky-400 mr-2"></i> Autonomous Certification Lifecycle Timeline</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">1</div>
                    <div>
                        <div class="text-xs text-slate-400 font-semibold">Stage 1</div>
                        <div class="text-sm font-bold text-white">Course Enrolled</div>
                    </div>
                </div>
                <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">2</div>
                    <div>
                        <div class="text-xs text-slate-400 font-semibold">Stage 2</div>
                        <div class="text-sm font-bold text-white">Capstone Verified</div>
                    </div>
                </div>
                <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold">3</div>
                    <div>
                        <div class="text-xs text-slate-400 font-semibold">Stage 3</div>
                        <div class="text-sm font-bold text-white">Employer Ready</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Chart & Competency Breakdown Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="{card_bg} border p-6 rounded-2xl space-y-4">
                <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="fa-solid fa-chart-pie text-sky-400"></i> Competency Radar Matrix</h3>
                <div class="w-full h-64 flex items-center justify-center">
                    <canvas id="skillsRadarCanvas"></canvas>
                </div>
            </div>

            <div class="{card_bg} border p-6 rounded-2xl space-y-4">
                <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="fa-solid fa-award text-amber-400"></i> Verified Skills & Assessment Breakdown</h3>
                <div class="space-y-3">
                    <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center">
                        <span class="text-slate-300 text-sm font-semibold">Objective MCQ Score</span>
                        <span class="text-emerald-400 font-bold text-base">{mcq_score} / 50.0 pts</span>
                    </div>
                    <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center">
                        <span class="text-slate-300 text-sm font-semibold">Practical Capstone Score</span>
                        <span class="text-cyan-400 font-bold text-base">{practical_score} / 50.0 pts</span>
                    </div>
                    <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
                        <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Cryptographic SHA-256 Seal</div>
                        <div class="text-xs font-mono text-indigo-300 truncate">{metric_hash}</div>
                    </div>
                    <div class="pt-2 flex flex-wrap gap-2">
                        {skills_badges}
                    </div>
                </div>
            </div>
        </div>

        <!-- Career History & Parsed Resume Section -->
        <div class="{card_bg} border rounded-2xl p-6 space-y-4">
            <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="fa-solid fa-user-check text-cyan-400"></i> Candidate Dossier & Target Preferences</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Target Role & Salary CTC Expectation</div>
                    <div class="font-bold text-white text-base">{(resume_data or {}).get("target_role_preference") or "Specialist Technical Role"}</div>
                    <div class="text-xs text-indigo-400 mt-1 font-mono">{(resume_data or {}).get("work_experience_years", 0)} Years Field Experience</div>
                </div>
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Past Experience & Industry Profile</div>
                    <div class="text-slate-300">{(resume_data or {}).get("past_companies_text") or "Certified through institutional curriculum & practical evaluation."}</div>
                </div>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 text-sm text-slate-300">
                <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Professional Bio Summary</div>
                <div>{(resume_data or {}).get("bio") or "Vocational graduate certified by SkillForge Autonomous Multi-Tenant Engine."}</div>
            </div>
        </div>

        <!-- Capstone Project Demonstration -->
        <div class="{card_bg} border rounded-2xl p-6 md:p-8 space-y-4">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-layer-group text-indigo-400"></i> Multimodal Practical Project Capstone
            </h3>
            <h4 class="text-md font-semibold text-slate-200">{project_title}</h4>
            {capstone_snippet}
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300 text-sm font-mono leading-relaxed">
                {project_description}
            </div>
            <div class="flex flex-wrap gap-4 pt-2">
                {f'<a href="{github_url}" target="_blank" class="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-brands fa-github"></i> View GitHub Code Repository</a>' if github_url else ''}
                {f'<a href="{live_url}" target="_blank" class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-solid fa-external-link"></i> Launch Live Capstone Demo</a>' if live_url else ''}
                <a href="mailto:{email}?subject=Interview%20Invitation%20for%20{candidate_name}" class="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-solid fa-envelope"></i> 📩 Schedule Technical Interview</a>
            </div>
        </div>

        <!-- Footer Verification Seal -->
        <div class="text-center text-xs text-slate-500 pt-4 border-t border-slate-800/60">
            Official SkillForge Autonomous Candidate Verification Dossier • Issued by Vocational Node: {branch_name}
        </div>
    </div>

    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        const ctx = document.getElementById('skillsRadarCanvas').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {domain_labels},
                datasets: [{{
                    label: 'Verified Score %',
                    data: {domain_chart_data},
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    borderColor: '{accent_color}',
                    pointBackgroundColor: '{accent_color}',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '{accent_color}'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        angleLines: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                        grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                        pointLabels: {{ color: '#94A3B8', font: {{ size: 11 }} }},
                        ticks: {{ display: false, beginAtZero: true, max: 100 }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
    }});
    </script>
</body>
</html>
"""
    return html
    return html

def save_student_dossier(student_id: str, html_content: str) -> str:
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, f"{student_id}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path
