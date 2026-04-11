from __future__ import annotations

import json
import os


def save_result(data: dict, file_path: str = "processed_results.json") -> None:
    results = []

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                results = json.load(file_handle)
        except json.JSONDecodeError:
            results = []

    results.append(data)

    with open(file_path, "w", encoding="utf-8") as file_handle:
        json.dump(results, file_handle, indent=4)
