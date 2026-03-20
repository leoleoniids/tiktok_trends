from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from loguru import logger

from src.config import settings
from src.models import DiscoverTrendsRequest, DiscoverTrendsResponse
from main import PTACSentinel

app = FastAPI(title="PTAC Sentinel API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://tiktok-trends-ptac.example.com"  # FIXME: Nomainīt uz īsto produkcijas domēnu
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Single long-lived sentinel instance
sentinel = PTACSentinel()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    keywords: List[str]
    limit: int = 20


class AuditRequest(BaseModel):
    hashtag: str
    keywords: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "apis": {
            "apify": bool(settings.apify_token),
            "tavily": bool(settings.tavily_api_key),
            "gemini": bool(settings.gemini_api_key),
        }
    }


@app.post("/api/scan")
async def scan_tiktok(req: ScanRequest):
    """
    Phase 1: Search TikTok by keywords, return a hashtag cloud.
    """
    if not req.keywords:
        raise HTTPException(status_code=400, detail="Vismaz viens atslēgas vārds ir obligāts.")

    logger.info(f"API /scan: keywords={req.keywords}, limit={req.limit}")
    trends, cloud = await sentinel.fetch_tiktok_trends(req.keywords, limit=req.limit)

    return {
        "total_videos": len(trends),
        "hashtag_cloud": cloud.model_dump() if cloud else None,
    }


@app.post("/api/audit")
async def audit_market(req: AuditRequest):
    """
    Phase 2: Search Latvian market for the chosen hashtag and AI-audit each listing.
    """
    if not req.hashtag:
        raise HTTPException(status_code=400, detail="Heštags ir obligāts.")

    logger.info(f"API /audit: hashtag={req.hashtag}, keywords={req.keywords}")
    result = await sentinel.run_audit_flow(req.hashtag, req.keywords)
    return result.model_dump()


@app.post("/api/trends/discover", response_model=DiscoverTrendsResponse)
async def discover_trends(req: DiscoverTrendsRequest):
    """
    Phase 0: Discover top 5 trends by category using OpenAI.
    """
    if not req.category:
        raise HTTPException(status_code=400, detail="Kategorija ir obligāta.")
        
    try:
        response = await sentinel.discover_category_trends(req.category)
        return response
    except Exception as e:
        logger.error(f"API /trends/discover error: {e}")
        # Try 1 retry as fallback per requirements
        try:
            logger.info("Retrying discovery...")
            response = await sentinel.discover_category_trends(req.category)
            return response
        except Exception as retry_e:
            raise HTTPException(status_code=500, detail=str(retry_e))
