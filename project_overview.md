# Personal Job Application Agent

A fully automated, AI-powered personal assistant that finds relevant job listings, scores them against your resume, generates tailored cover letters, and applies on your behalf while you sleep. Built entirely with Python, Playwright, and local LLMs (Ollama) for maximum privacy and zero API costs.

---

## 🚀 Features

- **Multi-Platform Scraping**: Automatically scrapes job listings from Indeed, Glassdoor, Built In, Wellfound, SimplyHired, and Jobright.ai using stealth Playwright browsers. *(LinkedIn is explicitly excluded to avoid aggressive anti-bot bans)*.
- **AI Relevance Filtering**: Uses your local Ollama instance (`llama3` or `mistral`) to compare every scraped job description against your resume. Only jobs scoring above your set threshold (e.g., 65/100) are processed further.
- **Tailored Cover Letters**: If a job passes the filter, the local LLM generates a highly personalized cover letter emphasizing the specific skills from your resume that match the job description.
- **Automated Applications**: Uses Playwright bots to navigate application portals (generic Workday/Greenhouse/Lever portals) and fills in your details, uploads your resume, and attaches the generated cover letter. *Note: Submit button is intentionally disabled as a safety measure; Indeed Apply is a manual fallback.*
- **Smart Tracking**: SQLite database prevents applying to the same job twice across different platforms and tracks the status of every application.
- **Local Dashboard**: A simple Flask web UI (`http://localhost:5000`) lets you monitor the agent's real-time progress, read the AI's relevance reasoning, and review submitted text.

---

## 🏗️ Architecture & Modules

The system is highly modular, making it easy to add new job boards or application heuristics.

```
job-agent/
├── config.py              # Central configuration (search terms, LLM settings, thresholds)
├── profile.py             # Your parsed demographic and professional data
├── resume_parser.py       # pypdf script to extract raw text from your PDF
├── agent.py               # Main orchestrator loop
├── scheduler.py           # Cron logic to run the agent periodically
│
├── scrapers/              # The "Eyes" (Playwright)
│   ├── base.py            # Abstract BaseScraper interface
│   ├── indeed.py          # Indeed pagination and extraction logic
│   ├── glassdoor.py       # Glassdoor logic
│   ├── builtin.py         # BuiltIn logic
│   ├── wellfound.py       # Wellfound (formerly AngelList) logic
│   ├── simplyhired.py     # SimplyHired logic
│   └── jobright.py        # Jobright.ai logic
│
├── filter/                # The "Brain" (Ollama)
│   ├── relevance.py       # Prompts LLM to score Job Description vs Resume Text
│   └── dedup.py           # Hashes job text to prevent cross-board duplicates
│
├── generator/             # The "Voice" (Ollama)
│   └── cover_letter.py    # Generates a 3-paragraph tailored letter per job
│
├── applier/               # The "Hands" (Playwright)
│   ├── indeed_apply.py    # specific Indeed Apply flow bot
│   └── generic_apply.py   # Heuristic HTML form-filler for company portals
│
├── db/                    # The "Memory" (SQLite)
│   ├── models.py          # Table schema definitions (CREATE TABLE SQL)
│   └── tracker.py         # CRUD operations for logging applications
│
└── dashboard/             # The "Face" (Flask)
    └── app.py             # Local web interface for monitoring
```

---

## ⚙️ How It Works (The Pipeline)

1. **Initialization**: The agent loads your `LAKSHMIDHAR KOTIPALLI.pdf` resume and parses it into text. It loads your target keywords (e.g., "AI Engineer", "Gen AI Developer") and locations from `config.py`.
2. **Scraping**: The `scrapers/` modules spin up headless browsers and pull down hundreds of recent job listings matching your criteria.
3. **Deduplication**: `filter/dedup.py` checks the SQLite database to ensure you haven't already applied to this exact role/company combo.
4. **Scoring**: `filter/relevance.py` sends the job description and your resume text to your local Ollama model. The model replies with a JSON object containing a `score` (0-100) and a `reason`.
5. **Generation**: If the score > 65, `generator/cover_letter.py` asks Ollama to write a custom cover letter. 
6. **Submission**: `applier/` modules take over the browser, navigate to the apply button, map your `profile.py` data to the HTML form fields, upload your PDF, paste the cover letter, and click submit.
7. **Tracking**: The result (Success, Failed Form, Skipped) is logged to the SQLite database and becomes visible on the Flask dashboard.

---

## 🛠️ Prerequisites

1. **Python 3.10+**
2. **Ollama**: Must be installed and running locally. (e.g., `ollama run llama3`)
3. **Playwright Browsers**: Run `playwright install` to download browser binaries.

## 🚀 Quick Start (Development)

1. **Clone & Install**:
   ```bash
   git clone <your-repo>
   cd job-agent
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install
   ```

2. **Configure**:
   - Place your resume PDF in the root directory.
   - Edit `config.py` with your search terms and location.

3. **Dry Run (Crucial First Step)**:
   ```bash
   python agent.py
   ```
   *Dry-run is the default. This will scrape, score, and write cover letters, but will **NOT** submit any forms. Use this to tune your relevance threshold!*

4. **Live Mode (Submit Applications)**:
   ```bash
   python agent.py --live
   ```
   *Pass `--live` to enable actual form submission.*

5. **Autopilot**:
   ```bash
   python scheduler.py
   ```
   *Starts the Flask dashboard on port 5000 and begins the scraping/applying loop.*
