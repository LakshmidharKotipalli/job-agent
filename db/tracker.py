import sqlite3
from typing import List, Dict, Any
from config import DB_PATH
from db.models import JOBS_TABLE_SQL

class Tracker:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(JOBS_TABLE_SQL)
            conn.commit()

    def log_job(self, job_hash: str, title: str, company: str, url: str,
                source: str, score: int, reason: str, status: str,
                cover_letter_path: str = "", job_description: str = ""):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO jobs (job_hash, title, company, url, source, score, reason, status, cover_letter_path, job_description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(job_hash) DO UPDATE SET
                        score=excluded.score,
                        reason=excluded.reason,
                        status=excluded.status,
                        cover_letter_path=excluded.cover_letter_path
                ''', (job_hash, title, company, url, source, score, reason, status, cover_letter_path, job_description))
                conn.commit()
        except Exception as e:
            print(f"Error logging to DB: {e}")

    def get_all_jobs(self, sort_by: str = "score", order: str = "desc",
                     source_filter: str = "", min_score: int = 0) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                allowed_sorts = {"score", "scraped_at", "company", "title", "source"}
                sort_col = sort_by if sort_by in allowed_sorts else "score"
                sort_order = "ASC" if order.lower() == "asc" else "DESC"

                query = f"SELECT * FROM jobs WHERE score >= ?"
                params: list = [min_score]

                if source_filter:
                    query += " AND source = ?"
                    params.append(source_filter)

                query += f" ORDER BY {sort_col} {sort_order}"
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error reading from DB: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM jobs")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE score >= 65")
                relevant = cursor.fetchone()[0]
                cursor.execute("SELECT AVG(score) FROM jobs WHERE score > 0")
                avg_row = cursor.fetchone()
                avg_score = round(avg_row[0], 1) if avg_row[0] else 0
                cursor.execute("SELECT source, COUNT(*) FROM jobs GROUP BY source")
                by_source = {row[0]: row[1] for row in cursor.fetchall()}
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE cover_letter_path != ''")
                with_cl = cursor.fetchone()[0]
                return {
                    "total": total,
                    "relevant": relevant,
                    "avg_score": avg_score,
                    "by_source": by_source,
                    "cover_letters": with_cl,
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total": 0, "relevant": 0, "avg_score": 0, "by_source": {}, "cover_letters": 0}

    def get_sources(self) -> List[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT source FROM jobs ORDER BY source")
                return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def get_job_by_id(self, job_id: int) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cursor.fetchone()
                return dict(row) if row else {}
        except Exception:
            return {}

    def get_cover_letter(self, job_id: int) -> str:
        job = self.get_job_by_id(job_id)
        cl_path = job.get("cover_letter_path", "")
        if cl_path:
            try:
                with open(cl_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return ""
