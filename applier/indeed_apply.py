import time
from playwright.sync_api import sync_playwright
from config import RESUME_PDF_PATH
from profile import PROFILE

class IndeedApplier:
    def __init__(self):
        self.profile = PROFILE

    def apply(self, job_url: str, cover_letter_path: str = "") -> bool:
        """
        Attempts to navigate through Indeed's Easy Apply flow.
        Returns True if successful, False otherwise.
        Note: requires an already logged-in session or extremely stable heuristic.
        Because manual login is tricky without a persistent context, this is a skeleton
        that attempts guest apply if available, or just logs the need for manual review.
        """
        print(f"Attempting to apply to Indeed: {job_url}")
        success = False
        with sync_playwright() as p:
            # For real usage, one should use a saved persistent_context to stay logged in.
            browser = p.firefox.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            
            try:
                page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(3)
                
                # Check for Apply Now button
                apply_button = page.locator('button#indeedApplyButton')
                if apply_button.count() == 0:
                    print("No Indeed Apply button found. Might redirect to company site.")
                    return False
                    
                apply_button.click()
                time.sleep(3)

                # Handling Indeed's apply modal (iframe usually)
                # Indeed's iframe structure changes rapidly and often requires 2FA login.
                # Flag for manual review in the dashboard.
                print("Indeed Apply modal reached but cannot automate multi-step iframe flow. Flagging for manual review.")
                success = False  # Intentionally False: Indeed automation is not implemented
                
            except Exception as e:
                print(f"Indeed apply failed: {e}")
            finally:
                browser.close()
                
        return success
