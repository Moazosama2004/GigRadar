import json
import os
import re

CONFIG_PATH = "config.json"
GIGS_CACHE_PATH = "gigs_cache.json"

# ── Arabic translations for matching against Arabic gig text ───────
SKILL_ARABIC = {
    "python":           ["بايثون", "python"],
    "javascript":       ["جافاسكربت", "javascript"],
    "java":             ["جافا", "java"],
    "php":              ["php"],
    "kotlin":           ["كوتلن", "kotlin"],
    "flutter":          ["فلاتر", "flutter"],
    "swift":            ["swift"],
    "react":            ["ريأكت", "react"],
    "wordpress":        ["ووردبريس", "wordpress"],
    "laravel":          ["لارافيل", "laravel"],
    "django":           ["جانقو", "django"],
    "android":          ["أندرويد", "android"],
    "machine learning": ["تعلم آلي", "machine learning", "تعلم الآلة"],
    "data science":     ["علم البيانات", "data science"],
    "data analysis":    ["تحليل البيانات", "data analysis"],
    "artificial intelligence": ["ذكاء اصطناعي", "ai", "artificial intelligence"],
    "ui/ux":            ["تصميم واجهات", "ui", "ux", "واجهة مستخدم"],
    "figma":            ["فيجما", "figma"],
    "photoshop":        ["فوتوشوب", "photoshop"],
    "graphic design":   ["تصميم جرافيك", "graphic design", "جرافيك"],
    "docker":           ["docker"],
    "git":              ["git"],
    "linux":            ["لينكس", "linux"],
    "web development":  ["تطوير مواقع", "web", "موقع"],
    "sql":              ["sql", "قاعدة بيانات", "قواعد بيانات"],
    "mysql":            ["mysql"],
    "postgresql":       ["postgresql"],
    "content writing":  ["كتابة محتوى", "محتوى", "content"],
    "translation":      ["ترجمة", "translation"],
    "seo":              ["seo", "تحسين محركات البحث"],
    "excel":            ["اكسل", "excel"],
    "project management": ["إدارة مشاريع", "project management"],
    "mobile app":       ["تطبيق موبايل", "تطبيق", "mobile", "app"],
    "api":              ["api", "واجهة برمجية"],
    "nodejs":           ["nodejs", "node.js", "node"],
    "typescript":       ["typescript"],
    "vue":              ["vue", "vuejs"],
    "angular":          ["angular"],
    "mongodb":          ["mongodb", "mongo"],
    "redis":            ["redis"],
    "aws":              ["aws", "amazon web services"],
    "azure":            ["azure"],
    "ci/cd":            ["ci/cd", "devops", "ديف أوبس"],
    "automation":       ["أتمتة", "automation", "تلقائي"],
    "scraping":         ["سكرابينج", "scraping", "استخراج بيانات"],
}


class MatchEngine:

    def __init__(self):
        self.profile = self._load_profile()
        self.skills = [s.lower() for s in self.profile.get("skills", [])]
        self.title = self.profile.get("title", "").lower()

    # ── Load user profile ──────────────────────────────────────────
    def _load_profile(self) -> dict:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                config = json.loads(content) if content else {}
                return config.get("profile", {})
        return {}

    # ── Score a single gig ─────────────────────────────────────────
    def score(self, gig: dict) -> int:
        """Return a score from 0 to 100."""
        if not self.skills:
            return 0

        # Combine all gig text into one searchable string
        gig_text = " ".join([
            gig.get("title",       ""),
            gig.get("description", ""),
            " ".join(gig.get("tags", [])),
        ]).lower()

        skill_score = self._score_skills(gig_text)
        title_score = self._score_title(gig_text)
        density_score = self._score_density(gig_text)

        total = skill_score + title_score + density_score
        return min(100, int(total))

    # ── Component 1: Skill overlap (max 50 pts) ────────────────────
    def _score_skills(self, gig_text: str) -> float:
        if not self.skills:
            return 0

        matched = 0
        for skill in self.skills:
            # Get all Arabic + English forms of this skill
            forms = SKILL_ARABIC.get(skill, [skill])
            for form in forms:
                if re.search(r"\b" + re.escape(form) + r"\b", gig_text, re.IGNORECASE):
                    matched += 1
                    break   # count each skill once even if multiple forms match

        # Score proportionally — matching 3 out of 10 skills = 15 pts
        ratio = matched / len(self.skills)
        return ratio * 50

    # ── Component 2: Title relevance (max 30 pts) ──────────────────
    def _score_title(self, gig_text: str) -> float:
        if not self.title or self.title == "freelancer":
            return 0

        # Break title into meaningful words (skip short words)
        title_words = [
            w for w in re.split(r"\W+", self.title)
            if len(w) > 2
        ]
        if not title_words:
            return 0

        matched = sum(
            1 for w in title_words
            if re.search(r"\b" + re.escape(w) + r"\b", gig_text, re.IGNORECASE)
        )

        ratio = matched / len(title_words)
        return ratio * 30

    # ── Component 3: Keyword density (max 20 pts) ──────────────────
    def _score_density(self, gig_text: str) -> float:
        """
        Count total keyword hits across the gig text.
        More mentions = higher signal that the gig is relevant.
        Capped at 5 hits for full score.
        """
        if not self.skills:
            return 0

        total_hits = 0
        for skill in self.skills:
            forms = SKILL_ARABIC.get(skill, [skill])
            for form in forms:
                hits = len(re.findall(
                    r"\b" + re.escape(form) + r"\b",
                    gig_text,
                    re.IGNORECASE,
                ))
                total_hits += hits

        # 5+ hits = full 20 pts, scaled below that
        return min(20, (total_hits / 5) * 20)

    # ── Score all gigs from cache ──────────────────────────────────
    def score_all(self, progress_callback=None) -> list[dict]:
        """Load gigs from cache, score them, sort, save back."""
        if not os.path.exists(GIGS_CACHE_PATH):
            print("[match] No gigs cache found. Run scraper first.")
            return []

        with open(GIGS_CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)

        gigs = cache.get("gigs", [])
        total = len(gigs)

        if progress_callback:
            progress_callback(f"Scoring {total} gigs...")

        for i, gig in enumerate(gigs):
            gig["match_score"] = self.score(gig)
            if progress_callback and i % 10 == 0:
                progress_callback(f"Scoring... {i}/{total}")

        # Sort highest score first
        gigs.sort(key=lambda g: g["match_score"], reverse=True)

        # Save scored results back to cache
        cache["gigs"] = gigs
        with open(GIGS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

        if progress_callback:
            progress_callback(f"Scored {total} gigs.")

        return gigs
