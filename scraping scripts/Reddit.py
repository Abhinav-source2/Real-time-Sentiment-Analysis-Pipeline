import os
import json
import time
import certifi
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import praw
from praw.models import MoreComments
from praw.exceptions import PRAWException
from dotenv import load_dotenv

# Fix SSL verification issues
os.environ['SSL_CERT_FILE'] = certifi.where()

# Load credentials from .env file
load_dotenv("detail.env")

def setup_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD")
    )

def extract_top_level_comments(post):
    top_comments = []
    for top_level_comment in post.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        top_comments.append({
            "comment_author": str(top_level_comment.author) if top_level_comment.author else "[deleted]",
            "comment_body": top_level_comment.body.replace("\n", " "),
            "comment_score": top_level_comment.score
        })
    return top_comments

def extract_post_data(post):
    try:
        post.comments.replace_more(limit=0)
        return {
            "post_title": post.title,
            "post_author": str(post.author) if post.author else "[deleted]",
            "post_date": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
            "content_type": "text" if post.is_self else "link",
            "content_url": post.url,
            "post_text": post.selftext if post.is_self else "",
            "post_score": post.score,
            "comments": extract_top_level_comments(post)  # Only top-level comments
        }
    except Exception as e:
        print(f"❌ Error processing post: {e}")
        return None

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Saved {len(data)} posts to {filename}")

def scrape_reddit_data(queries, posts_per_query=200):
    reddit = setup_reddit_client()
    for query in queries:
        print(f"\n🔍 Scraping query: {query}")
        results = []
        try:
            posts = list(reddit.subreddit("all").search(query, sort="top", limit=posts_per_query))
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(extract_post_data, post) for post in posts]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        results.append(result)
        except PRAWException as e:
            print(f"⚠️ Error while scraping '{query}': {e}")
        time.sleep(2)
        save_to_json(results, filename=f"{query}_reddit_posts.json")

if __name__ == "__main__":
    queries = [
        'US_debate_impact',
    ]
    scrape_reddit_data(queries, posts_per_query=200)
