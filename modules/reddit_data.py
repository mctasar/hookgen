import os
import logging
import praw
from prawcore.exceptions import Forbidden, NotFound

logger = logging.getLogger(__name__)

def fetch_reddit_data(subreddits: list, limit: int = 30) -> dict:
    """
    Connects to Reddit using PRAW and fetches posts from the specified subreddits.
    Returns a dictionary mapping each subreddit to its list of post texts.
    Subreddits that are forbidden or not found are skipped.
    """
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
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
        except (Forbidden, NotFound) as e:
            logger.warning(f"Skipping subreddit '{subreddit}': {e}")
    return subreddit_posts
