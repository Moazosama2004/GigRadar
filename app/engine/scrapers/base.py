import requests
import time
import random
from abc import ABC, abstractmethod
from fake_useragent import UserAgent


class BaseScraper(ABC):

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.gigs = []

    # ── Headers that mimic a real browser ─────────────────────────
    def _get_headers(self) -> dict:
        return {
            "User-Agent":      self.ua.random,
            "Accept-Language": "ar,en;q=0.9",
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection":      "keep-alive",
        }

    # ── Polite delay between requests ─────────────────────────────
    def _wait(self):
        """Wait 2–4 seconds between requests so we don't get blocked."""
        time.sleep(random.uniform(2.0, 4.0))

    # ── Safe fetch with retries ────────────────────────────────────
    def _fetch(self, url: str, retries: int = 3) -> str | None:
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=15,
                )
                if response.status_code == 200:
                    response.encoding = "utf-8"
                    return response.text
                elif response.status_code == 429:
                    # Rate limited — wait longer and retry
                    print(f"[{self.source}] Rate limited. Waiting 30s...")
                    time.sleep(30)
                else:
                    print(f"[{self.source}] HTTP {response.status_code} on {url}")
                    return None
            except requests.RequestException as e:
                print(f"[{self.source}] Attempt {attempt + 1} failed: {e}")
                self._wait()
        return None

    # ── Interface every subclass MUST implement ────────────────────
    @property
    @abstractmethod
    def source(self) -> str:
        """Platform name e.g. 'mostaql'"""
        pass

    @abstractmethod
    def get_gigs(self, keywords: list[str]) -> list[dict]:
        """
        Fetch and return a list of normalized gig dicts.
        keywords: extracted from the user's resume profile.
        """
        pass

    # ── Normalized gig format ──────────────────────────────────────
    def _normalize(
        self,
        title:       str,
        budget:      str,
        description: str,
        tags:        list[str],
        url:         str,
        posted_at:   str,
    ) -> dict:
        """Every scraper calls this to return a consistent gig dict."""
        return {
            "title":       title.strip(),
            "budget":      budget.strip(),
            "description": description.strip(),
            "tags":        [t.lower().strip() for t in tags],
            "url":         url.strip(),
            "source":      self.source,
            "posted_at":   posted_at.strip(),
            "match_score": 0,       # filled later by match engine
        }
