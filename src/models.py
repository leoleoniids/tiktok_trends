from __future__ import annotations

from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field


class TrendItem(BaseModel):
    """Represents a discovered trend from TikTok."""
    model_config = ConfigDict(frozen=True)

    description: str = Field(..., description="Video description or caption")
    views: int = Field(default=0, ge=0, description="Number of video views")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags extracted from the description")


class HashtagCloud(BaseModel):
    """Represents the analyzed hashtag cloud from TikTok trends."""
    model_config = ConfigDict(frozen=True)

    hashtags: Dict[str, int] = Field(
        default_factory=dict,
        description="Hashtag -> frequency/weight mapping"
    )
    top_hashtags: List[str] = Field(
        default_factory=list,
        description="Top hashtags recommended by AI for inspection"
    )
    ai_summary: str = Field(
        default="",
        description="AI explanation of the hashtag landscape"
    )


class MarketItem(BaseModel):
    """Represents a product found in the local market."""
    model_config = ConfigDict(frozen=True)

    url: str = Field(..., description="URL of the product page")
    snippet: str = Field(default="", description="Text content context from the page")
    title: Optional[str] = Field(None, description="Title of the page")


class AuditResult(BaseModel):
    """Represents the AI-driven safety audit of a product."""
    model_config = ConfigDict(frozen=True)

    ce_mark: bool = Field(default=False, description="Whether a CE mark was detected")
    manufacturer_info: bool = Field(default=False, description="Whether manufacturer info was found")
    lv_language: bool = Field(default=False, description="Whether the content is in Latvian")
    age_restriction: bool = Field(default=False, description="Whether age restrictions were found")
    risk_summary: str = Field(default="Nav kopsavilkuma", description="Detailed AI audit text")


class ReportItem(BaseModel):
    """The final processed report for a specific store/product."""
    model_config = ConfigDict(frozen=True)

    url: str
    title: Optional[str] = None
    audit: AuditResult
    risk_score: int = Field(..., ge=0, le=100)


class PipelineResult(BaseModel):
    """Result of the full sentinel pipeline."""
    model_config = ConfigDict(frozen=True)

    keywords: List[str]
    hashtag_used: str
    total_trends: int
    hashtag_cloud: Optional[HashtagCloud] = None
    reports: List[ReportItem]
    top_risk_score: int


class TrendProduct(BaseModel):
    """Represents a discovered trending product."""
    product_name: str
    category: str
    short_description: str
    why_trending: str
    example_keywords: List[str]
    source_urls: List[str]


class DiscoverTrendsRequest(BaseModel):
    category: str


class DiscoverTrendsResponse(BaseModel):
    category: str
    generated_at: str
    trends: List[TrendProduct]

