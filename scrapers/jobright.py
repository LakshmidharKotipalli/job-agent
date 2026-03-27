import time
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from .base import BaseScraper, JobPost

class JobrightScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.source = "jobright"

    def _ensure_browser(self):
        """Lazily launch a browser if one isn't already open."""
        if not self._browser:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)
            context = self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            self._page = context.new_page()

    def search(self, keywords: List[str], locations: List[str], max_results: int = 20) -> List[JobPost]:
        jobs = []
        self._ensure_browser()

        for keyword in keywords:
            if len(jobs) >= max_results:
                break

            q = quote_plus(keyword)
            url = f"https://jobright.ai/jobs?query={q}&jobType=fulltime"

            print(f"[{self.source}] Scraping: {url}")
            try:
                self._page.goto(url, wait_until="networkidle", timeout=20000)
                time.sleep(3)

                job_cards = self._page.locator('div[class*="job-card"], div[class*="JobCard"], article[class*="job"]').all()

                for card in job_cards:
                    if len(jobs) >= max_results:
                        break

                    try:
                        title_el = card.locator('a[class*="title"], h2 a, h3 a').first
                        title = title_el.inner_text().strip() if title_el.count() > 0 else "Unknown"

                        company_el = card.locator('span[class*="company"], a[class*="company"]').first
                        company = company_el.inner_text().strip() if company_el.count() > 0 else "Unknown"

                        location_el = card.locator('span[class*="location"]').first
                        location = location_el.inner_text().strip() if location_el.count() > 0 else "Remote"

                        href = title_el.get_attribute('href') if title_el.count() > 0 else ""
                        job_url = f"https://jobright.ai{href}" if href and not href.startswith("http") else href

                        if job_url:
                            jobs.append(JobPost(
                                title=title,
                                company=company,
                                location=location,
                                url=job_url,
                                description="",
                                source=self.source
                            ))
                    except Exception as e:
                        print(f"[{self.source}] Error parsing card: {e}")
                        continue

            except Exception as e:
                print(f"[{self.source}] Error navigating to search page: {e}")

        return jobs

    def fetch_description(self, url: str) -> str:
        """Fetch the full description for a specific Jobright job, reusing the open browser."""
        self._ensure_browser()
        try:
            self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            desc_el = self._page.locator('div[class*="description"], div[class*="jobDescription"]').first
            if desc_el.count() > 0:
                return desc_el.inner_text()
        except Exception as e:
            print(f"[{self.source}] failed to fetch description for {url}: {e}")
        return ""
