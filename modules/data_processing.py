import re
from typing import List, Dict
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .tools import clean_text

nltk.download("vader_lexicon")
nltk.download("stopwords")

def analyze_sentiment(documents: List[str]) -> Dict[str, float]:
    """
    Computes the average sentiment scores for a list of documents using VADER.
    """
    sid = SentimentIntensityAnalyzer()
    sentiments = {"neg": 0, "neu": 0, "pos": 0, "compound": 0}
    count = 0
    for doc in documents:
        scores = sid.polarity_scores(doc)
        for key in sentiments:
            sentiments[key] += scores[key]
        count += 1
    if count > 0:
        sentiments = {k: v / count for k, v in sentiments.items()}
    return sentiments

def extract_hook_examples(reddit_data: Dict[str, List[str]], example_limit: int = 3) -> List[str]:
    """
    Scans through Reddit data (grouped by subreddit) and returns sentences that look like potential hooks.
    """
    examples = []
    hook_keywords = [
        "stop scrolling",
        "the best way",
        "put your phone down",
        "this is what happens when",
        "have you heard",
        "did you know",
        "here's a fun fact",
        "this will blow",
        "here's the truth",
        "did it ever occur",
        "forget everything you know about"
    ]
    for subreddit, posts in reddit_data.items():
        for post in posts:
            sentences = re.split(r'[.!?]', post)
            for sentence in sentences:
                sentence_clean = sentence.strip()
                if len(sentence_clean) < 20:
                    continue
                sentence_lower = sentence_clean.lower()
                if any(keyword in sentence_lower for keyword in hook_keywords):
                    examples.append(sentence_clean)
                    if len(examples) >= example_limit:
                        return examples
    return examples
