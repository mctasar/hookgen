import logging
import praw
from prawcore.exceptions import Forbidden, NotFound, Redirect
import streamlit as st

logger = logging.getLogger(__name__)

def fetch_reddit_data(subreddits: list, limit: int = 30) -> dict:
    """
    Connects to Reddit using PRAW with credentials from st.secrets and fetches posts from the provided subreddits.
    Subreddits that are forbidden, not found, or result in a Redirect are skipped.
    Returns a dictionary mapping each subreddit to its list of posts.
    """
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
