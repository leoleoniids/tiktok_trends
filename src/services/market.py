import httpx
from typing import List
from urllib.parse import urlparse
from loguru import logger
from src.services.base import BaseService
from src.models import MarketItem


from src.config import settings




class MarketScannerService(BaseService[MarketItem]):
    """Service to search Latvian market for actual product listings via Tavily API."""

    def __init__(self, api_key: str):
        super().__init__("MarketScanner")
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"

    def _is_valid_product_url(self, url: str) -> bool:
        """Returns True only if the URL looks like an actual product/store page."""
        url_lower = url.lower()
        parsed = urlparse(url_lower)
        domain = parsed.netloc.replace("www.", "")

        # Block comparison portals and news
        if any(blocked in domain for blocked in settings.blocked_domains):
            return False

        # Block search/category/tag pages
        full_url = parsed.path + ("?" + parsed.query if parsed.query else "")
        if any(pat in full_url for pat in settings.blocked_path_patterns):
            return False

        # Must have a meaningful path (not just homepage)
        if parsed.path in ["", "/"] or len(parsed.path) < 4:
            return False

        return True

    async def fetch(self, hashtag: str, max_results: int = 20) -> List[MarketItem]:
        """
        Search for actual product listings selling `hashtag` in Latvia.
        Filters out all comparison portals and irrelevant pages.
        """
        logger.info(f"MarketScanner: searching for product pages selling '{hashtag}'")

        # Targeted query: find actual Latvian shops selling this product
        # No quotes around hashtag so search engines can match variations
        query = f'{hashtag} pirkt cena site:.lv'

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "exclude_domains": settings.blocked_domains,
            "topic": "general",
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()

            results = []
            for result in data.get("results", []):
                url = result.get("url", "")
                snippet = result.get("content") or result.get("snippet") or ""
                title = result.get("title", "")

                if not self._is_valid_product_url(url):
                    logger.debug(f"MarketScanner: Skipping non-product URL: {url}")
                    continue

                results.append(MarketItem(url=url.lower(), snippet=snippet, title=title))

            logger.info(f"MarketScanner: {len(results)} valid product pages found (from {len(data.get('results', []))} raw results)")
            return results[:10]

        except Exception as e:
            logger.error(f"MarketScanner Error: {e}")
            return []
