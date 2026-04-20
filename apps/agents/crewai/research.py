from __future__ import annotations

from html import unescape
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from django.conf import settings

from api.schemas import ContentGenerationRequest, ResearchBundle, ResolvedTopic

BLOCKED_DOMAINS = {
    "reddit.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "imdb.com",
}


class ResearchCollector:
    def __init__(self, service_settings=None) -> None:
        self.settings = service_settings or settings
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": getattr(self.settings, "USER_AGENT", "Mozilla/5.0")})

    def build_bundle(
        self,
        request: ContentGenerationRequest,
        resolved_topic: ResolvedTopic,
    ) -> ResearchBundle:
        source_urls = [str(url) for url in request.source_urls]
        research_blocks: list[str] = []

        if resolved_topic.additional_context:
            research_blocks.append(f"Topic context:\n{resolved_topic.additional_context}")

        if request.research_text:
            research_blocks.append(f"Provided research:\n{request.research_text.strip()}")

        if source_urls:
            research_blocks.extend(self._scrape_urls(source_urls))
        elif request.search_enabled and resolved_topic.topic:
            discovered_urls = self._search_google_cse(resolved_topic.topic)
            source_urls.extend(discovered_urls)
            research_blocks.extend(self._scrape_urls(discovered_urls))

        if not research_blocks:
            research_blocks.append(
                "No external research was provided. Use common knowledge carefully, avoid "
                "specific unverifiable claims, and keep the article practical."
            )

        combined_research = "\n\n".join(research_blocks).strip()
        return ResearchBundle(
            topic=resolved_topic.topic,
            research_text=combined_research,
            source_urls=source_urls,
            source_count=len(source_urls),
        )

    def check_ollama(self) -> bool:
        try:
            response = self._session.get(
                f"{self.settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags",
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def _search_google_cse(self, topic: str) -> list[str]:
        api_key = getattr(self.settings, "GOOGLE_CSE_API_KEY", None)
        cse_id = getattr(self.settings, "GOOGLE_CSE_ID", None)
        if not api_key or not cse_id:
            return []

        query = quote_plus(topic)
        search_url = (
            "https://www.googleapis.com/customsearch/v1"
            f"?q={query}&key={api_key}&cx={cse_id}&num={getattr(self.settings, 'MAX_SEARCH_RESULTS', 5)}"
        )
        try:
            response = self._session.get(
                search_url,
                timeout=getattr(self.settings, 'REQUEST_TIMEOUT_SECONDS', 45),
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException:
            return []

        urls: list[str] = []
        for item in payload.get("items", []):
            link = item.get("link")
            if not link or any(domain in link for domain in BLOCKED_DOMAINS):
                continue
            if link not in urls:
                urls.append(link)
        return urls[: getattr(self.settings, 'MAX_SCRAPE_SOURCES', 4)]

    def _scrape_urls(self, urls: list[str]) -> list[str]:
        scraped_blocks: list[str] = []
        for url in urls[: getattr(self.settings, 'MAX_SCRAPE_SOURCES', 4)]:
            try:
                response = self._session.get(
                    url,
                    timeout=getattr(self.settings, 'REQUEST_TIMEOUT_SECONDS', 45),
                )
                response.raise_for_status()
            except requests.RequestException:
                continue

            text_content = self._extract_text(response.text)
            if len(text_content.split()) < 80:
                continue

            text_content = text_content[: getattr(self.settings, 'MAX_CHARS_PER_SOURCE', 6000)]
            scraped_blocks.append(f"Source URL: {url}\n{text_content}")
        return scraped_blocks

    @staticmethod
    def _extract_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        main = soup.find("article") or soup.find("main") or soup.body or soup
        text = main.get_text(separator="\n", strip=True)
        lines = [unescape(line.strip()) for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
