import json
import os
from datetime import datetime
from app.engine.scrapers.mostaql import MostaqlScraper
from app.engine.scrapers.nafzly import NaflzyScraper

CONFIG_PATH = "config.json"
GIGS_CACHE_PATH = "gigs_cache.json"

SCRAPER_REGISTRY = {
    "mostaql": MostaqlScraper,
    "nafzly":  NaflzyScraper,
}

# ── English → Arabic keyword translations ─────────────────────────
# Arabic platforms search better with Arabic terms
ARABIC_KEYWORDS_MAP = {
    # Programming languages
    "python":           "بايثون",
    "javascript":       "جافاسكربت",
    "java":             "جافا",
    "php":              "PHP",
    "swift":            "Swift",
    "kotlin":           "كوتلن",
    "flutter":          "فلاتر",
    "dart":             "دارت",
    # Web
    "html":             "HTML",
    "css":              "CSS",
    "react":            "ريأكت",
    "wordpress":        "ووردبريس",
    "laravel":          "لارافيل",
    "django":           "جانقو",
    # Mobile
    "android":          "أندرويد",
    "mobile app":       "تطبيق موبايل",
    "mobile developer": "مطور تطبيقات",
    # Data
    "machine learning": "تعلم آلي",
    "data science":     "علم البيانات",
    "data analysis":    "تحليل البيانات",
    "artificial intelligence": "ذكاء اصطناعي",
    # Design
    "ui/ux":            "تصميم واجهات",
    "figma":            "فيجما",
    "photoshop":        "فوتوشوب",
    "graphic design":   "تصميم جرافيك",
    # DevOps
    "docker":           "docker",
    "git":              "git",
    "linux":            "لينكس",
    # General
    "web development":  "تطوير مواقع",
    "api":              "API",
    "sql":              "SQL",
    "mysql":            "MySQL",
    "postgresql":       "قواعد بيانات",
    "content writing":  "كتابة محتوى",
    "translation":      "ترجمة",
    "seo":              "تحسين محركات البحث",
    "excel":            "اكسل",
    "project management": "إدارة مشاريع",
    "ci/cd":            "ci/cd",
}


class ScraperManager:

    def __init__(self):
        self.config = self._load_config()
        self.keywords = self._get_keywords()
        self.scrapers = self._load_scrapers()

    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        return {}

    def _get_keywords(self) -> list[str]:
        profile = self.config.get("profile", {})
        skills = profile.get("skills", [])
        title = profile.get("title", "")

        keywords = list(skills)
        if title and title != "Freelancer":
            keywords.insert(0, title)

        if not keywords:
            keywords = ["python", "web development"]

        return keywords

    def _get_arabic_keywords(self, keywords: list[str]) -> list[str]:
        """
        For each English keyword, add its Arabic translation if available.
        Returns a combined list: [english1, arabic1, english2, arabic2, ...]
        Deduplicates and limits to 8 total to avoid too many requests.
        """
        combined = []
        seen = set()

        for kw in keywords:
            kw_lower = kw.lower()

            # Add English version
            if kw_lower not in seen:
                combined.append(kw_lower)
                seen.add(kw_lower)

            # Add Arabic translation if exists
            arabic = ARABIC_KEYWORDS_MAP.get(kw_lower)
            if arabic and arabic not in seen:
                combined.append(arabic)
                seen.add(arabic)

        return combined[:8]   # cap at 8 keywords

    def _load_scrapers(self) -> list:
        enabled_sites = self.config.get("sites", {})
        scrapers = []
        for name, scraper_class in SCRAPER_REGISTRY.items():
            if enabled_sites.get(name, True):
                scrapers.append(scraper_class())
                print(f"[manager] Loaded scraper: {name}")
        return scrapers

    def run(self, progress_callback=None) -> list[dict]:
        all_gigs = []
        total = len(self.scrapers)
        # Use bilingual keywords for Arabic platforms
        arabic_keywords = self._get_arabic_keywords(self.keywords)

        print(f"[manager] English keywords: {self.keywords[:4]}")
        print(f"[manager] Arabic keywords:  {arabic_keywords[:4]}")

        for i, scraper in enumerate(self.scrapers):
            if progress_callback:
                progress_callback(
                    f"Scanning {scraper.source}... ({i + 1}/{total})"
                )
            try:
                gigs = scraper.get_gigs(arabic_keywords)
                all_gigs.extend(gigs)
            except Exception as e:
                print(f"[manager] Scraper {scraper.source} failed: {e}")

        self._save_cache(all_gigs)

        if progress_callback:
            progress_callback(f"Done. Found {len(all_gigs)} gigs.")

        return all_gigs

    def _save_cache(self, gigs: list[dict]):
        cache = {
            "scraped_at": datetime.now().isoformat(),
            "total":      len(gigs),
            "gigs":       gigs,
        }
        with open(GIGS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"[manager] Saved {len(gigs)} gigs to {GIGS_CACHE_PATH}")
