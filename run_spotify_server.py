import os
import sys
import time
import subprocess
import signal
import json

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the script directory
os.chdir(script_dir)

# Function to check if the server is responding
def is_server_healthy():
    try:
        import requests
        response = requests.get('http://localhost:8888/health', timeout=2)
        return response.status_code == 200
    except:
        return False

# Print initial status
print(json.dumps({"status": "starting"}))

# Keep track of the process
process = None

def start_server():
    global process
    # Kill any existing process
    if process:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass
    
    # Start a new process
    with open('server_output.log', 'a') as log_file:
        log_file.write(f"\n\n--- Server restart at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
        process = subprocess.Popen(
            [sys.executable, 'spotify_mcp_server.py'],
            stdout=log_file,
            stderr=log_file
        )
    
    # Wait for server to start
    for _ in range(10):
        if is_server_healthy():
            return True
        time.sleep(1)
    return False

# Handle termination signals
def handle_signal(sig, frame):
    if process:
        process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# Main loop to keep the server running
try:
    while True:
        if not process or process.poll() is not None:
            # Server not running or has crashed, restart it
            if start_server():
                print(json.dumps({"status": "running"}))
            else:
                print(json.dumps({"status": "failed_to_start"}))
                time.sleep(30)  # Wait longer before retry if it failed to start
        elif not is_server_healthy():
            # Server is running but not responding, restart it
            print(json.dumps({"status": "restarting"}))
            start_server()
        
        # Sleep for a while before checking again
        time.sleep(5)
except Exception as e:
    with open('wrapper_error.log', 'a') as error_log:
        error_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error: {str(e)}\n")
    print(json.dumps({"status": "error", "message": str(e)}))
    if process:
        process.terminate()
    sys.exit(1) 