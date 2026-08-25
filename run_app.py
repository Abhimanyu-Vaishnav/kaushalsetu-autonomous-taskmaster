import os
import sys
import subprocess

# Ensure root directory is on PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.environ["PYTHONPATH"] = ROOT_DIR + (":" if os.name != "nt" else ";") + os.environ.get("PYTHONPATH", "")
os.environ["PYTHONUNBUFFERED"] = "1"

port = os.environ.get("PORT", "8080")
print("=" * 60)
print(f"🌟 Launching KaushalSetu Direct-Engine on 0.0.0.0:{port}...")
print("=" * 60)

# Ensure database tables exist before UI opens
try:
    from backend.database import ensure_db_schema
    ensure_db_schema()
    print("✅ Database schema initialized successfully.")
except Exception as ex:
    print(f"[STARTUP SCHEMA WARNING] {ex}")

cmd = [
    sys.executable, "-m", "streamlit", "run", "frontend/app.py",
    "--server.port", str(port),
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false"
]

subprocess.run(cmd)
