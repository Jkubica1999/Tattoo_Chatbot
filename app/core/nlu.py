def parse_message(text: str) -> dict:
    """Naive placeholder. Replace with real LLM tool-calling parser later."""
    t = (text or "").lower()
    style = "Fine-line" if "fine" in t else "Realism" if "realism" in t else None
    placement = "Ribs" if "rib" in t else "Forearm" if "forearm" in t else None
    color = "Color" if "color" in t else "Black & grey" if "black" in t else None
    size_band = "6–10cm" if any(k in t for k in ["palm","8cm","6-10","6–10"]) else None
    return {"style": style, "placement": placement, "color": color, "size_band": size_band, "confidence": 0.5}
