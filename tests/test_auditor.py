import pytest
import json
from unittest.mock import patch, MagicMock
from src.services.auditor import AIAuditorService
from src.models import AuditResult, HashtagCloud, TrendItem

@pytest.mark.asyncio
async def test_hashtag_cloud_builder():
    auditor = AIAuditorService(api_key="fake", model_name="test")
    
    # Mock GenAI response
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "top_hashtags": ["fidget", "toys"],
        "ai_summary": "Test summary"
    })
    
    with patch.object(auditor, "client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        
        trends = [
            TrendItem(description="Test video 1", views=100, hashtags=["fidget", "fun", "kids"]),
            TrendItem(description="Test video 2", views=200, hashtags=["fidget", "toys", "viral"]),
        ]
        
        cloud = await auditor.build_hashtag_cloud(trends, ["fidget"])
        
        assert "fidget" in cloud.top_hashtags
        assert cloud.ai_summary == "Test summary"
        assert cloud.hashtags["fidget"] == 2
        assert cloud.hashtags["toys"] == 1


@pytest.mark.asyncio
async def test_audit_parsing():
    auditor = AIAuditorService(api_key="fake", model_name="test")
    
    # Mock genai response
    mock_response = MagicMock()
    mock_response.text = '''```json
    {
        "ce_mark": true,
        "manufacturer_info": false,
        "lv_language": true,
        "age_restriction": false,
        "risk_summary": "Looks OK overall"
    }
    ```'''
    
    with patch.object(auditor, "client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        
        result = await auditor.audit("Some website text...")
        assert result is not None
        assert result.ce_mark is True
        assert result.manufacturer_info is False
        assert result.risk_summary == "Looks OK overall"
