import re
import os
import json
import unicodedata
from datetime import datetime

def clean_text(text: str) -> str:
    """
    Cleans the input text by removing extra spaces and non-word characters,
    and lowercasing the result.
    """
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\W+", " ", text)
    return text.lower().strip()

def normalize_text(text: str) -> str:
    """
    Normalizes text by replacing unwanted Unicode characters with plain-text equivalents,
    and then removing any remaining non-ASCII characters.
    """
    # Explicit replacements for common unwanted Unicode characters
    replacements = {
        "\u2026": "...",  # ellipsis
        "\u2019": "'",    # right single quotation mark
        "\u2018": "'",    # left single quotation mark
        "\u2013": "-",    # en dash
        "\u2014": "-",    # em dash
        "\u201c": '"',    # left double quotation mark
        "\u201d": '"',    # right double quotation mark
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return normalized

def save_output(data: dict, output_dir: str = "outputs") -> None:
    """
    Saves the provided data dictionary as a JSON file in the outputs/ folder.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"run_{timestamp}.json")
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Output saved to {output_file}")
