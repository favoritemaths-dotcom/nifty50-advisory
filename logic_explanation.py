def generate_explanation(stock, score, rec, reasons, profile, horizon):
    text = []
    text.append(f"### 🤖 AI Advisory – {stock}")
    text.append(f"Score: **{score}/100**")
    text.append(f"Recommendation: **{rec}**")
    text.append("")
    text.append("#### Key Factors:")

    for r in reasons:
        text.append(f"• {r}")

    text.append("")
    text.append(
        f"Aligned with **{profile}** risk profile over **{horizon}** horizon."
    )

    text.append("_Rule-based decision support, not financial advice._")

    return "\n".join(text)
