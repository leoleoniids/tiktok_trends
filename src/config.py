from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """System settings and API keys."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys
    apify_token: Optional[str] = Field(default=None, alias="apify_api_key", validation_alias="APIFY_API_KEY")
    tavily_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    serp_api_key: Optional[str] = Field(default=None, validation_alias="SERP_API_KEY")
    openai_api_key: Optional[str] = None

    # Gemini Models — flash ir ātrāks un lētāks, pro tiek izmantots tikai auditiem
    gemini_model_audit: str = "gemini-2.0-flash"
    gemini_model_discovery: str = "gemini-2.0-flash"

    # Business Logic
    risk_threshold: int = 70
    blocked_domains: list[str] = [
        "salidzini.lv", "kurpirkt.lv", "lv.bestshopping.com", "shopmania.lv",
        "cena.lv", "pricespy.lv", "pricesearch.lv", "skruverts.lv",
        "delfi.lv", "lsm.lv", "tvnet.lv", "jauns.lv", "la.lv", "apollo.lv",
        "db.lv", "diena.lv", "nra.lv",
        "facebook.com", "instagram.com", "tiktok.com", "youtube.com",
        "twitter.com", "x.com", "linkedin.com", "pinterest.com",
        "amazon.com", "amazon.de", "ebay.com", "aliexpress.com",
        "wikipedia.org", "bbc.com", "reddit.com",
    ]
    blocked_path_patterns: list[str] = [
        "?q=", "?query=", "?search=", "?s=", "?keyword=",
        "/search", "/meklet", "/search-results", "/cena?", "/cena.php",
        "/kategorija", "/category", "/cat=", "/tag/",
        "/blog/", "/raksts/", "/zinas/", "/news/",
    ]


# Global settings instance
settings = Settings()
