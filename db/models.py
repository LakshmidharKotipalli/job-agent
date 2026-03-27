"""Table schema definitions for the job scout database."""

JOBS_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_hash TEXT UNIQUE,
        title TEXT,
        company TEXT,
        url TEXT,
        source TEXT,
        score INTEGER DEFAULT 0,
        reason TEXT DEFAULT '',
        status TEXT DEFAULT 'low_match',
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cover_letter_path TEXT DEFAULT '',
        job_description TEXT DEFAULT ''
    )
'''
