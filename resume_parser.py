import pypdf
import os
import json
from config import RESUME_PDF_PATH
from profile import PROFILE

def get_resume_text() -> str:
    """
    Attempts to extract text directly from the PDF.
    Returns the full parsed text string.
    """
    if not os.path.exists(RESUME_PDF_PATH):
        print(f"Warning: Resume not found at {RESUME_PDF_PATH}. Falling back to static profile.")
        return get_static_profile_text()

    try:
        reader = pypdf.PdfReader(RESUME_PDF_PATH)
        full_text = []
        for page in reader.pages:
            full_text.append(page.extract_text())
        
        text = "\n".join(full_text).strip()
        if len(text) < 100: # heuristic: if very short, likely an image/scanned PDF which pypdf missed
             print("Warning: Parsed text seems too short. Falling back to static profile.")
             return get_static_profile_text()
             
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}. Falling back to static profile.")
        return get_static_profile_text()

def get_static_profile_text() -> str:
    """
    Converts the structured static PROFILE dictionary into a readable string format
    that the LLM can easily consume.
    """
    return json.dumps(PROFILE, indent=2)

if __name__ == "__main__":
    # Test the parser
    print("--- Testing PDF Extraction ---")
    text = get_resume_text()
    print(f"Extracted {len(text)} characters of resume text.\n")
    print(text[:500] + "...\n")
