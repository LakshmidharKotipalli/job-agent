import time
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from .base import BaseScraper, JobPost

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.source = "indeed"

    def _ensure_browser(self):
        """Lazily launch a browser if one isn't already open."""
        if not self._browser:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.firefox.launch(headless=True)
            context = self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
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
                url = f"https://www.indeed.com/jobs?q={q}&l={loc_query}"

                print(f"[{self.source}] Scraping: {url}")
                try:
                    self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    time.sleep(3)

                    job_cards = self._page.locator('.job_seen_beacon').all()

                    for card in job_cards:
                        if len(jobs) >= max_results:
                            break

                        try:
                            title_el = card.locator('h2.jobTitle span[title]')
                            title = title_el.inner_text() if title_el.count() > 0 else "Unknown"

                            company_el = card.locator('[data-testid="company-name"]')
                            company = company_el.inner_text() if company_el.count() > 0 else "Unknown"

                            loc_el = card.locator('[data-testid="text-location"]')
                            loc = loc_el.inner_text() if loc_el.count() > 0 else location

                            link_el = card.locator('h2.jobTitle a')
                            job_url = "https://www.indeed.com" + link_el.get_attribute('href') if link_el.count() > 0 else ""

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
        """Fetch the full description for a specific Indeed job, reusing the open browser."""
        self._ensure_browser()
        try:
            self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            desc_el = self._page.locator('#jobDescriptionText')
            if desc_el.count() > 0:
                return desc_el.inner_text()
        except Exception as e:
            print(f"[{self.source}] failed to fetch description for {url}: {e}")
        return ""

if __name__ == "__main__":
    with IndeedScraper() as scraper:
        jobs = scraper.search(["AI Engineer"], ["Remote"], max_results=2)
        for j in jobs:
            print(f"Found: {j.title} at {j.company}")
            desc = scraper.fetch_description(j.url)
            print(f"Description length: {len(desc)}")
