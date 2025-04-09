import re
import os
import json
import unicodedata
from datetime import datetime

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\W+", " ", text)
    return text.lower().strip()

def normalize_text(text: str) -> str:
    replacements = {
        "\u2026": "...",
        "\u2019": "'",
        "\u2018": "'",
        "\u2013": "-",
        "\u2014": "-",
        "\u201c": '"',
        "\u201d": '"',
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return normalized

def save_output(data: dict, output_dir: str = "outputs") -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"run_{timestamp}.json")
    # Write without ASCII escaping.
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Output saved to {output_file}")
