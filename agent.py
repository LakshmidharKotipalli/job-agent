import time
from config import SEARCH_KEYWORDS, SEARCH_LOCATIONS, MIN_RELEVANCE_SCORE, MAX_JOBS_PER_RUN, BLOCKED_COMPANIES
from resume_parser import get_resume_text
from scrapers.indeed import IndeedScraper
from scrapers.glassdoor import GlassdoorScraper
from scrapers.builtin import BuiltInScraper
from scrapers.wellfound import WellfoundScraper
from scrapers.simplyhired import SimplyHiredScraper
from scrapers.jobright import JobrightScraper
from filter.dedup import DedupFilter
from filter.relevance import RelevanceReviewer
from generator.cover_letter import CoverLetterGenerator
from db.tracker import Tracker

def run_agent():
    print("Starting Job Scout Agent...")

    # 1. Initialize components
    resume_text = get_resume_text()
    if not resume_text:
        print("Failed to get resume text. Exiting.")
        return

    tracker = Tracker()
    dedup = DedupFilter(tracker.db_path)
    reviewer = RelevanceReviewer(resume_text)
    generator = CoverLetterGenerator(resume_text)

    scraper_classes = [
        BuiltInScraper,
        WellfoundScraper,
        SimplyHiredScraper,
        JobrightScraper,
        GlassdoorScraper,
        IndeedScraper,
    ]

    processed_count = 0

    # 2. Scrape jobs from all sources
    for ScraperClass in scraper_classes:
        if processed_count >= MAX_JOBS_PER_RUN:
            break

        with ScraperClass() as scraper:
            print(f"\n--- Scraping via {scraper.source} ---")
            try:
                jobs = scraper.search(SEARCH_KEYWORDS, SEARCH_LOCATIONS, max_results=15)
                print(f"Found {len(jobs)} jobs from {scraper.source}")

                for job in jobs:
                    if processed_count >= MAX_JOBS_PER_RUN:
                        break

                    # 3. Deduplication pre-check (fast, title+company only)
                    if dedup.is_duplicate(job.title, job.company):
                        print(f"  Skipping duplicate: {job.title} at {job.company}")
                        continue

                    # 3b. Blocked company check
                    if any(blocked.lower() in job.company.lower() for blocked in BLOCKED_COMPANIES):
                        print(f"  Skipping blocked company: {job.company}")
                        continue

                    print(f"\n  Evaluating: {job.title} at {job.company}")

                    # Fetch full description if missing (reuses scraper's browser)
                    if not job.description:
                        job.description = scraper.fetch_description(job.url)
                        time.sleep(1)

                    if not job.description:
                        print("  Could not fetch description, skipping.")
                        continue

                    # Deduplication post-description (more accurate, includes content)
                    if dedup.is_duplicate(job.title, job.company, job.description):
                        print(f"  Skipping duplicate (by content): {job.title} at {job.company}")
                        continue
                    job_hash = dedup.add_seen(job.title, job.company, job.description)

                    # 4. Score with LLM
                    review = reviewer.score_job(job.title, job.company, job.description)
                    score = review['score']
                    reason = review['reason']
                    print(f"  Score: {score}/100 — {reason}")

                    # 5. Generate cover letter for high-scoring jobs
                    cl_path = ""
                    if score >= MIN_RELEVANCE_SCORE:
                        cl_path = generator.generate(job.title, job.company, job.description)
                        if cl_path:
                            print(f"  Cover letter saved: {cl_path}")

                    # 6. Track everything
                    status = "relevant" if score >= MIN_RELEVANCE_SCORE else "low_match"
                    tracker.log_job(
                        job_hash, job.title, job.company, job.url, job.source,
                        score, reason, status, cl_path, job.description
                    )
                    processed_count += 1

            except Exception as e:
                print(f"Scraper loop exception for {scraper.source}: {e}")

    print(f"\nFinished. Scored {processed_count} jobs. View results at http://localhost:5000")

if __name__ == "__main__":
    run_agent()
