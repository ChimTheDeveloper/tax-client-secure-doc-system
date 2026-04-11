from __future__ import annotations

import re


SSN_PATTERN = re.compile(r"^\d{3}-\d{2}-\d{4}$")
EIN_PATTERN = re.compile(r"^\d{2}-\d{7}$")
CURRENCY_PATTERN = re.compile(r"^\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?$|^\$?\d+(?:\.\d{2})?$")


def _score_formatted_value(value: str | None, pattern: re.Pattern[str]) -> str:
    if not value:
        return "low"
    if pattern.match(value.strip()):
        return "high"
    return "medium"


def _score_currency(value: str | None) -> str:
    if not value:
        return "low"
    if CURRENCY_PATTERN.match(value.strip()):
        return "high"
    return "medium"


def validate_w2_data(data: dict) -> tuple[dict, dict[str, str], list[str]]:
    validated = data.copy()
    confidence: dict[str, str] = {}
    warnings: list[str] = []

    confidence["employee_ssn"] = _score_formatted_value(data.get("employee_ssn"), SSN_PATTERN)
    if confidence["employee_ssn"] != "high":
        validated["employee_ssn"] = None
        warnings.append("Employee SSN is missing or malformed.")

    confidence["employer_ein"] = _score_formatted_value(data.get("employer_ein"), EIN_PATTERN)
    if confidence["employer_ein"] != "high":
        validated["employer_ein"] = None
        warnings.append("Employer EIN is missing or malformed.")

    confidence["wages_box_1"] = _score_currency(data.get("wages_box_1"))
    if confidence["wages_box_1"] != "high":
        validated["wages_box_1"] = None
        warnings.append("Box 1 wages are missing or malformed.")

    confidence["federal_tax_box_2"] = _score_currency(data.get("federal_tax_box_2"))
    if confidence["federal_tax_box_2"] != "high":
        validated["federal_tax_box_2"] = None
        warnings.append("Box 2 federal tax is missing or malformed.")

    return validated, confidence, warnings
