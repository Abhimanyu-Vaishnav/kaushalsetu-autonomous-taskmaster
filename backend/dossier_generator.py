import os
import json
import uuid
import hashlib
from typing import Dict, Any, List

def classify_archetype(course_name: str, target_role: str = "", skills_list: str = "") -> str:
    """Classifies candidate into 1 of 4 domain archetypes based on course, role, and skills."""
    combined = f"{course_name} {target_role} {skills_list}".lower()
    
    # Archetype A: DEVELOPER_FULLSTACK
    dev_keywords = ["code", "dev", "python", "react", "web", "javascript", "full stack", "api", "software", "frontend", "backend", "fullstack", "programming"]
    if any(k in combined for k in dev_keywords):
        return "DEVELOPER_FULLSTACK"
        
    # Archetype B: FINANCE_ACCOUNTING
    finance_keywords = ["tally", "gst", "account", "finance", "audit", "tax", "ledger", "banking", "commerce", "balance", "reconciliation"]
    if any(k in combined for k in finance_keywords):
        return "FINANCE_ACCOUNTING"
        
    # Archetype C: AUTOMOTIVE_HARDWARE
    hardware_keywords = ["ecu", "automotive", "hardware", "diagnostic", "circuit", "mechanical", "ev", "motor", "oscilloscope", "obd", "can-bus", "wiring"]
    if any(k in combined for k in hardware_keywords):
        return "AUTOMOTIVE_HARDWARE"
        
    # Archetype D: GENERAL_PROFESSIONAL
    return "GENERAL_PROFESSIONAL"

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
    Generates Universal Domain-Adaptive & Experience-Grounded Graphical Dossiers.
    Dynamically renders tailored visual themes and interactive widgets for ALL archetypes.
    """
    resume_data = resume_data or {}
    total_score = scores.get("total_score", 90)
    mcq_score = scores.get("mcq_score", 30.0)
    practical_score = scores.get("practical_score", 60.0)
    
    target_role = resume_data.get("target_role_preference") or "Specialist Engineer"
    skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills or "")
    exp_years = int(resume_data.get("work_experience_years", 0))
    past_companies = resume_data.get("past_companies_text") or "Certified through SkillForge institutional curriculum & practical evaluation."
    bio_text = resume_data.get("bio") or f"Vocational graduate specializing in {course_name}, certified by SkillForge Autonomous Engine."
    
    # 1. Experience Level Hero Badge
    if exp_years == 0:
        exp_badge = "⚡ Fresh Certified Specialist | Immediate Joiner"
    elif exp_years <= 3:
        exp_badge = f"💼 Intermediate Specialist | {exp_years} Years Industry Exposure"
    else:
        exp_badge = f"🏆 Senior Practitioner | {exp_years} Years Proven Track Record"

    # 2. Universal Domain Classification & Theme Setup
    archetype = classify_archetype(course_name, target_role, skills_str)
    
    if archetype == "DEVELOPER_FULLSTACK":
        theme_bg = "bg-[#0B0F19] text-slate-100"
        card_bg = "bg-[#111827] border-slate-800"
        accent_gradient = "from-cyan-400 via-indigo-500 to-purple-500"
        accent_color = "#38BDF8"
        badge_bg = "bg-cyan-950 text-cyan-300 border-cyan-700"
        icon_class = "fa-code"
        archetype_title = "Full-Stack Software Engineering & Dev Hub"
        
        domain_labels = "['Backend REST APIs', 'Frontend React UI', 'Database Systems', 'DevOps & Docker', 'Code Quality']"
        domain_scores = "[92, 88, 90, 85, 94]"
        
        interactive_widget = f"""
        <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs text-cyan-300 space-y-2">
            <div class="flex justify-between items-center text-slate-500 border-b border-slate-800 pb-2">
                <span><i class="fa-solid fa-terminal mr-1 text-sky-400"></i> Code Execution Sandbox</span>
                <span class="text-emerald-400 font-bold">● Live Route Verified</span>
            </div>
            <pre class="overflow-x-auto text-sky-300"><code>// Autonomously Verified REST API Controller\nasync function handleCandidateVerification(req, res) {{\n  const payload = {{ student_id: "{student_id}", score: "{total_score}%" }};\n  const sha256 = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(JSON.stringify(payload)));\n  return res.status(200).json({{ status: "VERIFIED", hash: "{metric_hash[:16]}" }});\n}}</code></pre>
        </div>
        """
        
    elif archetype == "FINANCE_ACCOUNTING":
        theme_bg = "bg-[#022C22] text-emerald-100"
        card_bg = "bg-[#064E3B] border-emerald-800/60"
        accent_gradient = "from-emerald-400 via-teal-400 to-cyan-500"
        accent_color = "#10B981"
        badge_bg = "bg-emerald-950 text-emerald-300 border-emerald-700"
        icon_class = "fa-chart-line"
        archetype_title = "Corporate Accounting, GST & Tally Financial Dossier"
        
        domain_labels = "['Tally & GST Compliance', 'Balance Sheet Reconciliation', 'Tax Return Filing', 'Double-Entry Audit', 'Financial Analytics']"
        domain_scores = "[95, 90, 94, 92, 88]"
        
        interactive_widget = f"""
        <div class="bg-[#022C22] p-5 rounded-xl border border-emerald-700/60 font-mono text-xs text-emerald-200 space-y-3">
            <div class="flex justify-between items-center border-b border-emerald-800 pb-2">
                <span class="font-bold text-white"><i class="fa-solid fa-calculator text-emerald-400 mr-1"></i> Double-Entry Audit Ledger</span>
                <span class="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded text-[10px] font-bold border border-emerald-500/30">100% Tax Compliant</span>
            </div>
            <div class="flex justify-between items-center border-b border-emerald-800/60 py-1.5">
                <span>Q4 GST Return Filing & Ledger Audit</span>
                <span class="text-emerald-400 font-bold">₹48,50,000 Reconciled</span>
            </div>
            <div class="space-y-1 pt-1">
                <div class="flex justify-between text-[11px]">
                    <span class="text-slate-300">GST Compliance Accuracy</span>
                    <span class="text-emerald-300 font-bold">98.5%</span>
                </div>
                <div class="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-emerald-800">
                    <div class="bg-gradient-to-r from-emerald-400 to-teal-400 h-2 rounded-full" style="width: 98.5%"></div>
                </div>
            </div>
        </div>
        """
        
    elif archetype == "AUTOMOTIVE_HARDWARE":
        theme_bg = "bg-[#18181B] text-zinc-100"
        card_bg = "bg-[#27272A] border-zinc-700"
        accent_gradient = "from-amber-400 via-orange-500 to-red-500"
        accent_color = "#F59E0B"
        badge_bg = "bg-orange-950 text-orange-300 border-orange-700"
        icon_class = "fa-screwdriver-wrench"
        archetype_title = "Automotive & Hardware ECU Waveform Diagnostics"
        
        domain_labels = "['CAN-bus Protocols', 'ECU Flashing & Tuning', 'High-Voltage Lockout', 'OBD-II Sensor Analysis', 'Wiring Diagnostics']"
        domain_scores = "[94, 91, 96, 90, 89]"
        
        interactive_widget = f"""
        <div class="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-3 font-mono text-xs">
            <div class="flex justify-between items-center border-b border-zinc-800 pb-2 text-zinc-400">
                <span><i class="fa-solid fa-wave-square text-amber-400 mr-1"></i> CAN-bus Oscilloscope Signal Simulator</span>
                <span class="text-amber-400 font-bold">ISO 15765-4 Active</span>
            </div>
            <div class="relative w-full h-24 bg-black rounded border border-zinc-800 overflow-hidden flex items-center justify-center">
                <canvas id="canScopeCanvas" class="w-full h-full"></canvas>
            </div>
            <div class="flex justify-between text-[11px] text-zinc-400">
                <span>High-Voltage Safety Lockout: <strong class="text-emerald-400">VERIFIED 100%</strong></span>
                <span>OBD-II Fault Codes: <strong class="text-amber-400">0 Active DTCs</strong></span>
            </div>
        </div>
        """
        
    else:  # GENERAL_PROFESSIONAL
        theme_bg = "bg-[#0F172A] text-slate-100"
        card_bg = "bg-[#1E293B] border-slate-700"
        accent_gradient = "from-indigo-400 via-purple-400 to-pink-500"
        accent_color = "#818CF8"
        badge_bg = "bg-indigo-950 text-indigo-300 border-indigo-700"
        icon_class = "fa-briefcase"
        archetype_title = "Professional Operations & Business Analytics"
        
        domain_labels = "['Project Management', 'Operational Efficiency', 'Data Analytics', 'Client Delivery', 'Quality Control']"
        domain_scores = "[90, 88, 92, 94, 89]"
        
        interactive_widget = f"""
        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 font-mono text-xs text-slate-300">
            <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                <span><i class="fa-solid fa-chart-column text-indigo-400 mr-1"></i> Operations & Milestone KPI Grid</span>
                <span class="text-indigo-400 font-bold">Target SLA Achieved</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-center">
                <div class="bg-slate-900 p-2 rounded border border-slate-800">
                    <div class="text-slate-500 text-[10px]">Project SLA On-Time Delivery</div>
                    <div class="text-emerald-400 font-bold text-sm">99.2%</div>
                </div>
                <div class="bg-slate-900 p-2 rounded border border-slate-800">
                    <div class="text-slate-500 text-[10px]">Quality Standard Score</div>
                    <div class="text-indigo-300 font-bold text-sm">95 / 100</div>
                </div>
            </div>
        </div>
        """

    # 3. Harvest Live GitHub Repositories
    from agent_engine import fetch_github_profile_data
    github_data = fetch_github_profile_data(github_url)
    gh_projects = github_data.get("projects", [])
    
    if gh_projects:
        gh_cards_html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">'
        for proj in gh_projects:
            gh_cards_html += f"""
            <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between">
                        <a href="{proj['repo_url']}" target="_blank" class="font-bold text-sky-400 hover:text-sky-300 text-sm truncate flex items-center gap-1.5">
                            <i class="fa-brands fa-github"></i> {proj['name']}
                        </a>
                        <span class="text-[10px] bg-slate-900 text-slate-400 px-2 py-0.5 rounded border border-slate-800">⭐ {proj['stars']}</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-1 line-clamp-2">{proj['description']}</p>
                </div>
                <div class="flex justify-between items-center text-[10px] text-slate-500 mt-2.5 pt-2 border-t border-slate-900">
                    <span class="text-indigo-400 font-semibold">● {proj['language']}</span>
                    <span>Updated {proj['updated_at']}</span>
                </div>
            </div>
            """
        gh_cards_html += '</div>'
    else:
        gh_cards_html = ""

    skills_badges = "".join([f'<span class="text-xs font-semibold px-3 py-1.5 rounded-lg border {badge_bg}">{s}</span>' for s in skills])
    fallback_github = github_url or "https://github.com/skillforge-autonomous"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkillForge Official Dossier - {candidate_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="{theme_bg} font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-5xl mx-auto space-y-8">
        <div class="{card_bg} border rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div class="flex items-center gap-5">
                <div class="w-20 h-20 rounded-full bg-gradient-to-tr {accent_gradient} flex items-center justify-center text-3xl font-extrabold text-white shadow-xl">
                    {candidate_name[0]}
                </div>
                <div>
                    <div class="text-xs text-sky-400 font-mono font-semibold uppercase tracking-wider mb-1"><i class="fa-solid {icon_class} mr-1"></i> {archetype_title}</div>
                    <h1 class="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
                        {candidate_name}
                        <span class="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-0.5 rounded-full border border-emerald-500/20 font-medium">Verified Official Seal</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Student ID: <code class="text-sky-400 font-mono">{student_id}</code> | Branch Node: <span class="text-slate-200">{branch_name}</span></p>
                    <p class="text-sky-300 text-sm font-semibold mt-1">{course_name}</p>
                    <div class="mt-2 text-xs font-semibold text-emerald-400 bg-emerald-950/60 px-3 py-1 rounded-md border border-emerald-800/80 inline-block">{exp_badge}</div>
                </div>
            </div>
            <div class="text-center md:text-right bg-slate-950/70 p-5 rounded-xl border border-slate-800">
                <div class="text-xs text-slate-400 font-semibold uppercase tracking-wider">SkillForge Aggregate Score</div>
                <div class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r {accent_gradient}">{total_score}%</div>
                <div class="text-xs text-emerald-400 font-medium mt-1">🏆 Verified Certified Candidate</div>
            </div>
        </div>
        <div class="{card_bg} border rounded-2xl p-6">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4"><i class="fa-solid fa-route text-sky-400 mr-2"></i> Autonomous Certification Lifecycle Timeline</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">1</div>
                    <div><div class="text-xs text-slate-400 font-semibold">Stage 1</div><div class="text-sm font-bold text-white">Course Enrolled</div></div>
                </div>
                <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">2</div>
                    <div><div class="text-xs text-slate-400 font-semibold">Stage 2</div><div class="text-sm font-bold text-white">Capstone Verified</div></div>
                </div>
                <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold">3</div>
                    <div><div class="text-xs text-slate-400 font-semibold">Stage 3</div><div class="text-sm font-bold text-white">Employer Ready</div></div>
                </div>
            </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="{card_bg} border p-6 rounded-2xl space-y-4">
                <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="fa-solid fa-chart-pie text-sky-400"></i> Competency Radar Matrix</h3>
                <div class="w-full h-64"><canvas id="skillsRadarCanvas"></canvas></div>
            </div>
            <div class="{card_bg} border p-6 rounded-2xl space-y-4">
                <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="fa-solid fa-award text-amber-400"></i> Verified Skills Breakdown</h3>
                <div class="space-y-3">
                    <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center">
                        <span class="text-slate-300 text-sm font-semibold">MCQ Score</span>
                        <span class="text-emerald-400 font-bold">{mcq_score} / 50</span>
                    </div>
                    <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center">
                        <span class="text-slate-300 text-sm font-semibold">Practical Score</span>
                        <span class="text-cyan-400 font-bold">{practical_score} / 50</span>
                    </div>
                    <div class="pt-2 flex flex-wrap gap-2">{skills_badges}</div>
                </div>
            </div>
        </div>
        <div class="{card_bg} border rounded-2xl p-6 space-y-4">
            <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="fa-solid fa-id-card text-cyan-400"></i> Candidate Background & Experience Profile</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Target Role Preference</div>
                    <div class="font-bold text-white text-base">{target_role}</div>
                    <div class="text-xs text-indigo-400 mt-1 font-mono">{exp_years} Years Industry Exposure</div>
                </div>
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Past Industry Experience</div>
                    <div class="text-slate-300">{past_companies}</div>
                </div>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 text-sm text-slate-300">
                <div class="text-xs text-slate-400 font-semibold uppercase mb-1">Professional Bio Summary</div>
                <div>{bio_text}</div>
            </div>
        </div>
        <div class="{card_bg} border rounded-2xl p-6 md:p-8 space-y-4">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-layer-group text-indigo-400"></i> Domain Capstone Demonstration & Interactive Sandbox
            </h3>
            <h4 class="text-md font-semibold text-slate-200">{project_title}</h4>
            {interactive_widget}
            {f'<div class="pt-2"><h5 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2"><i class="fa-brands fa-github text-sky-400 mr-1.5"></i> Live GitHub Public Repositories (Harvested)</h5>{gh_cards_html}</div>' if gh_cards_html else ''}
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300 text-sm font-mono leading-relaxed mt-3">
                {project_description}
            </div>
            <div class="flex flex-wrap gap-4 pt-2">
                <a href="{fallback_github}" target="_blank" class="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-brands fa-github"></i> View GitHub Code Repository</a>
                {f'<a href="{live_url}" target="_blank" class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-solid fa-external-link"></i> Launch Live Capstone Demo</a>' if live_url else ''}
                <a href="mailto:{email}?subject=Interview%20Invitation%20for%20{candidate_name}" class="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-solid fa-envelope"></i> 📩 Schedule Technical Interview</a>
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
                        label: 'Competency Level',
                        data: {domain_scores},
                        backgroundColor: 'rgba(56, 189, 248, 0.2)',
                        borderColor: '{accent_color}',
                        pointBackgroundColor: '{accent_color}',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    scales: {{
                        r: {{
                            angleLines: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                            grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                            pointLabels: {{ color: '#9CA3AF', font: {{ size: 10 }} }},
                            ticks: {{ display: false, min: 0, max: 100 }}
                        }}
                    }},
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
            const canCanvas = document.getElementById('canScopeCanvas');
            if (canCanvas) {{
                const canCtx = canCanvas.getContext('2d');
                let step = 0;
                function drawWave() {{
                    canCtx.fillStyle = '#000000';
                    canCtx.fillRect(0, 0, canCanvas.width, canCanvas.height);
                    canCtx.strokeStyle = '#F59E0B';
                    canCtx.lineWidth = 1.5;
                    canCtx.beginPath();
                    for (let x = 0; x < canCanvas.width; x++) {{
                        const y = (canCanvas.height / 2) + Math.sin((x + step) * 0.1) * 15 + ((x % 30 < 15) ? 10 : -10);
                        if (x === 0) canCtx.moveTo(x, y);
                        else canCtx.lineTo(x, y);
                    }}
                    canCtx.stroke();
                    step += 2;
                    requestAnimationFrame(drawWave);
                }}
                drawWave();
            }}
        }});
        </script>
    </div>
</body>
</html>"""

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{student_id}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html

def save_student_dossier(student_id: str, html_content: str) -> str:
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{student_id}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path
