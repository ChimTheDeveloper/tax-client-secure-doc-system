import re

def split_name_address(full_text):

    if not full_text:
        return None, None

    parts = full_text.split()

    # Heuristic: name is first 2–4 words, rest is address
    name_parts = parts[:4]
    address_parts = parts[4:]

    name = " ".join(name_parts)
    address = " ".join(address_parts)

    return name.strip(), address.strip()

def map_textract_to_tax_fields(response):
    raw_text = ""

    for block in response.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            raw_text += block.get("Text", "") + "\n"

    blocks = response.get("Blocks", [])

    block_map = {block["Id"]: block for block in blocks}
    key_map = {}
    value_map = {}

    for block in blocks:
        if block["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in block.get("EntityTypes", []):
                key_map[block["Id"]] = block
            elif "VALUE" in block.get("EntityTypes", []):
                value_map[block["Id"]] = block

    def get_text(block):
        text = ""
        if "Relationships" in block:
            for rel in block["Relationships"]:
                if rel["Type"] == "CHILD":
                    for child_id in rel["Ids"]:
                        word = block_map.get(child_id)
                        if word and word["BlockType"] == "WORD":
                            text += word["Text"] + " "
        return text.strip()

    def find_value_block(key_block):
        if "Relationships" in key_block:
            for rel in key_block["Relationships"]:
                if rel["Type"] == "VALUE":
                    for value_id in rel["Ids"]:
                        return value_map.get(value_id)
        return None

    # TARGET STRUCTURE
    extracted = {
        "employee_ssn": None,
        "employer_ein": None,
        "employer_name": None,
        "employer_address": None,
        "employee_name": None,
        "employee_address": None,

        "wages_box_1": None,
        "federal_tax_box_2": None,
        "ss_wages_box_3": None,
        "ss_tax_box_4": None,
        "medicare_wages_box_5": None,
        "medicare_tax_box_6": None,

        "dependent_care_box_10": None,
        "box_12": [],
        "box_13_flags": [],
        "box_14": None,

        "state_info": []
    }

    # MAIN EXTRACTION LOOP
    for key_id, key_block in key_map.items():
        key_text = get_text(key_block).lower().replace(".", "").strip()
        value_block = find_value_block(key_block)

        if not value_block:
            continue

        value_text = get_text(value_block)

        # IDENTIFICATION

        if "social security number" in key_text:
            extracted["employee_ssn"] = value_text

        elif "employer identification" in key_text or "ein" in key_text:
            extracted["employer_ein"] = value_text

        elif "employer" in key_text and "name" in key_text:
            name, address = split_name_address(value_text)
            extracted["employer_name"] = name
            extracted["employer_address"] = address

        elif "employee" in key_text and "name" in key_text:
            name, address = split_name_address(value_text)
            extracted["employee_name"] = name
            extracted["employee_address"] = address

        # FEDERAL BOXES

        elif "1 wages" in key_text or "wages tips other compensation" in key_text:
            extracted["wages_box_1"] = value_text

        elif "2 federal income tax" in key_text:
            extracted["federal_tax_box_2"] = value_text

        elif "3 social security wages" in key_text:
            extracted["ss_wages_box_3"] = value_text

        elif "4 social security tax" in key_text:
            extracted["ss_tax_box_4"] = value_text

        elif "5 medicare wages" in key_text:
            extracted["medicare_wages_box_5"] = value_text

        elif "6 medicare tax" in key_text:
            extracted["medicare_tax_box_6"] = value_text


        # BENEFITS

        elif "10 dependent care" in key_text:
            extracted["dependent_care_box_10"] = value_text

        elif "12" in key_text:
            extracted["box_12"].append(value_text)

        elif "13" in key_text:
            extracted["box_13_flags"].append(value_text)

        elif "14" in key_text:
            extracted["box_14"] = value_text


        # STATE

        elif "15 state" in key_text:
            extracted["state_info"].append({"state_id": value_text})

        elif "16 state wages" in key_text:
            extracted["state_info"].append({"wages": value_text})

        elif "17 state income tax" in key_text:
            extracted["state_info"].append({"tax": value_text})

    # FALLBACK LOGIC (CRITICAL)

    if extracted["wages_box_1"] is None:
        for block in blocks:
            if block.get("BlockType") == "LINE":
                text = block.get("Text", "").lower()

                if "wages" in text and "$" in text:
                    extracted["wages_box_1"] = text

    # PASS 2 - LINE-BASED FALLBACK

    if extracted["wages_box_1"] is None:
        for line in raw_text.lower().split("\n"):
            if "wages" in line and any(char.isdigit() for char in line):
                extracted["wages_box_1"] = line.strip()

    if extracted["employer_ein"] is None:
        for line in raw_text.split("\n"):
            if "-" in line and len(line.strip()) <= 15:
                extracted["employer_ein"] = line.strip()

    # PASS 3 - REGEX PRECISION EXTRACTION

    if extracted["wages_box_1"] is None:
        for line in raw_text.lower().split("\n"):
            if "wages" in line and any(char.isdigit() for char in line):
                extracted["wages_box_1"] = line.strip()

    if extracted["employer_ein"] is None:
        for line in raw_text.split("\n"):
            if "-" in line and len(line.strip()) <= 15:
                extracted["employer_ein"] = line.strip()

    # PASS 3 — EIN REGEX EXTRACTION (HIGH PRIORITY FALLBACK)

    import re

    # Try strict EIN format first (XX-XXXXXXX)
    match = re.search(r"\b\d{2}-\d{7}\b", raw_text)

    # If not found, try 9-digit fallback
    if not match:
        match = re.search(r"\b\d{9}\b", raw_text)

    if match:
        ein = match.group()

        # Normalize if it's 9 digits (no dash)
        if len(ein) == 9:
            ein = f"{ein[:2]}-{ein[2:]}"

        extracted["employer_ein"] = ein
        
    return extracted