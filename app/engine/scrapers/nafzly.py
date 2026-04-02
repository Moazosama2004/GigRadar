from bs4 import BeautifulSoup
from app.engine.scrapers.base import BaseScraper


class NaflzyScraper(BaseScraper):

    # Use key= parameter (confirmed from real HTML)
    BASE_URL = "https://nafezly.com/projects?search={keyword}&page={page}"

    @property
    def source(self) -> str:
        return "nafzly"

    def get_gigs(self, keywords: list[str]) -> list[dict]:
        gigs = []
        seen_urls = set()

        for keyword in keywords[:6]:
            print(f"[nafzly] Searching: {keyword}")
            for page in range(1, 3):
                url = self.BASE_URL.format(
                    keyword=keyword.replace(" ", "+"),
                    page=page,
                )
                html = self._fetch(url)
                if not html:
                    break

                page_gigs = self._parse(html)
                for gig in page_gigs:
                    if gig["url"] not in seen_urls:
                        seen_urls.add(gig["url"])
                        gigs.append(gig)

                self._wait()

        print(f"[nafzly] Found {len(gigs)} gigs total")
        return gigs

    def _parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        gigs = []

        # Real selector confirmed from HTML dump
        cards = soup.select("div.project-box")

        for card in cards:
            try:
                # Title + URL — the <a> inside the title div
                title_tag = card.select_one("a[href*='/project/']")
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                href = title_tag.get("href", "")
                url = href if href.startswith(
                    "http") else "https://nafezly.com" + href

                # Description — the h3 with class naskh
                desc_tag = card.select_one("h3.naskh")
                description = desc_tag.get_text(strip=True) if desc_tag else ""

                # Budget — span containing $ sign
                budget = "غير محدد"
                for span in card.select("span.kufi"):
                    text = span.get_text(strip=True)
                    if "$" in text:
                        budget = text
                        break

                # Posted time — look for clock icon parent
                posted_at = ""
                for span in card.select("span.kufi"):
                    text = span.get_text(strip=True)
                    if "منذ" in text or "ساعة" in text or "دقيقة" in text or "يوم" in text:
                        posted_at = text
                        break

                # No tags on Nafzly listing page — leave empty
                # They are only on the detail page
                tags = []

                gigs.append(self._normalize(
                    title=title,
                    budget=budget,
                    description=description,
                    tags=tags,
                    url=url,
                    posted_at=posted_at,
                ))

            except Exception as e:
                print(f"[nafzly] Card parse error: {e}")
                continue

        return gigs
