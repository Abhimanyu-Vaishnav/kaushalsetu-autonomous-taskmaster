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
    Generates a responsive standalone HTML/CSS portfolio page with Tailwind & animated charts.
    """
    total_score = scores.get("total_score", 90)
    mcq_score = scores.get("mcq_score", 30.0)
    practical_score = scores.get("practical_score", 60.0)
    
    skills_badges = "".join([f'<span class="bg-indigo-900 text-indigo-200 text-xs font-semibold px-3 py-1 rounded-full border border-indigo-700">{s}</span>' for s in skills])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkillForge Dossier - {candidate_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 0 15px rgba(99, 102, 241, 0.4); }}
            50% {{ box-shadow: 0 0 30px rgba(99, 102, 241, 0.8); }}
        }}
        .glow-card {{ animation: pulseGlow 4s infinite; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-4xl mx-auto space-y-8">
        
        <!-- Header Profile Card -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 glow-card">
            <div class="flex items-center gap-5">
                <div class="w-20 h-20 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-3xl font-extrabold text-white shadow-lg">
                    {candidate_name[0]}
                </div>
                <div>
                    <h1 class="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
                        {candidate_name}
                        <span class="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-0.5 rounded-full border border-emerald-500/20 font-medium">Verified Dossier</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">ID: <code class="text-indigo-400 font-mono">{student_id}</code> | Branch: <span class="text-slate-200">{branch_name}</span></p>
                    <p class="text-indigo-400 text-sm font-semibold mt-1">{course_name}</p>
                </div>
            </div>
            <div class="text-center md:text-right bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                <div class="text-xs text-slate-400 font-semibold uppercase tracking-wider">SkillForge Score</div>
                <div class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">{total_score}%</div>
                <div class="text-xs text-emerald-400 font-medium mt-0.5">Placement Qualified 🚀</div>
            </div>
        </div>

        <!-- Scores & Verification Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-slate-900/80 border border-slate-800 p-5 rounded-xl text-center">
                <div class="text-slate-400 text-xs font-semibold uppercase">MCQ Objective Assessment</div>
                <div class="text-3xl font-bold text-emerald-400 mt-2">{mcq_score} <span class="text-sm font-normal text-slate-500">/ 30 pts</span></div>
                <p class="text-xs text-slate-500 mt-1">Direct Technical Knowledge</p>
            </div>
            <div class="bg-slate-900/80 border border-slate-800 p-5 rounded-xl text-center">
                <div class="text-slate-400 text-xs font-semibold uppercase">Practical Vision Grading</div>
                <div class="text-3xl font-bold text-indigo-400 mt-2">{practical_score} <span class="text-sm font-normal text-slate-500">/ 70 pts</span></div>
                <p class="text-xs text-slate-500 mt-1">Multimodal Vision Inspection</p>
            </div>
            <div class="bg-slate-900/80 border border-slate-800 p-5 rounded-xl text-center">
                <div class="text-slate-400 text-xs font-semibold uppercase">Cryptographic Integrity</div>
                <div class="text-sm font-mono text-indigo-300 mt-3 truncate px-2">{metric_hash}</div>
                <p class="text-xs text-emerald-400 mt-2">SHA-256 Verified</p>
            </div>
        </div>

        <!-- Project Highlight & Artifacts -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 md:p-8 space-y-4">
            <h2 class="text-xl font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-microchip text-indigo-400"></i> Verified Practical Project Artifact
            </h2>
            <h3 class="text-lg font-semibold text-indigo-300">{project_title}</h3>
            <p class="text-slate-300 text-sm leading-relaxed bg-slate-950 p-4 rounded-lg border border-slate-800">
                "{project_description}"
            </p>
            
            <div class="flex flex-wrap gap-4 pt-2">
                {f'<a href="{github_url}" target="_blank" class="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition-colors"><i class="fa-brands fa-github text-base"></i> GitHub Code Repository</a>' if github_url else ''}
                {f'<a href="{live_url}" target="_blank" class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg shadow-md transition-colors"><i class="fa-solid fa-globe text-base"></i> Live Project Demo</a>' if live_url else ''}
            </div>
        </div>

        <!-- Verified Competency Tags -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">Verified Technical Competencies</h3>
            <div class="flex flex-wrap gap-2">
                {skills_badges}
            </div>
        </div>

        <!-- Footer Seal -->
        <div class="text-center text-xs text-slate-500 pt-4 border-t border-slate-800/80">
            <p>SkillForge Autonomous Continuous Placement Engine | Issued for Candidate ID: {student_id}</p>
        </div>
    </div>
</body>
</html>"""
    return html


def save_student_dossier(student_id: str, html_content: str) -> str:
    """
    Saves the generated dossier HTML to backend/static/portfolios/{student_id}.html
    """
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "portfolios")
    os.makedirs(out_dir, exist_ok=True)
    file_path = os.path.join(out_dir, f"{student_id}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path
