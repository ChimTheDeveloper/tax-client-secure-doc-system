from __future__ import annotations


FIELD_WEIGHTS = {
    "employee_ssn": 0.30,
    "employer_ein": 0.25,
    "wages_box_1": 0.25,
    "federal_tax_box_2": 0.20,
}

CONFIDENCE_VALUES = {
    "high": 1.0,
    "medium": 0.5,
    "low": 0.0,
}


def calculate_confidence(
    data: dict,
    field_confidence: dict[str, str] | None = None,
) -> float:
    if field_confidence:
        weighted_score = 0.0
        total_weight = 0.0

        for field_name, weight in FIELD_WEIGHTS.items():
            total_weight += weight
            confidence_label = field_confidence.get(field_name, "low")
            weighted_score += CONFIDENCE_VALUES.get(confidence_label, 0.0) * weight

        return round(weighted_score / total_weight, 2) if total_weight else 0.0

    score = sum(1 for field_name in FIELD_WEIGHTS if data.get(field_name))
    return round(score / len(FIELD_WEIGHTS), 2)
