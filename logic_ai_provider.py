# logic_ai_provider.py
# =========================================================
# AUTO AI PROVIDER
# - Uses Gemini if available (FREE)
# - Falls back safely to rule-based explanation
# - NEVER crashes the app
# =========================================================

import os
import json

# ---------------------------------------------------------
# Gemini SDK (safe import)
# ---------------------------------------------------------
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False


# =========================================================
# FALLBACK PROVIDER (Rule-based explanation)
# =========================================================

class FallbackAIProvider:
    """
    Used when:
    - Gemini API key missing
    - Gemini quota exceeded
    - Any AI error occurs
    """

    def explain_recommendation(self, system_rules, question, context):
        rb = context.get("rule_based_summary", {})

        lines = []
        lines.append("### 🧠 AI Advisor (Rule-Based Fallback)")
        lines.append("")
        lines.append("⚠️ External AI unavailable. Showing disciplined fallback analysis.")
        lines.append("")
        lines.append("#### 1️⃣ Rule-Based Summary")
        lines.append(f"- Recommendation: **{rb.get('recommendation')}**")
        lines.append(f"- Score: **{rb.get('score')} / 100**")
        lines.append(f"- Confidence: **{rb.get('confidence')}**")
        lines.append(f"- Risk Profile: **{rb.get('risk_profile')}**")

        if rb.get("reasons"):
            lines.append("")
            lines.append("#### 2️⃣ Key Supporting Factors")
            for r in rb["reasons"]:
                lines.append(f"• {r}")

        lines.append("")
        lines.append("#### 3️⃣ AI Judgment")
        lines.append(
            "Based on available quantitative and rule-based signals, "
            "the recommendation appears internally consistent. "
            "However, absence of live qualitative AI analysis means "
            "macro, management quality, and narrative risks may not be fully captured."
        )

        lines.append("")
        lines.append("#### 4️⃣ What to Watch")
        lines.append("• Earnings consistency")
        lines.append("• Valuation expansion or compression")
        lines.append("• Market regime changes")

        return "\n".join(lines)


# =========================================================
# GEMINI PROVIDER
# =========================================================

class GeminiAIProvider:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not found")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def explain_recommendation(self, system_rules, question, context):
        prompt = f"""
{system_rules}

========================
CONTEXT (JSON)
========================
{json.dumps(context, indent=2)}

========================
USER QUESTION
========================
{question}

========================
INSTRUCTIONS
========================
Respond clearly using this structure:

1. Rule-Based Summary
2. Independent AI Assessment
3. Risks Possibly Underestimated
4. Signals Possibly Overlooked
5. What I Would Watch Going Forward

Be conservative. Be honest. Avoid false certainty.
"""

        response = self.model.generate_content(prompt)

        return response.text


# =========================================================
# PROVIDER SELECTOR (AUTO MODE)
# =========================================================

def get_ai_provider():
    """
    AUTO mode:
    - Try Gemini
    - If anything fails → fallback provider
    """

    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        try:
            return GeminiAIProvider()
        except Exception:
            pass

    return FallbackAIProvider()
