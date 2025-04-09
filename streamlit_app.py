import os
import re
import json
import logging
import streamlit as st
from modules import reddit_data, data_processing, prompt_generator, hook_generator, defaults
from modules.prompt_generator import HOOK_TEMPLATES
from modules.tools import save_output, normalize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Hook Generator")

# Load saved defaults from temp.json (or use built-in defaults if none exists)
saved_defaults = defaults.load_defaults()
if "product_info" not in st.session_state:
    st.session_state["product_info"] = saved_defaults["product_info"].copy()
if "base_instruction" not in st.session_state:
    st.session_state["base_instruction"] = saved_defaults["base_instruction"]

# Sidebar: Input Parameters using session state
st.sidebar.header("Product Information")
st.session_state["product_info"]["PRODUCT_NAME"] = st.sidebar.text_input(
    "Product Name", 
    value=st.session_state["product_info"]["PRODUCT_NAME"], 
    key="product_name_input"
)
st.session_state["product_info"]["PRODUCT_DESCRIPTION"] = st.sidebar.text_area(
    "Product Description", 
    value=st.session_state["product_info"]["PRODUCT_DESCRIPTION"], 
    key="product_description_input"
)
st.session_state["product_info"]["TARGET_AUDIENCE"] = st.sidebar.text_input(
    "Target Audience", 
    value=st.session_state["product_info"]["TARGET_AUDIENCE"], 
    key="target_audience_input"
)
st.session_state["product_info"]["KEY_BENEFITS"] = st.sidebar.text_area(
    "Key Benefits", 
    value=st.session_state["product_info"]["KEY_BENEFITS"], 
    key="key_benefits_input"
)
st.session_state["product_info"]["BRAND_TONE"] = st.sidebar.text_input(
    "Brand Tone", 
    value=st.session_state["product_info"]["BRAND_TONE"], 
    key="brand_tone_input"
)
st.session_state["product_info"]["CONTEXT_INFO"] = st.sidebar.text_area(
    "Context Information", 
    value=st.session_state["product_info"]["CONTEXT_INFO"], 
    key="context_info_input"
)
n_hooks_ui = st.sidebar.number_input(
    "Number of Hooks", min_value=1, max_value=20, 
    value=int(st.secrets["openai"].get("N_HOOKS", 3)), 
    key="n_hooks_input"
)

st.sidebar.header("Base Prompt Instruction")
base_instruction = st.sidebar.text_area(
    "Edit Base Prompt Instruction", 
    value=st.session_state["base_instruction"], 
    height=150, 
    key="base_instruction_input"
)

def update_session_state():
    st.session_state["product_info"] = {
        "PRODUCT_NAME": st.session_state["product_name_input"],
        "PRODUCT_DESCRIPTION": st.session_state["product_description_input"],
        "TARGET_AUDIENCE": st.session_state["target_audience_input"],
        "KEY_BENEFITS": st.session_state["key_benefits_input"],
        "BRAND_TONE": st.session_state["brand_tone_input"],
        "CONTEXT_INFO": st.session_state["context_info_input"],
    }
    st.session_state["base_instruction"] = st.session_state["base_instruction_input"]

update_session_state()

if st.sidebar.button("Save Inputs as Defaults"):
    current_defaults = {
        "product_info": st.session_state["product_info"],
        "base_instruction": st.session_state["base_instruction"]
    }
    with open("temp.json", "w", encoding="utf-8") as f:
        json.dump(current_defaults, f, indent=4, ensure_ascii=False)
    defaults.save_defaults(current_defaults["product_info"], current_defaults["base_instruction"])
    st.sidebar.success("Inputs saved as defaults!")

if st.sidebar.button("Revert to Defaults"):
    loaded = defaults.revert_to_defaults()  # Loads built-in defaults and updates temp.json
    st.session_state["product_info"] = loaded["product_info"].copy()
    st.session_state["base_instruction"] = loaded["base_instruction"]
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.sidebar.info("Reverted to defaults! Please refresh the page if inputs do not update.")

def get_marketing_inputs() -> dict:
    return st.session_state["product_info"]

if st.button("Generate Hooks"):
    product_info = get_marketing_inputs()
    
    with st.spinner("Generating hooks..."):
        # 1. Discover subreddits using product info
        discovered_subreddits = reddit_data.discover_subreddits(product_info, n=10)
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
        
        # 5. Extract hook-like examples from Reddit data
        reddit_hook_examples = data_processing.extract_hook_examples(reddit_posts_by_subreddit, example_limit=3)
        
        # 6. Generate refined keywords based on product info and aggregated Reddit text
        refined_keywords = hook_generator.generate_refined_keywords(product_info, aggregated_text)
        
        # 7. Get number of hooks from UI
        n_hooks = n_hooks_ui
        
        # 8. Construct the final prompt using HOOK_TEMPLATES and the UI-edited base instruction
        final_prompt = prompt_generator.construct_prompt(
            product_info,
            refined_keywords,
            sentiment,
            reddit_hook_examples,
            n_hooks,
            base_instruction=st.session_state["base_instruction"]
        )
        logger.info("Constructed Prompt:\n%s", final_prompt)
        
        # 9. Generate hooks using the OpenAI API
        generated_hooks_raw = hook_generator.generate_hook(final_prompt)
        logger.info("Raw Generated Hooks: %s", generated_hooks_raw)
        
        # 10. Normalize and split the generated hooks into a list (one per line)
        generated_hooks = [normalize_text(hook.strip()) for hook in generated_hooks_raw.splitlines() if hook.strip()]
        
        # 11. Save run data locally as JSON in the outputs folder
        run_data = {
            "marketing_inputs": product_info,
            "discovered_subreddits": discovered_subreddits,
            "reddit_subreddits_used": reddit_posts_by_subreddit,
            "refined_keywords": refined_keywords,
            "sentiment": sentiment,
            "captured_reddit_examples": reddit_hook_examples,
            "hook_templates": HOOK_TEMPLATES,
            "n_hooks": n_hooks,
            "base_instruction": st.session_state["base_instruction"],
            "constructed_prompt": final_prompt,
            "generated_hooks": generated_hooks,
        }
        save_output(run_data)
        st.session_state["run_data"] = run_data  # Save for potential future use
    
    st.success("Hooks generated successfully!")
    st.header("Generated Hooks")
    for hook in generated_hooks:
        st.write(hook)
