
def map_textract_to_tax_fields(textract_response):
    fields = {}

    for block in textract_response.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            text = block.get("Text", "").lower()

            if "employer" in text:
                fields["employer"] = text

            elif "wages" in text or "income" in text:
                fields["income"] = text

    return fields