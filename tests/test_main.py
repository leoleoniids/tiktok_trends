import pytest

from main import PTACSentinel
from src.models import AuditResult, MarketItem


@pytest.mark.asyncio
async def test_run_audit_flow_calculates_risk_for_reports():
    sentinel = PTACSentinel()

    class FakeMarket:
        async def fetch(self, hashtag: str):
            return [
                MarketItem(
                    url="https://example.lv/produkts/test",
                    title="Test product",
                    snippet="Produkts bez skaidras atbilstības informācijas",
                )
            ]

    class FakeAuditor:
        async def audit(self, page_content: str):
            return AuditResult(
                ce_mark=False,
                manufacturer_info=False,
                lv_language=True,
                age_restriction=False,
                risk_summary="Trūkst vairākas būtiskas atbilstības pazīmes.",
            )

    sentinel.market = FakeMarket()
    sentinel.auditor = FakeAuditor()

    result = await sentinel.run_audit_flow("test", ["test"])

    assert len(result.reports) == 1
    assert result.reports[0].risk_score == 75
    assert result.top_risk_score == 75
