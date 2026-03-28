import json

OUTPUT_FILE = "processed_results.json"

def save_result(result):
    try:
        try:
            with open(OUTPUT_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append(result)

        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"[ERROR] {str(e)}")