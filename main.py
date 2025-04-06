import os
import re
import logging
from dotenv import load_dotenv
from modules import reddit_data, data_processing, prompt_generator, hook_generator
from modules.prompt_generator import HOOK_TEMPLATES
from modules.tools import save_output, normalize_text
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_marketing_inputs() -> dict:
    return {
        "PRODUCT_NAME": os.getenv("PRODUCT_NAME"),
        "PRODUCT_DESCRIPTION": os.getenv("PRODUCT_DESCRIPTION"),
        "TARGET_AUDIENCE": os.getenv("TARGET_AUDIENCE"),
        "KEY_BENEFITS": os.getenv("KEY_BENEFITS"),
        "BRAND_TONE": os.getenv("BRAND_TONE"),
        "CONTEXT_INFO": os.getenv("CONTEXT_INFO"),
        "CALL_TO_ACTION": os.getenv("CALL_TO_ACTION"),
    }

def discover_subreddits(marketing_inputs: dict, n: int = 10) -> list:
    """
    Uses the OpenAI API to discover a list of relevant subreddits based on the product marketing info.
    Returns a list of subreddit names.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    
    prompt = (
        "You are an expert in social media and online communities. Based on the following product information, "
        "list 10 relevant subreddit names (only the names, separated by commas or numbered list) where people discuss "
        "topics related to this product.\n\n"
        "Product Information:\n"
    )
    for key, value in marketing_inputs.items():
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

def main():
    marketing_inputs = get_marketing_inputs()
    
    # Dynamically discover relevant subreddits (10 subreddits)
    discovered_subreddits = discover_subreddits(marketing_inputs, n=10)
    logger.info("Discovered Subreddits: %s", discovered_subreddits)
    
    # Gather Reddit data as a dictionary {subreddit: [posts]}
    reddit_posts_by_subreddit = reddit_data.fetch_reddit_data(discovered_subreddits, limit=30)
    
    # Aggregate all posts for analysis
    all_reddit_posts = []
    for posts in reddit_posts_by_subreddit.values():
        all_reddit_posts.extend(posts)
    aggregated_text = " ".join(all_reddit_posts)
    
    # Perform sentiment analysis on aggregated posts
    sentiment = data_processing.analyze_sentiment(all_reddit_posts)
    
    # Extract hook examples from Reddit data
    reddit_hook_examples = data_processing.extract_hook_examples(reddit_posts_by_subreddit, example_limit=3)
    
    # Use intermediate prompt to generate refined keywords
    refined_keywords = hook_generator.generate_refined_keywords(marketing_inputs, aggregated_text)
    
    # Get number of hooks to generate from environment variable
    n_hooks = int(os.getenv("N_HOOKS", "3"))
    
    # Construct final prompt using HOOK_TEMPLATES from prompt_generator
    final_prompt = prompt_generator.construct_prompt(
        marketing_inputs,
        refined_keywords,
        sentiment,
        reddit_hook_examples,
        n_hooks
    )
    logger.info("Constructed Prompt:\n%s", final_prompt)
    
    # Generate hooks using the OpenAI API
    generated_hooks_raw = hook_generator.generate_hook(final_prompt)
    logger.info("Raw Generated Hooks: %s", generated_hooks_raw)
    
    # Normalize and split generated hooks into an array
    generated_hooks = [normalize_text(hook.strip()) for hook in generated_hooks_raw.splitlines() if hook.strip()]
    
    run_data = {
        "marketing_inputs": marketing_inputs,
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
    
    print("Final Generated Hooks:")
    for hook in generated_hooks:
        print(hook)

if __name__ == "__main__":
    main()
