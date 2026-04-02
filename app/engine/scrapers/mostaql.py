from bs4 import BeautifulSoup
from app.engine.scrapers.base import BaseScraper


class MostaqlScraper(BaseScraper):

    BASE_URL = "https://mostaql.com/projects?category=&budget_max=&skills=&q={keyword}&page={page}"

    @property
    def source(self) -> str:
        return "mostaql"

    def get_gigs(self, keywords: list[str]) -> list[dict]:
        gigs = []
        seen_urls = set()       # avoid duplicates across keyword searches

        for keyword in keywords[:5]:    # limit to 5 keywords per scan
            print(f"[mostaql] Searching: {keyword}")
            for page in range(1, 3):    # pages 1 and 2 only
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

        print(f"[mostaql] Found {len(gigs)} gigs total")
        return gigs

    def _parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        gigs = []

        # Each project is in a <tr> with class "project-row"
        rows = soup.select("tr.project-row")

        for row in rows:
            try:
                # Title and URL
                title_tag = row.select_one("h3.project__title a")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                url = "https://mostaql.com" + title_tag.get("href", "")

                # Budget
                budget_tag = row.select_one(".project-meta--budget")
                budget = budget_tag.get_text(
                    strip=True) if budget_tag else "غير محدد"

                # Description
                desc_tag = row.select_one(".project__brief")
                description = desc_tag.get_text(strip=True) if desc_tag else ""

                # Tags / skills
                tag_els = row.select(".skills-list a")
                tags = [t.get_text(strip=True) for t in tag_els]

                # Posted time
                time_tag = row.select_one("time")
                posted_at = time_tag.get("title", "") if time_tag else ""

                gigs.append(self._normalize(
                    title=title,
                    budget=budget,
                    description=description,
                    tags=tags,
                    url=url,
                    posted_at=posted_at,
                ))
            except Exception as e:
                print(f"[mostaql] Row parse error: {e}")
                continue

        return gigs
