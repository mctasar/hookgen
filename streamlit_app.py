import os
import re
import logging
import streamlit as st
from dotenv import load_dotenv
from modules import reddit_data, data_processing, prompt_generator, hook_generator
from modules.prompt_generator import HOOK_TEMPLATES
from modules.tools import save_output, normalize_text
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Hook Generator")

# Sidebar: Input Parameters (defaults from .env)
st.sidebar.header("Input Parameters")
product_name = st.sidebar.text_input("Product Name", value=os.getenv("PRODUCT_NAME", "FastingPro"))
product_description = st.sidebar.text_area("Product Description", 
    value=os.getenv("PRODUCT_DESCRIPTION", "FastingPro is an innovative fasting app that provides personalized fasting schedules, real-time tracking, and expert tips to help you achieve your health goals."))
target_audience = st.sidebar.text_input("Target Audience", value=os.getenv("TARGET_AUDIENCE", "Health-conscious individuals, fitness enthusiasts, and anyone looking to improve their lifestyle through intermittent fasting."))
key_benefits = st.sidebar.text_area("Key Benefits", value=os.getenv("KEY_BENEFITS", "Personalized fasting plans, progress tracking, expert guidance, and a supportive community."))
brand_tone = st.sidebar.text_input("Brand Tone", value=os.getenv("BRAND_TONE", "Empowering, motivational, and informative"))
context_info = st.sidebar.text_area("Context Information", value=os.getenv("CONTEXT_INFO", "Introducing our latest update with enhanced tracking features and new expert resources to help users maximize the benefits of intermittent fasting."))
n_hooks = st.sidebar.number_input("Number of Hooks", min_value=1, max_value=20, value=int(os.getenv("N_HOOKS", "3")))

def get_marketing_inputs() -> dict:
    # Removed CALL_TO_ACTION from inputs.
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
    Uses the OpenAI API to discover a list of relevant subreddits based on the product marketing info.
    Returns a list of subreddit names.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    
    prompt = (
        "You are an expert in social media and online communities. Based on the following product information, "
        "list 10 relevant subreddit names (only the names, separated by commas or a numbered list) where people discuss "
        "topics related to this product.\n\n"
        "Product Information:\n"
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
    
    # Use regex to extract subreddit names from a numbered or comma-separated list.
    subreddits = re.findall(r'(?:\d+\.\s*)?([a-zA-Z0-9_]+)', raw)
    return subreddits[:n]

if st.button("Generate Hooks"):
    product_info = get_marketing_inputs()
    
    with st.spinner("Generating hooks..."):
        # 1. Discover relevant subreddits
        discovered_subreddits = discover_subreddits(product_info, n=10)
        logger.info("Discovered Subreddits: %s", discovered_subreddits)
        
        # 2. Fetch Reddit data for discovered subreddits
        reddit_posts_by_subreddit = reddit_data.fetch_reddit_data(discovered_subreddits, limit=30)
        
        # 3. Aggregate Reddit posts
        all_reddit_posts = []
        for posts in reddit_posts_by_subreddit.values():
            all_reddit_posts.extend(posts)
        aggregated_text = " ".join(all_reddit_posts)
        
        # 4. Perform sentiment analysis on aggregated posts
        sentiment = data_processing.analyze_sentiment(all_reddit_posts)
        
        # 5. Extract hook-like examples from Reddit data
        reddit_hook_examples = data_processing.extract_hook_examples(reddit_posts_by_subreddit, example_limit=3)
        
        # 6. Generate refined, product-relevant keywords using an intermediate prompt
        refined_keywords = hook_generator.generate_refined_keywords(product_info, aggregated_text)
        
        # 7. Construct final prompt using HOOK_TEMPLATES from prompt_generator
        final_prompt = prompt_generator.construct_prompt(
            product_info,
            refined_keywords,
            sentiment,
            reddit_hook_examples,
            n_hooks
        )
        logger.info("Constructed Prompt:\n%s", final_prompt)
        
        # 8. Generate hooks using the OpenAI API
        generated_hooks_raw = hook_generator.generate_hook(final_prompt)
        logger.info("Raw Generated Hooks: %s", generated_hooks_raw)
        
        # 9. Normalize and split generated hooks into a list
        generated_hooks = [normalize_text(hook.strip()) for hook in generated_hooks_raw.splitlines() if hook.strip()]
        
        # 10. Save run data (output JSON) locally behind the scenes
        run_data = {
            "marketing_inputs": product_info,
            "discovered_subreddits": discovered_subreddits,
            "reddit_subreddits_used": reddit_posts_by_subreddit,
            "refined_keywords": refined_keywords,
            "sentiment": sentiment,
            "captured_reddit_examples": reddit_hook_examples,
            "hook_templates": HOOK_TEMPLATES,
            "n_hooks": n_hooks,
            "constructed_prompt": final_prompt,
            "generated_hooks": generated_hooks,
        }
        save_output(run_data)
    
    st.success("Hooks generated successfully!")
    
    st.header("Generated Hooks")
    for hook in generated_hooks:
        st.write(hook)
