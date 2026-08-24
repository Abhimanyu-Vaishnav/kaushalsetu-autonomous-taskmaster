import subprocess
import sys
import time
import os
import signal

def run_app():
    print("=" * 60)
    print("[KaushalSetu Taskmaster] Starting Engine & Dashboard")
    print("=" * 60)
    
    port = os.environ.get("PORT", "8080")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Start FastAPI backend server
    print("1. Launching FastAPI Backend on http://localhost:8000 ...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=os.path.join(root_dir, "backend")
    )
    
    # Wait for backend to boot up
    time.sleep(3)
    
    # 2. Start Streamlit frontend server
    print(f"2. Launching Streamlit Dashboard on http://0.0.0.0:{port} ...")
    frontend_process = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            f"--server.port={port}",
            "--server.address=0.0.0.0",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ],
        cwd=root_dir
    )
    
    def shutdown_handler(signum=None, frame=None):
        print("\nShutting down KaushalSetu processes...")
        for p in [backend_process, frontend_process]:
            if p.poll() is None:
                p.terminate()
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
    except (ValueError, AttributeError):
        pass
    
    try:
        while True:
            b_poll = backend_process.poll()
            f_poll = frontend_process.poll()
            if b_poll is not None or f_poll is not None:
                print(f"Process exited - Backend code: {b_poll}, Frontend code: {f_poll}")
                shutdown_handler()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_handler()

if __name__ == "__main__":
    run_app()

