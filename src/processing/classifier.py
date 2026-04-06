def classify_document(textract_response):

    text_blob = ""

    for block in textract_response.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            text_blob += block.get("Text", "").lower() + " "

    # W-2 KEY SIGNALS
    signals = [
        "w-2",
        "wage and tax statement",
        "employer identification number",
        "social security wages",
        "medicare wages"
    ]

    score = sum(1 for signal in signals if signal in text_blob)

    if score >= 2:
        return "W2"

    return "UNKNOWN"