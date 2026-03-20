from typing import List
import re
from apify_client import ApifyClient
from loguru import logger
from src.services.base import BaseService
from src.models import TrendItem


class TikTokService(BaseService[TrendItem]):
    """Service to handle TikTok trend discovery via Apify.
    
    Searches TikTok by KEYWORD (not hashtag), pulls top N videos,
    and extracts all hashtags from their descriptions.
    """

    def __init__(self, token: str):
        super().__init__("TikTok")
        self.client = ApifyClient(token)

    @staticmethod
    def _extract_hashtags(text: str) -> List[str]:
        """Extract all #hashtags from a text string."""
        return [tag.lower().lstrip("#") for tag in re.findall(r"#\w+", text)]

    async def fetch_by_keyword(self, keyword: str, limit: int = 20) -> List[TrendItem]:
        """
        Search TikTok for videos matching a keyword.
        Returns top `limit` videos with their extracted hashtags.
        """
        logger.info(f"TikTokService: searching keyword '{keyword}' (top {limit} videos)")
        try:
            run_input = {
                "searchQueries": [keyword],   # correct field name for clockworks/tiktok-scraper
                "resultsPerPage": limit,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False,
                "shouldDownloadSubtitles": False,
            }

            run = self.client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
            dataset_id = run.get("defaultDatasetId")

            if not dataset_id:
                logger.warning("TikTokService: No dataset returned.")
                return []

            items = []
            for item in self.client.dataset(dataset_id).iterate_items():
                stats = item.get("stats", {}) or {}
                desc = item.get("desc") or item.get("text") or ""
                views = int(stats.get("playCount", item.get("playCount", 0)) or 0)
                hashtags = self._extract_hashtags(desc)
                items.append(TrendItem(description=desc, views=views, hashtags=hashtags))

            logger.info(f"TikTokService: Found {len(items)} videos for '{keyword}'.")
            return items

        except Exception as e:
            logger.error(f"TikTokService Error: {e}")
            return []

    async def fetch(self, hashtag: str, limit: int = 20) -> List[TrendItem]:
        """Legacy method — searches by hashtag. Used in audit flow."""
        return await self.fetch_by_keyword(hashtag, limit)
