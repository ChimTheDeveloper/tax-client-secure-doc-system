from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def classify_document(text):
    text = text.lower()

    if "w-2" in text:
        return "W2"
    elif "1099" in text:
        return "1099"
    elif "schedule c" in text:
        return "Schedule C" ## NTS: Update complete list of possible tax documents ASAP
    else:
        return "Unknown"
    
import re

def extract_basic_fields(text):
    data = {}
    
    ## SSN pattern
    ssn_match = re.search(r"\d{3}-\d{2}-\d{4}", text)
    if ssn_match:
        data["ssn"] = ssn_match.group()

    ## Income match
    income_match = re.search(r"\$?\d{1,3}(?:,\d{3})*", text)
    if income_match:
        data["income"] = income_match.group()

    return data

def process_document(file_path):
    text = extract_text_from_pdf(file_path)
    doc_type = classify_document(text)
    fields = extract_basic_fields(text)

    return {
        "document_type": doc_type,
        "extracted_fields": fields
    }