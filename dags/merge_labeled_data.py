from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd

# File Paths
YOUTUBE_PATH = "/opt/airflow/data/youtube_labeled.csv"
REDDIT_PATH = "/opt/airflow/data/reddit_labeled.csv"
OUTPUT_PATH = "/opt/airflow/data/combined_labeled.csv"

def merge_and_normalize():
    if not os.path.exists(YOUTUBE_PATH):
        raise FileNotFoundError(f"YouTube labeled file not found: {YOUTUBE_PATH}")
    if not os.path.exists(REDDIT_PATH):
        raise FileNotFoundError(f"Reddit labeled file not found: {REDDIT_PATH}")
    
    # Read both files
    df_youtube = pd.read_csv(YOUTUBE_PATH)
    df_reddit = pd.read_csv(REDDIT_PATH)

    # Normalize YouTube columns
    yt_df = pd.DataFrame({
        'title': df_youtube['Video Title'],
        'date': df_youtube['Video Published Date'],
        'author': df_youtube['Comment Author'],
        'cleaned_text': df_youtube['cleaned_text'],
        'label': df_youtube['label'],
        'platform': df_youtube['platform']
    })

    # Normalize Reddit columns
    reddit_df = pd.DataFrame({
        'title': df_reddit['Post Title'],
        'date': df_reddit['Post Date'],
        'author': df_reddit['Comment Author'],
        'cleaned_text': df_reddit['cleaned_text'],
        'label': df_reddit['label'],
        'platform': df_reddit['platform']
    })

    # Merge the two
    combined_df = pd.concat([yt_df, reddit_df], ignore_index=True)

    # Save to output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    combined_df.to_csv(OUTPUT_PATH, index=False)

    return f"Merged and normalized file saved at: {OUTPUT_PATH}"

# DAG Definition
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id='merge_labeled_data',
    default_args=default_args,
    description='Merge and normalize YouTube and Reddit labeled data',
    start_date=datetime(2025, 5, 15),
    schedule=None,
    catchup=False,
    tags=["merge", "nlp", "normalize"]
) as dag:

    merge_task = PythonOperator(
        task_id='merge_and_normalize_csvs',
        python_callable=merge_and_normalize
    )
