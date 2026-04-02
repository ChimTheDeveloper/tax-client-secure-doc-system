import re

def classify_document(text):
    text = text.lower()
    if "w-2" in text:
        return "W2"
    elif "1099" in text:
        return "1099"
    elif "schedule c" in text:
        return "Schedule C"
    return "Unknown"

def extract_basic_fields(text):
    data = {}
    # SSN pattern
    ssn_match = re.search(r"\d{3}-\d{2}-\d{4}", text)
    if ssn_match:
        data["ssn"] = ssn_match.group()

    # Income match - using the fix we discussed for your tax project
    income_match = re.search(r"\$?\d{1,3}(?:,\d{3})*", text)
    if income_match:
        data["income"] = income_match.group()
    return data

def process_document(file_bytes, raw_text_data):

    if not raw_text_data or "Blocks" not in raw_text_data:
        print("[ERROR] Parser received empty Textract data")
        return {"document_type": "Unknown", "extracted_fields": {}}
    
    blocks = raw_text_data.get("Blocks", [])

    full_text = ""
    # Use .get() to avoid crashing if Blocks is missing
    for block in blocks:
        if block["BlockType"] == "WORD":
            full_text += block["Text"] + " "

    # 1. Convert Textract blocks into a single string for your regex/logic
    full_text = ""
    for block in blocks:
        if block["BlockType"] == "WORD":
            full_text += block["Text"] + " "
    
    # 2. Use your existing logic on the extracted text
    doc_type = classify_document(full_text)
    fields = extract_basic_fields(full_text)

    return {
        "document_type": doc_type,
        "extracted_fields": fields
    }