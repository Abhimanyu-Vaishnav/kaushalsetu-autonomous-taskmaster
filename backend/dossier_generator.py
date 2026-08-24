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
    metric_hash: str
) -> str:
    """
    Generates domain-adaptive responsive standalone HTML/CSS/Tailwind portfolio dossiers.
    - Tech/Coding: Cyberpunk / Modern Terminal Theme
    - Finance/Tally: Executive Corporate Navy / Emerald Theme
    - Automotive/Diagnostics: Industrial Titanium / Solar Orange Theme
    """
    total_score = scores.get("total_score", 90)
    mcq_score = scores.get("mcq_score", 30.0)
    practical_score = scores.get("practical_score", 60.0)
    
    course_lower = course_name.lower()
    
    # 1. Determine Domain Theme
    if "web" in course_lower or "code" in course_lower or "stack" in course_lower or "developer" in course_lower:
        # Cyberpunk Tech Theme
        theme_bg = "bg-slate-950 text-slate-100"
        card_bg = "bg-slate-900 border-slate-800"
        accent_color = "from-cyan-400 to-indigo-500"
        badge_bg = "bg-cyan-950 text-cyan-300 border-cyan-700"
        icon_class = "fa-code"
        theme_title = "Tech & SaaS Engineering Dossier"
    elif "finance" in course_lower or "tally" in course_lower or "accounting" in course_lower:
        # Executive Corporate Theme
        theme_bg = "bg-gray-950 text-gray-100"
        card_bg = "bg-slate-900 border-slate-700"
        accent_color = "from-emerald-400 to-teal-500"
        badge_bg = "bg-emerald-950 text-emerald-300 border-emerald-700"
        icon_class = "fa-chart-pie"
        theme_title = "Corporate Financial & Compliance Dossier"
    else:
        # Industrial Automotive Theme
        theme_bg = "bg-zinc-950 text-zinc-100"
        card_bg = "bg-zinc-900 border-zinc-800"
        accent_color = "from-amber-400 to-orange-500"
        badge_bg = "bg-orange-950 text-orange-300 border-orange-700"
        icon_class = "fa-screwdriver-wrench"
        theme_title = "Automotive & Industrial Engineering Dossier"

    skills_badges = "".join([f'<span class="text-xs font-semibold px-3 py-1 rounded-full border {badge_bg}">{s}</span>' for s in skills])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkillForge Official Dossier - {candidate_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 0 15px rgba(99, 102, 241, 0.3); }}
            50% {{ box-shadow: 0 0 30px rgba(99, 102, 241, 0.6); }}
        }}
        .glow-card {{ animation: pulseGlow 4s infinite; }}
    </style>
</head>
<body class="{theme_bg} font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-4xl mx-auto space-y-8">
        
        <!-- Header Profile Card -->
        <div class="{card_bg} border rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 glow-card">
            <div class="flex items-center gap-5">
                <div class="w-20 h-20 rounded-full bg-gradient-to-tr {accent_color} flex items-center justify-center text-3xl font-extrabold text-white shadow-lg">
                    {candidate_name[0]}
                </div>
                <div>
                    <div class="text-xs text-indigo-400 font-mono font-semibold uppercase tracking-wider mb-1"><i class="fa-solid {icon_class} mr-1"></i> {theme_title}</div>
                    <h1 class="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
                        {candidate_name}
                        <span class="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-0.5 rounded-full border border-emerald-500/20 font-medium">Verified Official Seal</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Student ID: <code class="text-indigo-400 font-mono">{student_id}</code> | Branch Node: <span class="text-slate-200">{branch_name}</span></p>
                    <p class="text-indigo-300 text-sm font-semibold mt-1">{course_name}</p>
                </div>
            </div>
            <div class="text-center md:text-right bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                <div class="text-xs text-slate-400 font-semibold uppercase tracking-wider">SkillForge Score</div>
                <div class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r {accent_color}">{total_score}%</div>
                <div class="text-xs text-emerald-400 font-medium mt-0.5">Placement Qualified 🚀</div>
            </div>
        </div>

        <!-- Scores & Verification Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="{card_bg} border p-5 rounded-xl text-center">
                <div class="text-slate-400 text-xs font-semibold uppercase">MCQ Assessment</div>
                <div class="text-3xl font-bold text-emerald-400 mt-2">{mcq_score} <span class="text-sm font-normal text-slate-500">/ 50 pts</span></div>
                <p class="text-xs text-slate-500 mt-1">Objective Competency</p>
            </div>
            <div class="{card_bg} border p-5 rounded-xl text-center">
                <div class="text-slate-400 text-xs font-semibold uppercase">Multimodal Practical Work</div>
                <div class="text-3xl font-bold text-cyan-400 mt-2">{practical_score} <span class="text-sm font-normal text-slate-500">/ 50 pts</span></div>
                <p class="text-xs text-slate-500 mt-1">Project & Code Execution</p>
            </div>
            <div class="{card_bg} border p-5 rounded-xl text-center">
                <div class="text-slate-400 text-xs font-semibold uppercase">Cryptographic SHA-256 Hash</div>
                <div class="text-xs font-mono text-indigo-300 bg-slate-950 p-2.5 rounded-lg mt-2 truncate border border-slate-800">{metric_hash}</div>
                <p class="text-xs text-slate-500 mt-1">Immutable Verification Badge</p>
            </div>
        </div>

        <!-- Verified Skills Badge Section -->
        <div class="{card_bg} border rounded-2xl p-6">
            <h3 class="text-lg font-bold text-white mb-3 flex items-center gap-2"><i class="fa-solid fa-award text-amber-400"></i> Verified Competencies & Tech Stack</h3>
            <div class="flex flex-wrap gap-2">
                {skills_badges}
            </div>
        </div>

        <!-- Capstone Project Demonstration -->
        <div class="{card_bg} border rounded-2xl p-6 md:p-8 space-y-4">
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-layer-group text-indigo-400"></i> Multimodal Practical Project Capstone
            </h3>
            <h4 class="text-md font-semibold text-slate-200">{project_title}</h4>
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300 text-sm font-mono leading-relaxed">
                {project_description}
            </div>
            <div class="flex flex-wrap gap-4 pt-2">
                {f'<a href="{github_url}" target="_blank" class="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-brands fa-github"></i> View GitHub Code Repository</a>' if github_url else ''}
                {f'<a href="{live_url}" target="_blank" class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition"><i class="fa-solid fa-external-link"></i> Launch Live Capstone Demo</a>' if live_url else ''}
            </div>
        </div>

        <!-- Footer Verification Seal -->
        <div class="text-center text-xs text-slate-500 pt-4 border-t border-slate-800/60">
            Official SkillForge Autonomous Candidate Verification Dossier • Issued by Vocational Node: {branch_name}
        </div>
    </div>
</body>
</html>
"""
    return html

def save_student_dossier(student_id: str, html_content: str) -> str:
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, f"{student_id}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path
