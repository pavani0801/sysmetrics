import subprocess
import threading

def stream_output(process, name):
    for line in iter(process.stdout.readline, b''):
        print(f"[{name}] {line.decode().rstrip()}")

def run_process(name, command):
    print(f"Starting '{name}' with command: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    )
    thread = threading.Thread(target=stream_output, args=(process, name))
    thread.start()
    return process, thread

if __name__ == "__main__":
    # Start both agent and web services
    print("Starting services...")
    dashboard_cmd = "python dashboard/manage.py runserver 0.0.0.0:7000"
    agent_cmd = "python agent/main.py"
    agent_proc, agent_thread = run_process("Agent", agent_cmd)
    dashboard_proc, dashboard_thread = run_process("Dashboard", dashboard_cmd)
    

    try:
        dashboard_thread.join()
        agent_thread.join()
    except KeyboardInterrupt:
        print("Shutting down services...")
        dashboard_proc.terminate()
        agent_proc.terminate()
