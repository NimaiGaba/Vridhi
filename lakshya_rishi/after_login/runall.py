import subprocess
import threading
import socket
import time
import os

# Project root (one level up from 'after_login')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0

def wait_for_service(port, timeout=15):
    """Wait for a port to be open (service ready)"""
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(port):
            return True
        time.sleep(1)
    return False

def run_process(name, cmd):
    print(f"[{name}] Launching: {' '.join(cmd)} (cwd={BASE_DIR})")
    process = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',       # <-- Force UTF-8 decoding
        errors='replace'        # <-- Replace undecodable characters instead of crashing
    )
    for line in iter(process.stdout.readline, ''):
        print(f"[{name}] {line.strip()}")

def start_services():
    def run_chatbot():
        if not is_port_open(8002):  
            print("🚀 Starting chatbot service...")
            threading.Thread(
                target=run_process,
                args=("Chatbot", ["uvicorn", "after_login.frontend.bakend.main:app", "--reload", "--port", "8002"]),
                daemon=True
            ).start()
            if wait_for_service(8002):
                print("✅ Chatbot service is running on port 8002")
            else:
                print("❌ Chatbot failed to start")
        else:
            print("⚡ Chatbot already running on port 8002")

    def run_forecasting():
        if not is_port_open(8001):
            print("🚀 Starting forecasting service...")
            threading.Thread(
                target=run_process,
                args=("Forecasting", ["uvicorn", "after_login.frontend.app:app", "--reload", "--port", "8001"]),
                daemon=True
            ).start()
            if wait_for_service(8001):
                print("✅ Forecasting service is running on port 8001")
            else:
                print("❌ Forecasting failed to start")
        else:
            print("⚡ Forecasting already running on port 8001")

    threading.Thread(target=run_chatbot, daemon=True).start()
    threading.Thread(target=run_forecasting, daemon=True).start()
