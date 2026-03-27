# 🤖 Personal Job Application Agent

A fully automated, AI-powered Python agent that scrapes job listings from multiple platforms, scores them against your resume using a local LLM (Ollama), generates tailored cover letters, and submits applications on your behalf — all while you sleep.

> **Privacy-first**: Everything runs locally. Your resume, job data, and cover letters never leave your machine.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Multi-Platform Scraping** | Scrapes Indeed, Glassdoor, and Built In using stealth Playwright browsers |
| **AI Relevance Scoring** | Uses your local Ollama model to rate every job against your resume (0–100) |
| **Tailored Cover Letters** | Auto-generates personalized 3-paragraph cover letters per job |
| **Smart Deduplication** | Prevents duplicate applications across platforms using content hashing |
| **Application Tracking** | SQLite database stores every job's company name, title, full description, score, and status |
| **Web Dashboard** | Flask UI at `localhost:5000` to monitor progress in real time |
| **Scheduled Autopilot** | Runs every 6 hours automatically via built-in scheduler |
| **Dry-Run Safety** | Default mode finds and scores jobs without submitting — flip to live when ready |

---

## 📁 Project Structure

```
job-agent/
├── agent.py               # Main orchestrator — runs the full pipeline
├── scheduler.py            # Cron-style loop (every 6 hrs) + launches dashboard
├── config.py               # Search keywords, locations, thresholds, Ollama settings
├── profile.py              # Your structured resume data for form-filling
├── resume_parser.py        # Extracts text from your PDF resume
│
├── scrapers/               # Playwright-based job board scrapers
│   ├── base.py             # Abstract BaseScraper + JobPost dataclass
│   ├── indeed.py           # Indeed scraper
│   ├── glassdoor.py        # Glassdoor scraper
│   └── builtin.py          # Built In scraper
│
├── filter/                 # AI filtering layer
│   ├── relevance.py        # Ollama-powered job scoring (0–100)
│   └── dedup.py            # Cross-platform duplicate detection
│
├── generator/              # Content generation
│   └── cover_letter.py     # Ollama-powered tailored cover letter writer
│
├── applier/                # Browser-based application bots
│   ├── indeed_apply.py     # Indeed Easy Apply bot
│   └── generic_apply.py    # Heuristic form-filler for ATS portals
│
├── db/                     # Persistence layer
│   └── tracker.py          # SQLite CRUD for application history
│
├── dashboard/              # Monitoring UI
│   ├── app.py              # Flask server
│   └── templates/
│       └── index.html      # Dashboard template
│
├── cover_letters/          # Generated cover letters saved here
├── jobs.db                 # SQLite database (auto-created on first run)
└── LAKSHMIDHAR KOTIPALLI.pdf  # Your resume
```

---

## 🛠️ Prerequisites

- **Python 3.10+**
- **Ollama** installed and running locally ([ollama.com](https://ollama.com))
  - Pull a model: `ollama pull llama3` (or `mistral`)
- **Playwright browsers**: installed via `playwright install`

---

## 🚀 Quick Start

### 1. Setup
```bash
cd /Users/lakshmidharkotipalli/Desktop/Jobs
python3 -m venv venv
source venv/bin/activate
pip install playwright pypdf requests httpx beautifulsoup4 schedule flask python-dotenv
playwright install
```

### 2. Configure
Edit `config.py` to customize:
- **Search keywords** — default: `AI Engineer`, `Gen AI Developer`, `ML Engineer`
- **Locations** — default: `Remote`, `United States`
- **MIN_RELEVANCE_SCORE** — raise to 80 for stricter filtering
- **BLOCKED_COMPANIES** — add companies you want to skip
- **OLLAMA_MODEL** — change to `mistral`, `deepseek-coder`, etc.

### 3. Dry Run (Recommended First Step)
```bash
source venv/bin/activate
python agent.py
```
This scrapes jobs, scores them with your LLM, and generates cover letters — but does **NOT** submit any applications. Check the terminal output and `cover_letters/` folder to verify quality.

### 4. View Dashboard
```bash
python dashboard/app.py
```
Open [http://localhost:5000](http://localhost:5000) to see all tracked jobs, scores, and statuses.

### 5. Go Live (Autopilot)
```bash
python agent.py --live
```
Or for continuous scheduled runs (every 6 hours + dashboard):
```bash
python scheduler.py
```

---

## ⚙️ How the Pipeline Works

```
1. SCRAPE      → Playwright browsers query Indeed, Glassdoor, Built In
                  with your configured keywords & locations

2. DEDUPLICATE → Hash-based check against SQLite to skip already-seen jobs

3. SCORE       → Ollama reads each job description + your resume
                  and returns a fit score (0–100) with reasoning

4. GENERATE    → For jobs scoring ≥ 65, Ollama writes a custom cover letter
                  highlighting your relevant experience

5. APPLY       → Playwright bot navigates to the application page,
                  fills in your details, uploads resume + cover letter
                  (only in --live mode)

6. TRACK       → Every job is logged to SQLite with full details:
                  company, title, description, score, status, timestamp
```

---

## 📊 What Gets Saved

Every job the agent encounters is permanently stored in `jobs.db` with:

| Column | Description |
|---|---|
| `title` | Job title |
| `company` | Company name |
| `job_description` | Full job description text |
| `url` | Link to the original listing |
| `source` | Which platform it came from |
| `score` | AI relevance score (0–100) |
| `status` | `applied`, `skipped`, `dry_run`, or `failed` |
| `cover_letter_path` | Path to the generated cover letter file |
| `applied_at` | Timestamp |

---

## ⚠️ Important Notes

- **Dry-run is ON by default**. The agent will never submit applications unless you explicitly pass `--live`.
- **Job board anti-bot measures**: Sites may occasionally block scraping. The agent uses stealth headers and human-like delays, but results may vary.
- **Ollama must be running** before starting the agent. Run `ollama serve` or open the Ollama desktop app.
- **LinkedIn is not included** due to aggressive anti-automation enforcement.

---

## 📝 License

Personal use only.
