import subprocess
import sys
import time
import os

def run_app():
    print("=" * 60)
    print("[KaushalSetu Taskmaster] Starting Engine & Dashboard")
    print("=" * 60)
    
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
    print("2. Launching Streamlit Dashboard on http://localhost:8501 ...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"],
        cwd=root_dir
    )
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down KaushalSetu processes...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    run_app()
