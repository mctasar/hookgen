import json
import os

TEMP_FILE = "temp.json"

DEFAULT_PRODUCT_INFO = {
    "PRODUCT_NAME": "FastingPro",
    "PRODUCT_DESCRIPTION": "FastingPro is an innovative fasting app that provides personalized fasting schedules, real-time tracking, and expert tips to help you achieve your health goals.",
    "TARGET_AUDIENCE": "Health-conscious individuals, fitness enthusiasts, and anyone looking to improve their lifestyle through intermittent fasting.",
    "KEY_BENEFITS": "Personalized fasting plans, progress tracking, expert guidance, and a supportive community.",
    "BRAND_TONE": "Empowering, motivational, and informative",
    "CONTEXT_INFO": "Introducing our latest update with enhanced tracking features and new expert resources to help users maximize the benefits of intermittent fasting."
}

DEFAULT_BASE_INSTRUCTION = (
    "You are a creative copywriter who specializes in producing hooks that immediately capture attention. "
    "Your task is to generate creative, clickbaity, and engaging hook options using the information provided below. "
    "Each hook should blend elements from the provided hook templates with language inspired by the product details and real Reddit data. "
    "Do not be generic; be bold, vivid, and tailored to the product."
)

def save_defaults(product_info: dict, base_instruction: str):
    defaults = {"product_info": product_info, "base_instruction": base_instruction}
    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        json.dump(defaults, f, indent=4, ensure_ascii=False)

def load_defaults():
    if os.path.exists(TEMP_FILE):
        with open(TEMP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"product_info": DEFAULT_PRODUCT_INFO, "base_instruction": DEFAULT_BASE_INSTRUCTION}

def revert_to_defaults():
    defaults_dict = {"product_info": DEFAULT_PRODUCT_INFO, "base_instruction": DEFAULT_BASE_INSTRUCTION}
    save_defaults(DEFAULT_PRODUCT_INFO, DEFAULT_BASE_INSTRUCTION)
    return defaults_dict
