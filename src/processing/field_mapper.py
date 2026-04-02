def map_textract_to_tax_fields(response):
    blocks = response.get("Blocks", [])

    # Build lookup maps
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
                        word = block_map[child_id]
                        if word["BlockType"] == "WORD":
                            text += word["Text"] + " "
        return text.strip()

    def find_value_block(key_block):
        if "Relationships" in key_block:
            for rel in key_block["Relationships"]:
                if rel["Type"] == "VALUE":
                    for value_id in rel["Ids"]:
                        return value_map.get(value_id)
        return None

    extracted = {}

    for key_id, key_block in key_map.items():
        key_text = get_text(key_block).lower()
        value_block = find_value_block(key_block)

        if value_block:
            value_text = get_text(value_block)

            # TARGET TAX FIELDS
            if "employer" in key_text:
                extracted["employer"] = value_text

            elif "wages" in key_text or "income" in key_text:
                extracted["income"] = value_text

            elif "social security" in key_text:
                extracted["ssn"] = value_text

    return extracted