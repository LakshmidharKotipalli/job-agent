import time
from playwright.sync_api import sync_playwright
from config import RESUME_PDF_PATH
from profile import PROFILE

class GenericApplier:
    def __init__(self):
        self.profile = PROFILE

    def apply(self, apply_url: str, cover_letter_path: str = "") -> bool:
        """
        Best-effort heuristic form filler for generic ATS portals (Workday, Greenhouse, Lever).
        """
        print(f"Attempting generic apply at: {apply_url}")
        success = False
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            try:
                page.goto(apply_url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(3)
                
                # Fill First Name
                page.locator("input[name*='first'], input[id*='first']").first.fill(self.profile['first_name'], timeout=2000)
                
                # Fill Last Name
                page.locator("input[name*='last'], input[id*='last']").first.fill(self.profile['last_name'], timeout=2000)
                
                # Fill Email
                page.locator("input[type='email'], input[name*='email']").first.fill(self.profile['email'], timeout=2000)
                
                # Fill Phone
                page.locator("input[type='tel'], input[name*='phone']").first.fill(self.profile['phone'], timeout=2000)
                
                # Upload Resume
                file_input = page.locator("input[type='file']").first
                if file_input.count() > 0:
                    file_input.set_input_files(RESUME_PDF_PATH, timeout=3000)
                    
                # Upload/Paste Cover Letter
                if cover_letter_path:
                    try:
                        with open(cover_letter_path, 'r', encoding='utf-8') as f:
                            cl_text = f.read()
                        textarea = page.locator("textarea[name*='cover'], textarea[id*='cover']").first
                        if textarea.count() > 0:
                            textarea.fill(cl_text, timeout=2000)
                    except Exception:
                        pass
                
                # Attempt to click the submit button
                submit_button = page.locator("button[type='submit'], input[type='submit']").first
                if submit_button.count() > 0:
                    submit_button.click(timeout=5000)
                    time.sleep(2)
                    print(f"Form submitted for {apply_url}.")
                    success = True
                else:
                    print(f"Form filled but no submit button found for {apply_url}. Flagging for manual review.")
                    success = False
                
            except Exception as e:
                print(f"Generic apply failed or timed out: {e}")
                success = False
            finally:
                browser.close()
                
        return success
