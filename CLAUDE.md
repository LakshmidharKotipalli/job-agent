# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A job scout agent that scrapes listings from Indeed, Glassdoor, Built In, Wellfound, SimplyHired, and Jobright.ai, scores them against a resume using a local Ollama LLM, generates tailored cover letters for high-scoring matches, and displays everything in a web dashboard. Everything runs locally -- no external APIs, no auto-applying.

## Commands

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt
playwright install

# Run agent (scrapes, scores, generates cover letters)
python agent.py

# Run scheduler (agent every 6 hours + dashboard)
python scheduler.py

# Run dashboard only
python dashboard/app.py
# Dashboard at http://localhost:5000

# Test resume parser
python resume_parser.py

# Test cover letter generator
python generator/cover_letter.py
```

Ollama must be running before starting the agent (`ollama serve` or the desktop app).

## Architecture

The pipeline in `agent.py` orchestrates everything in this order:

1. **Scrape** (`scrapers/`) -- Playwright headless browsers pull listings. Each scraper extends `BaseScraper` (in `scrapers/base.py`) and returns `JobPost` dataclass instances. Scrapers use a lazy `_ensure_browser()` pattern to reuse a single browser across `search()` and `fetch_description()` calls. Context manager protocol cleans up on exit.

2. **Deduplicate** (`filter/dedup.py`) -- Two-pass: fast title+company SHA-256 hash pre-description fetch, then full title+company+description hash post-fetch. Hashes loaded into memory from SQLite on init.

3. **Score** (`filter/relevance.py`) -- Sends resume text + job description to Ollama's `/api/generate` endpoint. Expects JSON response with `score` (0-100) and `reason`. Input is sanitized and truncated to 6000 chars. Timeout is 120s per job.

4. **Generate cover letter** (`generator/cover_letter.py`) -- Only for jobs scoring >= `MIN_RELEVANCE_SCORE` (default 65). Saves to `cover_letters/` with filename pattern `{Company}_{Title}_{timestamp}.txt`.

5. **Track** (`db/tracker.py`) -- SQLite CRUD. Single `jobs` table with `job_hash` as unique key. Uses `ON CONFLICT DO UPDATE` for upserts. Schema defined in `db/models.py`.

6. **Dashboard** (`dashboard/`) -- Flask web UI with filtering (by source, min score), sorting, cover letter modal viewer, and per-job detail pages at `/job/<id>`.

## Key Configuration

- `config.py` -- Search keywords, locations, `MIN_RELEVANCE_SCORE`, `MAX_JOBS_PER_RUN`, `BLOCKED_COMPANIES`, Ollama model/URL, file paths.
- `profile.py` -- Structured candidate data. Sensitive fields (email, phone) are required env vars from `.env`.
- `.env` -- `CANDIDATE_EMAIL`, `CANDIDATE_PHONE`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.

## Important Patterns

- All Ollama calls use `requests.post` to the `/api/generate` endpoint with `"stream": False`. The relevance scorer requests `"format": "json"`.
- Job descriptions are sanitized before LLM prompts (truncation + stripping prompt-breaking chars) to mitigate prompt injection.
- Scrapers use lazy browser init and context manager cleanup. Each scraper class is used as `with ScraperClass() as scraper:` in the agent loop.
- The `DedupFilter` reads from the DB on init but doesn't own the schema -- `db/tracker.py` owns table creation.
- The dashboard adds the parent directory to `sys.path` to import project modules.
