import json
import os

def save_result(data):
    file_path = "processed_results.json"
    
    # 1. Start with an empty list
    results = []

    # 2. Only try to load if the file exists AND isn't empty (0 bytes)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r") as f:
                results = json.load(f)
        except json.JSONDecodeError:
            print("[WARNING] JSON file was empty or corrupt. Resetting.")
            results = []

    # 3. Add the new tax data
    results.append(data)

    # 4. Save it back
    with open(file_path, "w") as f:
        json.dump(results, f, indent=4)