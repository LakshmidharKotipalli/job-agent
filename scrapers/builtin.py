import time
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from .base import BaseScraper, JobPost

class BuiltInScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.source = "builtin"

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

        for location in locations:
            for keyword in keywords:
                if len(jobs) >= max_results:
                    break

                q = quote_plus(keyword)
                url = f"https://builtin.com/jobs?search={q}"

                print(f"[{self.source}] Scraping: {url}")
                try:
                    self._page.goto(url, wait_until="networkidle", timeout=15000)
                    time.sleep(2)

                    job_cards = self._page.locator('div[data-id="job-card"]').all()

                    for card in job_cards:
                        if len(jobs) >= max_results:
                            break

                        try:
                            title_el = card.locator('h2 a')
                            title = title_el.inner_text().strip() if title_el.count() > 0 else "Unknown"

                            company_el = card.locator('div[data-id="company-title"]')
                            company = company_el.inner_text().strip() if company_el.count() > 0 else "Unknown"

                            job_url = "https://builtin.com" + title_el.get_attribute('href') if title_el.count() > 0 else ""

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
        """Fetch the full description for a specific BuiltIn job, reusing the open browser."""
        self._ensure_browser()
        try:
            self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            desc_el = self._page.locator('.job-description')
            if desc_el.count() > 0:
                return desc_el.inner_text()
        except Exception as e:
            print(f"[{self.source}] failed to fetch description for {url}: {e}")
        return ""
