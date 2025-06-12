from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import re
from bs4 import BeautifulSoup
import nltk
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import torch
import ssl

# Fix SSL for nltk
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords', quiet=True)
stop_words = set(nltk.corpus.stopwords.words('english'))

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Labels
candidate_labels = [
    "Pro-Government", "Anti-Government", "Toxic / Abusive", "Media Criticism",
    "Immigration / Border Issue", "Election & Democracy", "Conspiracy Theory / Misinformation",
    "Religious / Ethnic Sentiment", "Support for Military / Police",
    "Social Justice / Activism", "Neutral / Informative"
]

# Paths
INPUT_PATH = "/opt/airflow/data/youtube_cleaned.csv"
OUTPUT_PATH = "/opt/airflow/data/youtube_labeled.csv"
COMMENT_COLUMN = "Comment"

def clean_comment(comment: str) -> str:
    if pd.isnull(comment):
        return ""
    soup = BeautifulSoup(comment, "html.parser")
    text = soup.get_text()
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = text.encode('ascii', 'ignore').decode()
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def assign_labels(texts, labels):
    label_embeddings = model.encode(labels, convert_to_tensor=True)
    predictions = []
    for text in tqdm(texts, desc="Labeling YouTube comments"):
        text_embedding = model.encode(text, convert_to_tensor=True)
        similarities = util.cos_sim(text_embedding, label_embeddings)
        best_label_idx = torch.argmax(similarities)
        predictions.append(labels[best_label_idx])
    return predictions

def validate_input_data(df):
    global COMMENT_COLUMN
    if COMMENT_COLUMN not in df.columns:
        for col in ["comment", "Comment", "text", "body", "content"]:
            if col in df.columns:
                COMMENT_COLUMN = col
                return
        raise ValueError(f"Comment column not found. Available columns: {list(df.columns)}")
    if df.empty:
        raise ValueError("Input DataFrame is empty")

def run_youtube_labelling_pipeline():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    df = pd.read_csv(INPUT_PATH)
    validate_input_data(df)

    df['cleaned_text'] = df[COMMENT_COLUMN].apply(clean_comment)
    df = df[df['cleaned_text'].str.len() > 0]

    df['label'] = assign_labels(df['cleaned_text'].tolist(), candidate_labels)
    df['platform'] = 'YouTube'  # ✅ Add platform column

    df.to_csv(OUTPUT_PATH, index=False)
    return f"Labeling complete. Output saved at {OUTPUT_PATH}"

# Airflow DAG Definition
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=3)
}

with DAG(
    dag_id='youtube_comment_labelling',
    default_args=default_args,
    description='Label YouTube comments using transformer model',
    start_date=datetime(2025, 5, 15),
    schedule=None,  # Set a cron string for scheduled runs
    catchup=False,
    tags=["nlp", "youtube", "labelling"]
) as dag:

    label_youtube_comments = PythonOperator(
        task_id='run_youtube_labeller',
        python_callable=run_youtube_labelling_pipeline
    )
