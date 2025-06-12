from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import pandas as pd
import os
import re
import ssl
import nltk
import torch
from tqdm import tqdm
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

# Fix SSL
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords', quiet=True)
stop_words = set(nltk.corpus.stopwords.words('english'))

# Global variables
MODEL = SentenceTransformer('all-MiniLM-L6-v2')
CANDIDATE_LABELS = [
    "Pro-Government", "Anti-Government", "Toxic / Abusive", "Media Criticism",
    "Immigration / Border Issue", "Election & Democracy", "Conspiracy Theory / Misinformation",
    "Religious / Ethnic Sentiment", "Support for Military / Police",
    "Social Justice / Activism", "Neutral / Informative"
]

# File Paths
RAW_YOUTUBE_PATH = "/opt/airflow/data/youtube_comments_combined.csv"
RAW_REDDIT_PATH = "/opt/airflow/data/flattened_reddit_data.csv"
CLEAN_YOUTUBE_PATH = "/opt/airflow/data/youtube_cleaned.csv"
CLEAN_REDDIT_PATH = "/opt/airflow/data/cleaned_reddit_posts.csv"
YOUTUBE_OUTPUT = "/opt/airflow/data/youtube_labeled.csv"
REDDIT_OUTPUT = "/opt/airflow/data/reddit_labeled.csv"
MERGED_OUTPUT = "/opt/airflow/data/merged_labeled_comments.csv"

# Utility
def clean_comment(comment: str) -> str:
    if pd.isnull(comment):
        return ""
    text = BeautifulSoup(comment, "html.parser").get_text()
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = text.encode('ascii', 'ignore').decode()
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def assign_labels(texts, labels):
    label_embeddings = MODEL.encode(labels, convert_to_tensor=True)
    predictions = []
    for text in tqdm(texts, desc="Labeling comments"):
        text_embedding = MODEL.encode(text, convert_to_tensor=True)
        similarities = util.cos_sim(text_embedding, label_embeddings)
        best_label_idx = torch.argmax(similarities)
        predictions.append(labels[best_label_idx])
    return predictions

# Cleaning tasks
def clean_youtube():
    df = pd.read_csv(RAW_YOUTUBE_PATH)
    df['cleaned_text'] = df['Comment'].apply(clean_comment)
    df = df[df['cleaned_text'].str.len() > 0]
    df.to_csv(CLEAN_YOUTUBE_PATH, index=False)

def clean_reddit():
    df = pd.read_csv(RAW_REDDIT_PATH)
    df['cleaned_text'] = df['Comment Body'].apply(clean_comment)
    df = df[df['cleaned_text'].str.len() > 0]
    df.to_csv(CLEAN_REDDIT_PATH, index=False)

# Labelling tasks
def label_youtube():
    df = pd.read_csv(CLEAN_YOUTUBE_PATH)
    df['label'] = assign_labels(df['cleaned_text'].tolist(), CANDIDATE_LABELS)
    df['platform'] = "YouTube"
    df.to_csv(YOUTUBE_OUTPUT, index=False)

def label_reddit():
    df = pd.read_csv(CLEAN_REDDIT_PATH)
    df['label'] = assign_labels(df['cleaned_text'].tolist(), CANDIDATE_LABELS)
    df['platform'] = "Reddit"
    df.to_csv(REDDIT_OUTPUT, index=False)

# Validation
def validate_labels(file_path: str, valid_labels: list):
    df = pd.read_csv(file_path)
    if df['label'].isnull().any() or df['cleaned_text'].isnull().any() or df['platform'].isnull().any():
        raise ValueError("Missing or invalid data found in labeling output.")
    if not set(df['label'].unique()).issubset(valid_labels):
        raise ValueError("Invalid labels detected.")

def validate_youtube():
    validate_labels(YOUTUBE_OUTPUT, CANDIDATE_LABELS)

def validate_reddit():
    validate_labels(REDDIT_OUTPUT, CANDIDATE_LABELS)

# Merge task
def merge_datasets():
    youtube_df = pd.read_csv(YOUTUBE_OUTPUT)
    reddit_df = pd.read_csv(REDDIT_OUTPUT)

    merged_df = pd.DataFrame({
        "title": reddit_df["Post Title"].fillna('') + " " + youtube_df["Video Title"].fillna(''),
        "date": youtube_df["Video Published Date"].fillna('') + " " + reddit_df["Post Date"].fillna(''),
        "author": reddit_df["Comment Author"].fillna('') + " " + youtube_df["Comment Author"].fillna(''),
        "cleaned_text": reddit_df["cleaned_text"].fillna('') + " " + youtube_df["cleaned_text"].fillna(''),
        "label": reddit_df["label"].fillna('') + " | " + youtube_df["label"].fillna(''),
        "platform": reddit_df["platform"].fillna('') + " & " + youtube_df["platform"].fillna('')
    })

    merged_df.to_csv(MERGED_OUTPUT, index=False)

# DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='full_text_labelling_pipeline',
    default_args=default_args,
    start_date=datetime(2025, 5, 15),
    schedule=None,
    catchup=False,
    tags=["nlp", "cleaning", "labelling", "merge"]
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    clean_youtube_task = PythonOperator(task_id='clean_youtube_data_dag', python_callable=clean_youtube)
    clean_reddit_task = PythonOperator(task_id='clean_reddit_data_dag', python_callable=clean_reddit)

    label_youtube_task = PythonOperator(task_id='label_youtube', python_callable=label_youtube)
    label_reddit_task = PythonOperator(task_id='label_reddit', python_callable=label_reddit)

    validate_youtube_task = PythonOperator(task_id='validate_youtube_labels', python_callable=validate_youtube)
    validate_reddit_task = PythonOperator(task_id='validate_reddit_labels', python_callable=validate_reddit)

    merge_task = PythonOperator(task_id='merge_labeled_data', python_callable=merge_datasets)

    # DAG Dependencies
    start >> [clean_youtube_task, clean_reddit_task]
    clean_youtube_task >> label_youtube_task >> validate_youtube_task >> merge_task
    clean_reddit_task >> label_reddit_task >> validate_reddit_task >> merge_task
    merge_task >> end
