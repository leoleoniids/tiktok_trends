import json
import re
from collections import Counter
from typing import Optional, List, Dict
from google import genai
from loguru import logger
from src.models import AuditResult, HashtagCloud, TrendItem


class AIAuditorService:
    """Service for AI safety audits and hashtag analysis using Google Gemini."""

    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    # -------------------------------------------------------------------------
    # Hashtag Cloud Analysis
    # -------------------------------------------------------------------------

    def _count_hashtags(self, trends: List[TrendItem]) -> Dict[str, int]:
        """Count hashtag frequency across all TikTok videos."""
        all_tags = []
        for trend in trends:
            all_tags.extend(trend.hashtags)
        return dict(Counter(all_tags).most_common(50))

    async def build_hashtag_cloud(
        self,
        trends: List[TrendItem],
        keywords: List[str],
    ) -> HashtagCloud:
        """
        Analyze hashtags from TikTok trends and build a smart hashtag cloud.
        Returns frequency counts + AI-recommended top hashtags for inspection.
        """
        logger.info("AIAuditor: building hashtag cloud from TikTok data")

        hashtag_counts = self._count_hashtags(trends)

        if not hashtag_counts:
            logger.warning("AIAuditor: No hashtags found in trends.")
            return HashtagCloud(
                hashtags={},
                top_hashtags=keywords,
                ai_summary="Netika atrasti heštagi TikTok datos. Meklēšanai izmantotas ievadītās atslēgvārdi."
            )

        # Format for AI
        tag_list = "\n".join(
            f"#{tag}: {count} video" for tag, count in list(hashtag_counts.items())[:30]
        )

        prompt = f"""
Tu esi PTAC (Patērētāju tiesību aizsardzības centra) datu analītiķis.
Tev ir jāanalizē TikTok heštagi, kas saistīti ar uzraudzāmajiem produktiem: {', '.join(keywords)}.

Zemāk ir biežāk izmantotie heštagi TikTok (formāts: #heštags: N video):
{tag_list}

Tava uzdevums:
1. Identificē 5-10 heštagus, kas visvairāk norāda uz potenciāli bīstamu/nelikumīgu produktu tirdzniecību.
2. Prioritizē heštagus, kas saistīti ar: nezināmiem brendiem, aizdomīgiem produktiem, izteikti komerciāliem videiem.
3. Ignorē vispārīgus heštagus (#fyp, #viral, #foryou, #xyzbca u.tml.) ja vien tie nav specifiskā kontekstā.

Atbildi TIKAI JSON formātā:
{{
  "top_hashtags": ["heshtags1", "heshtags2", ...],
  "ai_summary": "Īss apraksts latviski par šiem TikTok tendencēm un to riskiem (2-3 teikumi)."
}}
""".strip()

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            raw = (response.text or "").strip()
            payload = self._extract_json(raw)
            data = json.loads(payload)

            top = data.get("top_hashtags", [])
            summary = data.get("ai_summary", "")

            # Ensure top hashtags are clean (no #)
            top = [t.lstrip("#").lower() for t in top if t]

            return HashtagCloud(
                hashtags=hashtag_counts,
                top_hashtags=top,
                ai_summary=summary
            )
        except Exception as e:
            logger.error(f"HashtagCloud Error: {e}")
            # Fallback: return top by frequency
            top_fallback = list(hashtag_counts.keys())[:8]
            return HashtagCloud(
                hashtags=hashtag_counts,
                top_hashtags=top_fallback,
                ai_summary="AI analīze neizdevās. Rādīti biežākie heštagi pēc biežuma."
            )

    # -------------------------------------------------------------------------
    # Product Page Audit
    # -------------------------------------------------------------------------

    async def audit(self, page_content: str) -> Optional[AuditResult]:
        logger.info("AIAuditor: starting product page audit")

        prompt = f"""
Tu esi produktu atbilstības auditors PTAC vajadzībām.
Analizē zemāk esošo produkta lapas tekstu un atbildi TIKAI JSON formātā.

JSON atslēgas:
- ce_mark (bool): vai ir CE marķējums
- manufacturer_info (bool): vai ir ražotāja informācija
- lv_language (bool): vai lapa ir latviešu valodā
- age_restriction (bool): vai ir vecuma ierobežojums
- risk_summary (string): īss latvisks kopsavilkums par riskiem

Noteikumi:
- Ja informācija nav skaidri redzama, izmanto false.
- Neizdomā faktus. Atgriez tikai vienu JSON objektu.

Produkta lapas teksts:
{page_content[:3000]}
""".strip()

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            raw_text = (response.text or "").strip()
            payload = self._extract_json(raw_text)
            data = json.loads(payload)
            return AuditResult(**data)
        except Exception as e:
            logger.error(f"AIAuditor Error: {e}")
            return None

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group(0) if match else text
