import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.market import MarketScannerService
from src.models import MarketItem

@pytest.mark.asyncio
async def test_market_scanner_fetch_filters_invalid_urls():
    scanner = MarketScannerService(api_key="fake")
    
    mock_response_data = {
        "results": [
            {"url": "https://www.salidzini.lv/search?q=fidget", "title": "Salidzini - fidget", "content": "Comparison!"},
            {"url": "https://www.lsm.lv/zinas/fidget-toys", "title": "News - Fidget toys", "content": "News article"},
            {"url": "https://www.veikals.lv/produkti/fidget-toy-123", "title": "Veikals", "content": "Prc"},
            {"url": "https://veikals.lv/", "title": "Veikals Home", "content": "Home"}
        ]
    }
    
    # We patch httpx.AsyncClient.post to return a mock response
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response_data
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        
        results = await scanner.fetch("fidget toy")
        
        # Only the valid product url should remain
        assert len(results) == 1
        assert "veikals.lv/produkti" in results[0].url
        assert results[0].title == "Veikals"
