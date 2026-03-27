import sqlite3
import hashlib
from typing import Set

def get_job_hash(title: str, company: str, description: str = "") -> str:
    """Create a unique hash for a job posting to detect duplicates.
    Uses title+company+description_snippet for the canonical hash stored in DB."""
    desc_snippet = description[:200].lower().strip() if description else ""
    normalized = f"{title.lower().strip()}_{company.lower().strip()}_{desc_snippet}"
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def get_quick_hash(title: str, company: str) -> str:
    """Lightweight title+company-only hash for fast pre-check before description is fetched."""
    normalized = f"{title.lower().strip()}_{company.lower().strip()}"
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

class DedupFilter:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.seen_hashes: Set[str] = set()       # Full hashes (title+company+desc)
        self.seen_quick_hashes: Set[str] = set()  # Quick hashes (title+company only)
        self._load_existing()

    def _load_existing(self):
        """Loads all existing job data from the SQLite database into memory for dedup."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Only read from the table; schema is owned by db/tracker.py
                # Check both old and new table names for backwards compatibility
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('jobs', 'applications')")
                table = cursor.fetchone()
                if table is None:
                    return  # No table exists yet, nothing to load
                table_name = table[0]
                cursor.execute(f"SELECT job_hash, title, company FROM {table_name} WHERE job_hash IS NOT NULL")
                rows = cursor.fetchall()
                for job_hash, title, company in rows:
                    self.seen_hashes.add(job_hash)
                    if title and company:
                        self.seen_quick_hashes.add(get_quick_hash(title, company))
        except Exception as e:
            print(f"Dedup load warning: {e}")

    def is_duplicate(self, title: str, company: str, description: str = "") -> bool:
        """Check if we've already processed this job.
        Uses quick hash (title+company) when no description is available,
        and full hash when description is provided."""
        if description:
            return get_job_hash(title, company, description) in self.seen_hashes
        return get_quick_hash(title, company) in self.seen_quick_hashes

    def add_seen(self, title: str, company: str, description: str = "") -> str:
        """Marks a job as seen in the current memory session (DB insert happens later).
        Returns the full hash for use as job_hash in the DB."""
        job_hash = get_job_hash(title, company, description)
        self.seen_hashes.add(job_hash)
        self.seen_quick_hashes.add(get_quick_hash(title, company))
        return job_hash
