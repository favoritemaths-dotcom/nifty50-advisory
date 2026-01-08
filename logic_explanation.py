def generate_explanation(stock, score, rec, reasons, risk, horizon):
    text=[f"### AI View – {stock}",
          f"Score: {score}/100",
          f"Recommendation: {rec}",
          f"Risk Profile: {risk}, Horizon: {horizon}",
          "Key Reasons:"]
    for r in reasons:
        text.append(f"- {r}")
    return "\n".join(text)
