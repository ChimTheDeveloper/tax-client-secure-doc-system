import boto3
import re

# Initialize client with the correct region for your S3 bucket
textract = boto3.client("textract", region_name="us-east-1")

def analyze_document_bytes(file_bytes):
    try:
        response = textract.analyze_document(
            Document={'Bytes': file_bytes},
            FeatureTypes=['FORMS', 'TABLES']
        )
        return response
    except Exception as e:
        print(f"Textract Error: {e}")
        return {}

def process_document(file_bytes):

    response = analyze_document_bytes(file_bytes)
    
    # 1. Create a map for lightning-fast lookups
    blocks = response.get("Blocks", [])
    id_map = {block["Id"]: block for block in blocks}
    
    # 2. Helper function to extract text from a block's children
    def get_text(result_block):
        text = ""
        if "Relationships" in result_block:
            for relationship in result_block["Relationships"]:
                if relationship["Type"] == "CHILD":
                    for child_id in relationship["Ids"]:
                        word_block = id_map.get(child_id)
                        if word_block and word_block["BlockType"] == "WORD":
                            text += word_block["Text"] + " "
        return text.strip()

    data = {}

    # 3. Loop through all blocks to find Key-Value pairs
    for block in blocks:
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            # Get the Key (e.g., "Social Security Number")
            key_text = get_text(block)
            value_text = ""

            # Find the associated Value block
            if "Relationships" in block:
                for rel in block["Relationships"]:
                    if rel["Type"] == "VALUE":
                        for value_id in rel["Ids"]:
                            value_block = id_map.get(value_id)
                            if value_block:
                                value_text = get_text(value_block)
            
            if key_text:
                data[key_text] = value_text

    # 4. Regex Fallback (Important for Tax Docs if Textract missed a label)
    # We grab all words to check for patterns like SSNs or Income totals
    full_text = " ".join([b["Text"] for b in blocks if b["BlockType"] == "WORD"])
    
    ssn_match = re.search(r"\d{3}-\d{2}-\d{4}", full_text)
    if ssn_match:
        data["Extracted_SSN"] = ssn_match.group()

    return data # Returns AFTER the loop is finished