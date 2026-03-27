# Job Application Agent - Verification Walkthrough

All core components of the Personal Job Application Agent have been successfully implemented! Here is a summary of what was built and how you can verify it locally.

## What Was Completed
- **Project Infrastructure**: Configured search filters ([config.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/config.py)), generated an AI-friendly profile ([profile.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/profile.py)), and wrote a PDF parser ([resume_parser.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/resume_parser.py)) for your existing resume.
- **Job Scrapers**: Built resilient Playwright scrapers for Indeed, Glassdoor, and BuiltIn in the `scrapers/` module.
- **AI Brain**: Implemented [relevance.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/filter/relevance.py) to evaluate your resume against every job using Ollama, and [cover_letter.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/generator/cover_letter.py) to generate tailored 3-paragraph letters automatically.
- **Application Trackers**: Set up a robust SQLite tracking module ([db/tracker.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/db/tracker.py)) and a Flask web dashboard ([dashboard/app.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/dashboard/app.py) & [dashboard/templates/index.html](file:///Users/lakshmidharkotipalli/Desktop/Jobs/dashboard/templates/index.html)).
- **Orchestration**: Bound everything together into [agent.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/agent.py) for manual/test runs, and [scheduler.py](file:///Users/lakshmidharkotipalli/Desktop/Jobs/scheduler.py) for continuous autopilot.

## How to Verify (Dry-Run Mode)

Before letting the agent loose to click "submit" automatically, you should run a safe **Dry Run**. This tests the entire system (scraping, AI scoring, deduplication, and cover letter generation) but **prevents** the final form submission.

### 1. Ensure Prerequisites
1. Open your terminal in `/Users/lakshmidharkotipalli/Desktop/Jobs`.
2. Ensure your local LLM is running in the background (e.g., run `ollama serve` or open the Ollama desktop app).

### 2. Run the Agent Safely
In your terminal, activate the environment and run the agent:
```bash
source venv/bin/activate
python agent.py
```
*(Note: `agent.py` runs in Dry-Run mode by default unless you pass the `--live` flag).*

**What you will see:**
- The agent launches stealth browsers to query BuiltIn, Glassdoor, and Indeed for "AI Engineer", "Gen AI Developer", etc., in "Remote" and "United States".
- The terminal will log jobs it evaluates. If a job scores > 65 (based on Ollama's judgment), the agent generates a cover letter and saves it to the `cover_letters/` directory.
- It will safely skip the final "Submit" click.

### 3. Check the Dashboard
While or after running the agent, you can start the dashboard to view your AI tracker:
```bash
python dashboard/app.py
```
Open your browser to [http://localhost:5000](http://localhost:5000). You will instantly see all the jobs the agent analyzed, the status ("dry_run", "skipped"), their scores, and links to the job boards.

### 4. Going Live (Autopilot)
Once you're satisfied with the AI filter's accuracy:
```bash
python scheduler.py
```
This script will:
1. Spin up the Flask server in the background so the dashboard is continuously accessible.
2. Run the full agent.
3. Hibernate and repeat every 6 hours indefinitely. 

> [!TIP]
> If you find the agent is applying to jobs you don't like, simply increase the `MIN_RELEVANCE_SCORE` in `config.py` from 65 to 80 to make it stricter!
