import streamlit as st
from openai import OpenAI

def generate_refined_keywords(product_info: dict, aggregated_text: str) -> list:
    """
    Uses the OpenAI API (with credentials from st.secrets) to generate a comma-separated list of product-relevant keywords.
    """
    client = OpenAI(api_key=st.secrets["openai"]["OPENAI_API_KEY"])
    model_name = st.secrets["openai"].get("MODEL_NAME", "gpt-4o")
    temperature = float(st.secrets["openai"].get("TEMPERATURE", 0.7))
    
    prompt = (
        "You are an expert in marketing and keyword analysis. Given the following product information and Reddit data, "
        "generate a concise, comma-separated list of keywords that best represent the product. "
        "Exclude generic terms such as 'https', 'com', 'reddit', etc.\n\n"
        "Product Information:\n"
    )
    for key, value in product_info.items():
        prompt += f"- {key}: {value}\n"
    prompt += "\nReddit Data (first 1000 characters):\n" + aggregated_text[:1000] + "\n\nKeywords:"
    
    response = client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    
    output = response.output_text
    if isinstance(output, list):
        refined = output[0].get("content", "")
    elif isinstance(output, str):
        refined = output
    else:
        refined = str(output)
    refined_keywords = [kw.strip() for kw in refined.split(",") if kw.strip()]
    return refined_keywords

def generate_hook(prompt: str) -> str:
    """
    Uses the OpenAI API (with credentials from st.secrets) to generate content hooks based on the provided prompt.
    Returns a newline-separated string of hooks.
    """
    client = OpenAI(api_key=st.secrets["openai"]["OPENAI_API_KEY"])
    model_name = st.secrets["openai"].get("MODEL_NAME", "gpt-4o")
    temperature = float(st.secrets["openai"].get("TEMPERATURE", 0.7))
    
    input_messages = [
        {
            "role": "developer",
            "content": (
                "You are a creative copywriter who specializes in producing hooks that immediately capture attention. "
                "Your hooks should blend elements from the provided hook templates with language inspired by the product details and real Reddit data. "
                "Do not be generic—make each hook distinct and memorable."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    response = client.responses.create(
        model=model_name,
        input=input_messages,
        temperature=temperature
    )
    
    output = response.output_text
    generated_text = ""
    if isinstance(output, list):
        for msg in output:
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                for part in msg.get("content", []):
                    if part.get("type") == "output_text":
                        generated_text += part.get("text", "") + "\n"
    elif isinstance(output, str):
        generated_text = output
    else:
        generated_text = str(output)
    
    return generated_text.strip()
