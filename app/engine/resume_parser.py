import fitz          # PyMuPDF
import docx
import spacy
import re
import json
import os

CONFIG_PATH = "config.json"

# Load spaCy model once at import time (expensive operation)
nlp = spacy.load("en_core_web_sm")

# ── Skills keyword bank ────────────────────────────────────────────
# These are the words we scan for in the resume text.
# You can add more here as needed later.
SKILLS_BANK = [
    # Programming languages
    "python", "javascript", "typescript", "java", "c++", "c#", "php",
    "ruby", "swift", "kotlin", "go", "rust", "r", "matlab",
    # Web
    "html", "css", "react", "vue", "angular", "nextjs", "nodejs",
    "django", "flask", "fastapi", "laravel", "wordpress",
    # Data & AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn",
    "data analysis", "data science", "sql", "postgresql", "mysql",
    "mongodb", "redis", "elasticsearch",
    # DevOps & Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "linux",
    "git", "ci/cd", "jenkins", "terraform",
    # Design & other
    "figma", "photoshop", "illustrator", "ui/ux", "seo",
    "content writing", "copywriting", "translation", "arabic",
    # Freelance-relevant
    "api", "rest", "graphql", "scraping", "automation",
    "excel", "powerpoint", "project management",
]


class ResumeParser:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_text = ""
        self.profile = {}

    # ── Public entry point ─────────────────────────────────────────
    def parse(self) -> dict:
        """Full pipeline: read → clean → extract → return profile."""
        self.raw_text = self._read_file()
        clean_text = self._clean_text(self.raw_text)
        self.profile = {
            "file_path":   self.file_path,
            "name":        self._extract_name(clean_text),
            "title":       self._extract_title(clean_text),
            "skills":      self._extract_skills(clean_text),
            "experience":  self._extract_experience(clean_text),
            "email":       self._extract_email(clean_text),
            "phone":       self._extract_phone(clean_text),
            "raw_text":    clean_text,          # kept for Phase 4 matching
        }
        self._save_profile()
        return self.profile

    # ── Step 1: Read file ──────────────────────────────────────────
    def _read_file(self) -> str:
        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == ".pdf":
            return self._read_pdf()
        elif ext == ".docx":
            return self._read_docx()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _read_pdf(self) -> str:
        text = ""
        with fitz.open(self.file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _read_docx(self) -> str:
        document = docx.Document(self.file_path)
        return "\n".join(p.text for p in document.paragraphs if p.text.strip())

    # ── Step 2: Clean text ─────────────────────────────────────────
    def _clean_text(self, text: str) -> str:
        # Collapse multiple blank lines into one
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove non-printable characters
        text = re.sub(r"[^\x20-\x7E\n\u0600-\u06FF]", " ", text)
        # Collapse multiple spaces
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    # ── Step 3: Extract name ───────────────────────────────────────
    def _extract_name(self, text: str) -> str:
        """
        Strategy: spaCy NER looks for PERSON entities.
        We take the first one found — resumes usually start with the name.
        Fallback: first non-empty line of the resume.
        """
        doc = nlp(text[:500])       # only scan the top of the resume
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

        # Fallback: first line
        first_line = text.split("\n")[0].strip()
        return first_line if first_line else "Unknown"

    # ── Step 4: Extract job title ──────────────────────────────────
    def _extract_title(self, text: str) -> str:
        """
        Look for common title patterns in the first 300 characters.
        """
        title_patterns = [
            r"(Senior|Junior|Lead|Full[- ]?Stack|Front[- ]?end|Back[- ]?end"
            r"|Software|Web|Mobile|Data|ML|AI|DevOps|Cloud|UI|UX"
            r")[^\n,]{3,50}(Engineer|Developer|Designer|Scientist|Analyst"
            r"|Consultant|Specialist|Manager|Architect)",
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text[:600], re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return "Freelancer"

    # ── Step 5: Extract skills ─────────────────────────────────────
    def _extract_skills(self, text: str) -> list[str]:
        """
        Compare every word/phrase in SKILLS_BANK against the resume text.
        Case-insensitive. Returns a sorted, deduplicated list.
        """
        text_lower = text.lower()
        found = set()
        for skill in SKILLS_BANK:
            # Use word boundary matching so "r" doesn't match inside "developer"
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found.add(skill)
        return sorted(found)

    # ── Step 6: Extract years of experience ───────────────────────
    def _extract_experience(self, text: str) -> str:
        """
        Look for patterns like '5 years', '3+ years', '2 years of experience'.
        """
        pattern = r"(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)?"
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Take the largest number found (most likely total experience)
            years = max(int(m[0]) for m in matches)
            return f"{years} years"
        return "Not specified"

    # ── Step 7: Extract email ──────────────────────────────────────
    def _extract_email(self, text: str) -> str:
        match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
        return match.group(0) if match else ""

    # ── Step 8: Extract phone ──────────────────────────────────────
    def _extract_phone(self, text: str) -> str:
        match = re.search(
            r"(\+?\d{1,3}[\s\-]?)?(\(?\d{2,4}\)?[\s\-]?)(\d{3,4}[\s\-]?\d{3,4})",
            text,
        )
        return match.group(0).strip() if match else ""

    # ── Save profile to config ─────────────────────────────────────
    def _save_profile(self):
        config = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                content = f.read().strip()
                config = json.loads(content) if content else {}

        config["profile"] = {
            k: v for k, v in self.profile.items()
            if k != "raw_text"          # don't save full text to config
        }

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
