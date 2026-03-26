from __future__ import annotations

import asyncio
from typing import List
from loguru import logger

from src.config import settings
from src.models import PipelineResult, ReportItem, TrendItem, HashtagCloud
from src.services.tiktok import TikTokService
from src.services.market import MarketScannerService
from src.services.auditor import AIAuditorService
import json
from datetime import date
from openai import AsyncOpenAI


class PTACSentinel:
    """
    PTAC Sentinel — main orchestrator.

    Flow:
    1. fetch_tiktok_trends(keywords)  -> List[TrendItem] + HashtagCloud
    2. run_audit_flow(hashtag, keywords) -> PipelineResult
    """

    def __init__(self):
        self.tiktok = TikTokService(settings.apify_token) if settings.apify_token else None
        self.market = MarketScannerService(settings.tavily_api_key) if settings.tavily_api_key else None
        self.auditor = AIAuditorService(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model_audit
        ) if settings.gemini_api_key else None
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    # ------------------------------------------------------------------
    # Phase 1: TikTok Discovery + Hashtag Cloud
    # ------------------------------------------------------------------

    async def fetch_tiktok_trends(self, keywords: List[str], limit: int = 20) -> tuple[List[TrendItem], HashtagCloud | None]:
        """
        Search TikTok for each keyword in parallel, collect all videos,
        then build a hashtag cloud from everything found.

        Returns (all_trends, hashtag_cloud)
        """
        if not self.tiktok:
            logger.warning("TikTok service not configured (no APIFY token).")
            return [], None

        logger.info(f"PTACSentinel: fetching Top {limit} TikTok trends for keywords: {keywords}")

        # Parallel search for all keywords
        tasks = [self.tiktok.fetch_by_keyword(kw, limit=limit) for kw in keywords]
        results = await asyncio.gather(*tasks)

        all_trends: List[TrendItem] = []
        for trend_list in results:
            all_trends.extend(trend_list)

        logger.info(f"PTACSentinel: collected {len(all_trends)} total TikTok videos across {len(keywords)} keywords")

        # Build hashtag cloud with AI analysis
        cloud = None
        if self.auditor and all_trends:
            cloud = await self.auditor.build_hashtag_cloud(all_trends, keywords)

        return all_trends, cloud

    # ------------------------------------------------------------------
    # Phase 2: Market Audit for a chosen hashtag
    # ------------------------------------------------------------------

    async def run_audit_flow(self, hashtag: str, keywords: List[str]) -> PipelineResult:
        """
        Given a chosen hashtag (from the hashtag cloud), search the Latvian market
        for product listings and audit each one with AI.
        """
        logger.info(f"PTACSentinel: running audit for #{hashtag}")

        # Fetch market listings (excluding comparison portals)
        market_data = []
        if self.market:
            market_data = await self.market.fetch(hashtag)
        
        # AI audit each product page in parallel
        reports: List[ReportItem] = []
        if self.auditor and market_data:
            audit_tasks = [self.auditor.audit(site.snippet) for site in market_data]
            audit_results = await asyncio.gather(*audit_tasks)

            for site, audit_res in zip(market_data, audit_results):
                if not audit_res:
                    continue
                score = self._calculate_risk(audit_res)
                reports.append(ReportItem(
                    url=site.url,
                    title=site.title,
                    audit=audit_res,
                    risk_score=score
                ))

        top_score = max((r.risk_score for r in reports), default=0)

        return PipelineResult(
            keywords=keywords,
            hashtag_used=hashtag,
            total_trends=0,  # Already shown in phase 1
            hashtag_cloud=None,
            reports=reports,
            top_risk_score=top_score
        )

    # ------------------------------------------------------------------
    # Category Trends Discovery (OpenAI)
    # ------------------------------------------------------------------

    async def discover_category_trends(self, category: str) -> "DiscoverTrendsResponse":
        from src.models import DiscoverTrendsResponse, TrendProduct
        if not self.openai_client:
            raise ValueError("OpenAI API atslēga nav konfigurēta.")
            
        today = date.today().isoformat()
        
        system_prompt = f"""
You are a trend discovery assistant for a consumer protection workflow used by PTAC.

Today's date is: {today}.

Your task:
Find exactly 5 currently emerging product trends for the category: "{category}".

Important context:
- PTAC is interested in real consumer products that may become relevant for market monitoring.
- Focus on concrete products or product types, not broad lifestyle themes, aesthetics, or abstract topics.
- The output will later be used for TikTok and web investigation, so results must be specific and searchable.

Requirements:
1. Use web search to identify recent and currently emerging product trends.
2. Prefer trends that show signs of recent popularity growth, media attention, social discussion, marketplace visibility, or repeated mention across multiple sources.
3. Focus on actual products that consumers can buy or search for.
4. Avoid vague trends such as "self-care", "minimalism", "viral gadgets" unless they clearly refer to a concrete product.
5. Avoid duplicates, near-duplicates, and overly broad category labels.
6. If possible, prioritize products that are relevant to e-commerce, social platforms, or viral consumer behavior.
7. Use multiple sources when available.
8. Return exactly 5 results.
9. Return only valid JSON. Do not include markdown, explanations, notes, or any text outside the JSON array.

For each result, return an object with this exact structure:
{{
  "product_name": "string",
  "category": "string",
  "short_description": "string",
  "why_trending": "string",
  "example_keywords": ["string", "string", "string"],
  "source_urls": ["string", "string"]
}}

Field rules:
- product_name: a concrete and searchable product or product-type name.
- category: repeat the input category or a closely matching subcategory.
- short_description: one short factual description of the product.
- why_trending: short explanation of why it appears to be trending now.
- example_keywords: 3 to 6 practical search phrases or keywords that can be used in TikTok or web search.
- source_urls: 1 to 3 URLs used to support the trend.

Quality bar:
- Prefer precision over hype.
- Prefer concrete product names over generic trend labels.
- Do not invent products, popularity signals, or URLs.
- If evidence is weak, choose the most plausible concrete product with the strongest available support.

Return exactly one JSON array with 5 objects.
"""

        logger.info(f"PTACSentinel: discovering trends for category: {category}")
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Kategorija: {category}"}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            # Remove markdown if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip(" \n`")
            
            data = json.loads(content)
            if not isinstance(data, list):
                if isinstance(data, dict) and "trends" in data:
                    data = data["trends"]
                else:
                    raise ValueError("Atbilde nav JSON masīvs.")
            
            # Validate and format
            trends = []
            for item in data[:5]:
                trends.append(TrendProduct(
                    product_name=item.get("product_name", "Nezināms produkts"),
                    category=item.get("category", category),
                    short_description=item.get("short_description", ""),
                    why_trending=item.get("why_trending", ""),
                    example_keywords=item.get("example_keywords", []),
                    source_urls=item.get("source_urls", [])
                ))
            
            return DiscoverTrendsResponse(
                category=category,
                generated_at=today,
                trends=trends
            )
            
        except Exception as e:
            logger.error(f"Kļūda iegūstot trendus: {e}")
            raise ValueError("Neizdevās iegūt strukturētus trendu datus.")

    # ------------------------------------------------------------------
    # Risk Scoring
    # ------------------------------------------------------------------

    def _calculate_risk(self, audit_result) -> int:
        """
        Calculate a simple deterministic risk score from audit findings.

        Missing compliance signals increase risk. Presence of an age restriction
        lowers risk slightly because it indicates at least some safety labeling.
        """
        score = 0

        if not audit_result.ce_mark:
            score += 35
        if not audit_result.manufacturer_info:
            score += 25
        if not audit_result.lv_language:
            score += 25
        if not audit_result.age_restriction:
            score += 15
        else:
            score -= 5

        return max(0, min(100, score))

    # ------------------------------------------------------------------
    # Risk Scoring
    # ------------------------------------------------------------------
