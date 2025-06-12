from airflow.decorators import dag, task
from airflow.utils import timezone
from datetime import timedelta
import pandas as pd
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import nltk
import ssl

# Fix SSL certificate issues
ssl._create_default_https_context = ssl._create_unverified_context

# Setup NLTK
def setup_nltk():
    nltk_data_path = Path.home() / "nltk_data"
    nltk_data_path.mkdir(parents=True, exist_ok=True)
    nltk.download('stopwords', download_dir=str(nltk_data_path), quiet=True)
    nltk.data.path.append(str(nltk_data_path))

setup_nltk()
stop_words = set(nltk.corpus.stopwords.words('english'))

# File paths inside container
RAW_DATA_DIR = Path("/opt/airflow/data/")
CLEANED_DATA_DIR = Path("/opt/airflow/data/")
INPUT_FILE = RAW_DATA_DIR / "flattened_reddit_data.csv"
OUTPUT_FILE = CLEANED_DATA_DIR / "cleaned_reddit_posts.csv"

def clean_comment(comment: str) -> str:
    if pd.isna(comment):
        return ""
    soup = BeautifulSoup(comment, "html.parser")
    text = soup.get_text()
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = text.encode('ascii', 'ignore').decode()
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip().lower()

@dag(
    dag_id="clean_reddit_data_dag",
    start_date=timezone.datetime(2025, 5, 15),
    schedule=None,  # No auto scheduling
    catchup=False,
    tags=["data-cleaning", "reddit"]
)
def reddit_cleaning_dag():

    @task()
    def clean_reddit_comments():
        if not INPUT_FILE.exists():
            available = "\n  - ".join(os.listdir(RAW_DATA_DIR)) if RAW_DATA_DIR.exists() else "Raw data folder not found"
            raise FileNotFoundError(
                f"Input file not found: {INPUT_FILE}\nAvailable files:\n  - {available}"
            )

        df = pd.read_csv(INPUT_FILE, on_bad_lines='skip')  # ✅ Fixed line

        possible_columns = {"comment", "body", "text", "comment body"}
        comment_col = next(
            (col for col in df.columns if col.lower().replace("_", " ") in possible_columns),
            None
        )
        if not comment_col:
            raise ValueError(f"No valid comment column found. Available: {df.columns.tolist()}")

        df['cleaned_text'] = df[comment_col].apply(clean_comment)
        df = df[df['cleaned_text'].str.len() > 0]

        CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Cleaned {len(df)} comments. Saved to {OUTPUT_FILE}")

    clean_reddit_comments()

reddit_cleaning_dag = reddit_cleaning_dag()
