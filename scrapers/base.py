from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class JobPost:
    title: str
    company: str
    location: str
    url: str # Listing URL
    description: str # Full job description text
    source: str # e.g., 'indeed', 'glassdoor'
    date_posted: Optional[str] = None
    apply_url: Optional[str] = None # Direct ATS link if found

class BaseScraper:
    """
    Abstract base class for all job board scrapers.
    Supports context manager protocol so a single browser instance
    can be reused across search() and multiple fetch_description() calls.
    """
    def __init__(self):
        self.source = "base"
        self._playwright = None
        self._browser = None
        self._page = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        """Clean up browser resources."""
        if self._browser:
            self._browser.close()
            self._browser = None
            self._page = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def search(self, keywords: List[str], locations: List[str], max_results: int = 50) -> List[JobPost]:
        """
        Main entry point for the scraper.
        Returns a list of JobPost objects.
        """
        raise NotImplementedError("Subclasses must implement the search method.")

    def fetch_description(self, url: str) -> str:
        """
        Fetch the full job description for a given job URL.
        """
        raise NotImplementedError("Subclasses must implement fetch_description.")
