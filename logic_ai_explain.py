from logic_ai_memory import load_memory, save_to_memory
def ai_ask_why(
    question: str,
    recommendation: str,
    score: int,
    confidence: str,
    reasons: list,
    risk_profile: str,
    market: str = None,
    portfolio_mode: bool = False,
    identifier: str = "default"
):
    provider = get_ai_provider()

    mode = "portfolio" if portfolio_mode else "stock"
    memory = load_memory(mode, identifier)

    context = {
        "recommendation": recommendation,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
        "risk_profile": risk_profile,
        "market": market,
        "previous_questions": memory
    }

    answer = provider.explain_recommendation(
        question=question,
        context=context
    )

    save_to_memory(mode, identifier, question, answer)

    return answer
