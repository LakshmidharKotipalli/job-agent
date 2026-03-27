import time
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from .base import BaseScraper, JobPost

class GlassdoorScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.source = "glassdoor"

    def _ensure_browser(self):
        """Lazily launch a browser if one isn't already open."""
        if not self._browser:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)
            context = self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
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
                loc_query = quote_plus(location)
                url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={q}&locT=C&locId=1&locKeyword={loc_query}"

                print(f"[{self.source}] Scraping: {url}")
                try:
                    self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    time.sleep(3)

                    job_cards = self._page.locator('li[data-test="jobListing"]').all()

                    for card in job_cards:
                        if len(jobs) >= max_results:
                            break

                        try:
                            title_el = card.locator('a[data-test="job-link"]').first
                            title = title_el.inner_text().strip() if title_el.count() > 0 else "Unknown"

                            # Use multiple selectors as fallback since Glassdoor uses hashed CSS classes
                            company = "Unknown"
                            for selector in ['span[data-test="employer-short-name"]', 'span.EmployerProfile_employerName__Cq9Sy', 'div.employer-name']:
                                company_el = card.locator(selector)
                                if company_el.count() > 0:
                                    company = company_el.first.inner_text().strip()
                                    break

                            loc_el = card.locator('div[data-test="emp-location"]')
                            loc = loc_el.inner_text().strip() if loc_el.count() > 0 else location

                            job_url = title_el.get_attribute('href') if title_el.count() > 0 else ""
                            if job_url and not job_url.startswith('http'):
                                job_url = "https://www.glassdoor.com" + job_url

                            if job_url:
                                jobs.append(JobPost(
                                    title=title,
                                    company=company,
                                    location=loc,
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
        """Fetch the full description for a specific Glassdoor job, reusing the open browser."""
        self._ensure_browser()
        try:
            self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            # Try multiple selectors since Glassdoor uses hashed CSS class names
            for selector in ['div[data-test="job-description"]', 'div.JobDetails_jobDescription__uW_fK', '.jobDescriptionContent']:
                desc_el = self._page.locator(selector)
                if desc_el.count() > 0:
                    return desc_el.first.inner_text()
        except Exception as e:
            print(f"[{self.source}] failed to fetch description for {url}: {e}")
        return ""
