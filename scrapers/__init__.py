# scrapers module init
from .base import BaseScraper, JobPost
from .indeed import IndeedScraper
from .glassdoor import GlassdoorScraper
from .builtin import BuiltInScraper
from .wellfound import WellfoundScraper
from .simplyhired import SimplyHiredScraper
from .jobright import JobrightScraper

__all__ = [
    "BaseScraper", "JobPost",
    "IndeedScraper", "GlassdoorScraper", "BuiltInScraper",
    "WellfoundScraper", "SimplyHiredScraper", "JobrightScraper",
]
