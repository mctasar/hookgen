import os
import re
import logging
import streamlit as st
from modules import reddit_data, data_processing, prompt_generator, hook_generator
from modules.prompt_generator import HOOK_TEMPLATES
from modules.tools import save_output, normalize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Hook Generator")

# Sidebar: Input Parameters (with defaults)
st.sidebar.header("Product Information")
product_name = st.sidebar.text_input("Product Name", value="FastingPro")
product_description = st.sidebar.text_area(
    "Product Description", 
    value="FastingPro is an innovative fasting app that provides personalized fasting schedules, real-time tracking, and expert tips to help you achieve your health goals."
)
target_audience = st.sidebar.text_input(
    "Target Audience", 
    value="Health-conscious individuals, fitness enthusiasts, and anyone looking to improve their lifestyle through intermittent fasting."
)
key_benefits = st.sidebar.text_area(
    "Key Benefits", 
    value="Personalized fasting plans, progress tracking, expert guidance, and a supportive community."
)
brand_tone = st.sidebar.text_input("Brand Tone", value="Empowering, motivational, and informative")
context_info = st.sidebar.text_area(
    "Context Information", 
    value="Introducing our latest update with enhanced tracking features and new expert resources to help users maximize the benefits of intermittent fasting."
)
n_hooks_ui = st.sidebar.number_input("Number of Hooks", min_value=1, max_value=20, value=3)

st.sidebar.header("Base Prompt Instruction")
default_base_instruction = (
    "You are a creative copywriter who specializes in producing hooks that immediately capture attention. "
    "Your task is to generate creative, clickbaity, and engaging hook options using the information provided below. "
    "Each hook should blend elements from the provided hook templates with language inspired by the product details and real Reddit data. "
    "Do not be generic; be bold, vivid, and tailored to the product."
)
base_instruction = st.sidebar.text_area("Edit Base Prompt Instruction", value=default_base_instruction, height=150)

def get_marketing_inputs() -> dict:
    # Removed CALL_TO_ACTION, as requested.
    return {
        "PRODUCT_NAME": product_name,
        "PRODUCT_DESCRIPTION": product_description,
        "TARGET_AUDIENCE": target_audience,
        "KEY_BENEFITS": key_benefits,
        "BRAND_TONE": brand_tone,
        "CONTEXT_INFO": context_info,
    }

def discover_subreddits(product_info: dict, n: int = 10) -> list:
    """
    Uses the OpenAI API to discover a list of relevant subreddit names using st.secrets.
    """
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["openai"]["OPENAI_API_KEY"])
    model_name = st.secrets["openai"].get("MODEL_NAME", "gpt-4o")
    temperature = float(st.secrets["openai"].get("TEMPERATURE", 0.7))
    
    prompt = (
        "You are an expert in social media and online communities. Based on the following product information, "
        "list 10 relevant subreddit names (only the names, separated by commas or as a numbered list) where people discuss "
        "topics related to this product.\n\nProduct Information:\n"
    )
    for key, value in product_info.items():
        prompt += f"- {key}: {value}\n"
    
    response = client.responses.create(
        model=model_name,
        input=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    output = response.output_text
    if isinstance(output, list):
        raw = output[0].get("content", "")
    elif isinstance(output, str):
        raw = output
    else:
        raw = str(output)
    
    # Extract subreddit names using a regex
    subreddits = re.findall(r'(?:\d+\.\s*)?([a-zA-Z0-9_]+)', raw)
    return subreddits[:n]

if st.button("Generate Hooks"):
    product_info = get_marketing_inputs()
    
    with st.spinner("Generating hooks..."):
        # 1. Discover relevant subreddits
        discovered_subreddits = discover_subreddits(product_info, n=10)
        logger.info("Discovered Subreddits: %s", discovered_subreddits)
        
        # 2. Fetch Reddit data from discovered subreddits
        reddit_posts_by_subreddit = reddit_data.fetch_reddit_data(discovered_subreddits, limit=30)
        
        # 3. Aggregate all Reddit posts
        all_reddit_posts = []
        for posts in reddit_posts_by_subreddit.values():
            all_reddit_posts.extend(posts)
        aggregated_text = " ".join(all_reddit_posts)
        
        # 4. Perform sentiment analysis on aggregated posts
        sentiment = data_processing.analyze_sentiment(all_reddit_posts)
        
        # 5. Extract hook examples from Reddit data
        reddit_hook_examples = data_processing.extract_hook_examples(reddit_posts_by_subreddit, example_limit=3)
        
        # 6. Generate refined, product-relevant keywords using an intermediate prompt
        refined_keywords = hook_generator.generate_refined_keywords(product_info, aggregated_text)
        
        # 7. Use the UI number input for number of hooks
        n_hooks = n_hooks_ui
        
        # 8. Construct the final prompt—pass base_instruction from UI to allow editing!
        final_prompt = prompt_generator.construct_prompt(
            product_info,
            refined_keywords,
            sentiment,
            reddit_hook_examples,
            n_hooks,
            base_instruction=base_instruction
        )
        logger.info("Constructed Prompt:\n%s", final_prompt)
        
        # 9. Generate hooks using the OpenAI API
        generated_hooks_raw = hook_generator.generate_hook(final_prompt)
        logger.info("Raw Generated Hooks: %s", generated_hooks_raw)
        
        # 10. Normalize and split the hooks
        generated_hooks = [normalize_text(hook.strip()) for hook in generated_hooks_raw.splitlines() if hook.strip()]
        
        # 11. Save all run data as a JSON locally
        run_data = {
            "marketing_inputs": product_info,
            "discovered_subreddits": discovered_subreddits,
            "reddit_subreddits_used": reddit_posts_by_subreddit,
            "refined_keywords": refined_keywords,
            "sentiment": sentiment,
            "captured_reddit_examples": reddit_hook_examples,
            "hook_templates": HOOK_TEMPLATES,
            "n_hooks": n_hooks,
            "base_instruction": base_instruction,
            "constructed_prompt": final_prompt,
            "generated_hooks": generated_hooks,
        }
        save_output(run_data)
    
    st.success("Hooks generated successfully!")
    st.header("Generated Hooks")
    for hook in generated_hooks:
        st.write(hook)
