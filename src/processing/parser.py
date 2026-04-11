from __future__ import annotations

import re


def classify_document_text(text: str) -> str:
    lowered_text = text.lower()
    if "w-2" in lowered_text:
        return "W2"
    if "1099" in lowered_text:
        return "1099"
    if "schedule c" in lowered_text:
        return "Schedule C"
    return "Unknown"


def extract_basic_fields(text: str) -> dict[str, str]:
    data: dict[str, str] = {}

    ssn_match = re.search(r"\d{3}-\d{2}-\d{4}", text)
    if ssn_match:
        data["ssn"] = ssn_match.group()

    income_match = re.search(r"\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?", text)
    if income_match:
        data["income"] = income_match.group()

    return data


def process_document(_file_bytes: bytes, raw_text_data: dict) -> dict[str, object]:
    if not raw_text_data or "Blocks" not in raw_text_data:
        return {"document_type": "Unknown", "extracted_fields": {}}

    blocks = raw_text_data.get("Blocks", [])
    full_text = " ".join(
        block.get("Text", "")
        for block in blocks
        if block.get("BlockType") == "WORD"
    )

    return {
        "document_type": classify_document_text(full_text),
        "extracted_fields": extract_basic_fields(full_text),
    }
