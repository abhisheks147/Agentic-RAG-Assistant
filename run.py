import subprocess
import time
import sys
import os
import socket

def kill_process_on_port(port):
    try:
        # Check using netstat on Windows
        output = subprocess.check_output("netstat -ano", shell=True).decode()
        pids_to_kill = set()
        for line in output.splitlines():
            if f":{port}" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        pids_to_kill.add(int(pid))
                    except ValueError:
                        pass
        for pid in pids_to_kill:
            if pid > 0:
                print(f"Port {port} is occupied. Killing process with PID {pid}...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
    except Exception as e:
        print(f"Error checking/killing process on port {port}: {e}")

def main():
    print("=" * 60)
    print("Starting Agentic RAG Assistant (Backend & Frontend)")
    print("=" * 60)

    # 1. Clear any existing processes on port 8000 and 8501
    kill_process_on_port(8000)
    kill_process_on_port(8501)

    python_exe = os.path.join("venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        print(f"Error: Virtual environment python not found at '{python_exe}'")
        print("Please run 'python -m venv venv' and install requirements.")
        sys.exit(1)

    print("Starting backend server (Uvicorn on port 8000)...")
    backend_log = open("backend.log", "w", encoding="utf-8")
    backend_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=backend_log,
        stderr=backend_log,
        text=True
    )

    print("Starting frontend server (Streamlit on port 8501)...")
    frontend_log = open("frontend.log", "w", encoding="utf-8")
    frontend_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "127.0.0.1"],
        stdout=frontend_log,
        stderr=frontend_log,
        text=True
    )

    # Give them a few seconds to start up
    print("Verifying services...")
    time.sleep(5)

    backend_running = backend_proc.poll() is None
    frontend_running = frontend_proc.poll() is None

    if backend_running and frontend_running:
        print("\nSuccess! Both services are running successfully.")
        print("Backend URL:  http://127.0.0.1:8000")
        print("Frontend URL: http://127.0.0.1:8501")
        print("Press Ctrl+C to stop both servers.\n")
    else:
        print("\nError during startup:")
        if not backend_running:
            print("- Backend failed to start. Last few lines of backend.log:")
            try:
                with open("backend.log", "r", encoding="utf-8") as f:
                    print("".join(f.readlines()[-15:]))
            except Exception:
                pass
        if not frontend_running:
            print("- Frontend failed to start. Last few lines of frontend.log:")
            try:
                with open("frontend.log", "r", encoding="utf-8") as f:
                    print("".join(f.readlines()[-15:]))
            except Exception:
                pass
        
        # Kill the other process if it's running
        if backend_proc.poll() is None:
            backend_proc.terminate()
        if frontend_proc.poll() is None:
            frontend_proc.terminate()
        sys.exit(1)

    try:
        # Monitor the processes
        while True:
            if backend_proc.poll() is not None:
                print("\nBackend server stopped unexpectedly!")
                print("Last few lines of backend.log:")
                try:
                    with open("backend.log", "r", encoding="utf-8") as f:
                        print("".join(f.readlines()[-20:]))
                except Exception:
                    pass
                break
            if frontend_proc.poll() is not None:
                print("\nFrontend server stopped unexpectedly!")
                print("Last few lines of frontend.log:")
                try:
                    with open("frontend.log", "r", encoding="utf-8") as f:
                        print("".join(f.readlines()[-20:]))
                except Exception:
                    pass
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        if backend_proc.poll() is None:
            backend_proc.terminate()
            backend_proc.wait()
        if frontend_proc.poll() is None:
            frontend_proc.terminate()
            frontend_proc.wait()
        backend_log.close()
        frontend_log.close()
        print("Servers stopped.")

if __name__ == "__main__":
    main()
