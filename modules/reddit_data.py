import logging
import re
import praw
from prawcore.exceptions import Forbidden, NotFound, Redirect
import streamlit as st

logger = logging.getLogger(__name__)

def fetch_reddit_data(subreddits: list, limit: int = 30) -> dict:
    reddit = praw.Reddit(
        client_id=st.secrets["reddit"]["REDDIT_CLIENT_ID"],
        client_secret=st.secrets["reddit"]["REDDIT_CLIENT_SECRET"],
        user_agent=st.secrets["reddit"]["REDDIT_USER_AGENT"],
    )
    
    subreddit_posts = {}
    for subreddit in subreddits:
        try:
            logger.info(f"Fetching posts from subreddit: {subreddit}")
            sub = reddit.subreddit(subreddit)
            posts = []
            for submission in sub.hot(limit=limit):
                text = submission.title + " " + submission.selftext
                posts.append(text)
            subreddit_posts[subreddit] = posts
        except (Forbidden, NotFound, Redirect) as e:
            logger.warning(f"Skipping subreddit '{subreddit}': {e}")
    return subreddit_posts

def discover_subreddits(product_info: dict, n: int = 10) -> list:
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
    
    subreddits = re.findall(r'(?:\d+\.\s*)?([a-zA-Z0-9_]+)', raw)
    return subreddits[:n]
