import re

def normalize_currency(value):
    if not value:
        return None

    # Remove $ and commas
    cleaned = value.replace("$", "").replace(",", "").strip()

    try:
        return float(cleaned)
    except:
        return None


def normalize_ssn(value):
    if not value:
        return None

    # Extract digits only
    digits = re.sub(r"\D", "", value)

    if len(digits) == 9:
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    
    return None


def normalize_ein(value):
    if not value:
        return None

    digits = re.sub(r"\D", "", value)

    if len(digits) == 9:
        return f"{digits[:2]}-{digits[2:]}"
    
    return None


def normalize_w2_data(data):
    normalized = data.copy()

    normalized["wages_box_1"] = normalize_currency(data.get("wages_box_1"))
    normalized["federal_tax_box_2"] = normalize_currency(data.get("federal_tax_box_2"))
    normalized["ss_wages_box_3"] = normalize_currency(data.get("ss_wages_box_3"))
    normalized["ss_tax_box_4"] = normalize_currency(data.get("ss_tax_box_4"))
    normalized["medicare_wages_box_5"] = normalize_currency(data.get("medicare_wages_box_5"))
    normalized["medicare_tax_box_6"] = normalize_currency(data.get("medicare_tax_box_6"))

    normalized["employee_ssn"] = normalize_ssn(data.get("employee_ssn"))
    normalized["employer_ein"] = normalize_ein(data.get("employer_ein"))

    return normalized