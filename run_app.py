import subprocess
import sys
import os
import time
import requests
import signal

# Set paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.environ["PYTHONPATH"] = ROOT_DIR + (":" if os.name != "nt" else ";") + os.environ.get("PYTHONPATH", "")
os.environ["PYTHONUNBUFFERED"] = "1"

def run_app():
    print("=" * 60)
    print("🚀 [Supervisor] Booting FastAPI Backend on 127.0.0.1:8000...")
    print("=" * 60)

    # 1. Start FastAPI backend with unbuffered stdout
    env_copy = os.environ.copy()
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"],
        env=env_copy,
        cwd=ROOT_DIR
    )

    # 2. Resilient Health Check Loop (Wait up to 25 seconds)
    backend_alive = False
    for i in range(25):
        try:
            res = requests.get("http://127.0.0.1:8000/api/health", timeout=1)
            if res.status_code == 200:
                print(f"✅ [Supervisor] FastAPI Backend is HEALTHY on attempt {i+1}!")
                backend_alive = True
                break
        except Exception:
            # Check if process died early
            if backend_proc.poll() is not None:
                print(f"❌ [Supervisor Error] Backend process exited unexpectedly with code {backend_proc.returncode}!")
                break
            time.sleep(1)

    if not backend_alive:
        print("⚠️ [Supervisor Warning] FastAPI health check did not respond with HTTP 200 after 25s.")

    # 3. Launch Streamlit Frontend on $PORT
    port = os.environ.get("PORT", "8080")
    print(f"🌟 [Supervisor] Launching Streamlit on port {port}...")
    frontend_proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ], cwd=ROOT_DIR)

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
