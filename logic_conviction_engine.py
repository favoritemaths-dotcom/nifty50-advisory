def conviction_check(
    rule_recommendation: str,
    rule_confidence: str,
    ai_response: str
):
    """
    Detects disagreement or weak conviction between
    rule-based engine and AI reasoning.
    """

    ai_text = ai_response.lower()

    caution_signals = [
        "risk",
        "uncertain",
        "concern",
        "downside",
        "headwind",
        "not comfortable",
        "could deteriorate",
        "watch closely",
        "dependent on",
        "sensitive to"
    ]

    caution_count = sum(1 for w in caution_signals if w in ai_text)

    # -------------------------------
    # DECISION LOGIC
    # -------------------------------
    if rule_recommendation == "BUY" and caution_count >= 3:
        return {
            "status": "⚠️ Weak Conviction",
            "message": (
                "Rule-based engine suggests BUY, "
                "but AI highlights multiple risks.\n\n"
                "This may be a false-confidence setup."
            )
        }

    if rule_recommendation in ["HOLD", "AVOID"] and "optional upside" in ai_text:
        return {
            "status": "🟡 Optional Opportunity",
            "message": (
                "AI sees selective upside despite conservative rules.\n\n"
                "Not a strong BUY, but worth monitoring."
            )
        }

    if rule_confidence == "Low":
        return {
            "status": "⚠️ Low Confidence",
            "message": (
                "Both rule confidence and AI conviction are weak.\n\n"
                "Avoid aggressive positioning."
            )
        }

    return {
        "status": "✅ Conviction Aligned",
        "message": (
            "Rule-based logic and AI judgment are broadly aligned."
        )
    }
