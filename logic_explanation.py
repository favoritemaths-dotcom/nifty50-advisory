def generate_explanation(stock, score, rec, reasons, risk_profile, time_horizon):
    text = []
    text.append(f"### 🤖 AI Advisory View – {stock}")
    text.append(f"**Score:** {score}/100")
    text.append(f"**Recommendation:** {rec}")
    text.append(f"**Risk Profile:** {risk_profile}")
    text.append(f"**Investment Horizon:** {time_horizon}")
    if reasons:
        text.append("#### Key Factors:")
        for r in reasons:
            text.append(f"• {r}")
    text.append("_This is a rule-based advisory insight, not financial advice._")
    return "\n\n".join(text)
