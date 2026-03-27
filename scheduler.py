import schedule
import time
import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
flask_process = None

def run_flask():
    """Run the Flask dashboard in a background process."""
    global flask_process
    print("Starting dashboard on http://localhost:5000 ...")
    dashboard_path = os.path.join(BASE_DIR, "dashboard", "app.py")
    flask_process = subprocess.Popen([sys.executable, dashboard_path])

def run_agent_job():
    """The job executed by the scheduler."""
    print("\n" + "=" * 50)
    print(f"Running Job Scout at {time.ctime()}")
    print("=" * 50)

    agent_path = os.path.join(BASE_DIR, "agent.py")
    result = subprocess.run([sys.executable, agent_path], capture_output=True, text=True)

    log_path = os.path.join(BASE_DIR, "scheduler_log.txt")
    with open(log_path, "a") as f:
        f.write(f"\n--- Run at {time.ctime()} ---\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("ERRORS:\n")
            f.write(result.stderr)

    print("Agent run complete. Check scheduler_log.txt or the dashboard.")

if __name__ == "__main__":
    print("Initializing Job Scout Scheduler...")
    run_flask()

    # Run once immediately
    run_agent_job()

    # Schedule to run every 6 hours
    schedule.every(6).hours.do(run_agent_job)

    print("Scheduler active. Next run in 6 hours. Dashboard at http://localhost:5000")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
        if flask_process:
            flask_process.terminate()
            print("Dashboard stopped.")
