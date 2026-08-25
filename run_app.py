import subprocess
import time
import sys
import os
import requests
import signal

def run_app():
    print("=" * 60)
    print("🚀 [Startup] Launching FastAPI Backend...")
    print("=" * 60)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=root_dir,
        env=backend_env
    )

    # Wait for backend readiness (up to 20 seconds)
    backend_ready = False
    for i in range(20):
        try:
            res = requests.get("http://127.0.0.1:8000/docs", timeout=1)
            if res.status_code in (200, 404):
                print(f"✅ Backend ready on attempt {i+1}")
                backend_ready = True
                break
        except Exception:
            time.sleep(1)

    if not backend_ready:
        print("⚠️ Warning: Backend health check timed out after 20s, proceeding to launch frontend...")

    # Start Streamlit on Cloud Run ingress port
    port = os.environ.get("PORT", "8080")
    print(f"🌟 Launching Streamlit on port {port}...")
    frontend_proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ], cwd=root_dir)

    def shutdown_handler(signum=None, frame=None):
        print("\nShutting down KaushalSetu processes...")
        for p in [backend_proc, frontend_proc]:
            if p and p.poll() is None:
                p.terminate()
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
    except (ValueError, AttributeError):
        pass

    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        shutdown_handler()

if __name__ == "__main__":
    run_app()
