# Statically typed profile extracted from the resume
# Used as fallback if PDF parsing fails, and directly by application bots for form-filling.
import os
from dotenv import load_dotenv
load_dotenv()

PROFILE = {
    "first_name": "Lakshmidhar",
    "last_name": "Kotipalli",
    "email": os.environ["CANDIDATE_EMAIL"],  # Required: set in .env
    "phone": os.environ["CANDIDATE_PHONE"],  # Required: set in .env
    "linkedin": "https://www.linkedin.com/in/", # Can insert full URL if needed
    
    "skills": {
        "programming": ["Python", "SQL", "FastAPI"],
        "models": ["Qwen3-VL", "PaddleOCR-VL", "Gemma", "Mistral"],
        "deployment": ["vLLM", "llama.cpp", "Quantization"],
        "ocr": ["PaddleOCR", "PP-Structure", "Tesseract", "Layout Analysis"],
        "frameworks": ["Transformers", "LangChain", "RAG", "LangGraph"],
        "databases": ["PostgreSQL", "ChromaDB", "FAISS", "Qdrant"],
        "cloud": ["Google Cloud Platform", "Document AI", "Vertex AI", "Cloud Storage"],
        "claude": ["Skills", "Sub-Agents", "Hooks", "MCP Servers", "Plugins"]
    },
    
    "experience": [
        {
            "company": "PhFlow AI",
            "title": "AI Engineer",
            "location": "Tampa, USA",
            "start_date": "July 2025",
            "end_date": "Present",
            "highlights": [
                "Built a vision-language model extraction pipeline to digitize shipment documents from 15+ vendor layouts.",
                "Deployed the extraction pipeline on private GPU infrastructure",
                "Applied model quantization and tuned inference configuration to reduce document processing time from ~16 seconds to under 10 seconds",
                "Integrated an AI assistant RAG system into warehouse workflows"
            ]
        },
        {
            "company": "GanaIT",
            "title": "AI Engineer",
            "location": "Tampa, USA",
            "start_date": "May 2024",
            "end_date": "June 2025",
            "highlights": [
                "Built a retrieval-augmented QA system routing queries between internal docs and web search.",
                "Engineered retrieval pipeline using Qdrant, BGE embeddings, and semantic document chunking.",
                "Indexed private document collections spanning 9 volumes and 12,000 pages.",
                "Deployed the system locally using llama.cpp with GGUF models."
            ]
        }
    ],
    
    "education": [
        {
            "degree": "Master of Science in Data Science",
            "university": "University of Michigan-Dearborn",
            "graduation_date": "April 2024"
        },
        {
            "degree": "Bachelor's in Computer Science",
            "university": "Centurion University of Technology & Management",
            "graduation_date": "May 2022"
        }
    ]
}
