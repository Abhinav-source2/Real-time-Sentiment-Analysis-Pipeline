import os
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cleaning function inside DAG file
def clean_youtube_data():
    """
    Cleans YouTube comments CSV and saves cleaned data.
    Adjust input_path and output_path as needed.
    """
    try:
        # Download stopwords if not present
        nltk.download('stopwords', quiet=True)
        
        # Define paths (change these as per your setup)
        input_path = '/opt/airflow/data/youtube_comments_combined.csv'  # Your raw data CSV path
        output_path = '/opt/airflow/data/youtube_cleaned.csv'  # Output cleaned CSV path
        comment_col = "Comment"

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found at: {input_path}")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)

        if comment_col not in df.columns:
            available_cols = ", ".join(df.columns)
            raise ValueError(f"Column '{comment_col}' not found. Available columns: {available_cols}")

        stop_words = set(stopwords.words('english'))
        translator = str.maketrans('', '', string.punctuation)

        def clean_single_comment(comment: str) -> str:
            if pd.isna(comment):
                return ""
            text = str(comment)
            text = text.translate(translator)
            text = text.lower()
            text = ' '.join([word for word in text.split() if word not in stop_words])
            return text.strip()

        logger.info(f"Cleaning {len(df)} comments...")
        df['cleaned_comment'] = df[comment_col].apply(clean_single_comment)
        df = df[df['cleaned_comment'].str.len() > 0]

        df.to_csv(output_path, index=False)
        logger.info(f"Successfully cleaned {len(df)} comments. Output saved to {output_path}")
    except Exception as e:
        logger.error(f"Error cleaning YouTube data: {e}")
        raise

# Default args for DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}
# Define DAG
with DAG(
    'clean_youtube_data_dag',
    default_args=default_args,
    description='DAG to clean YouTube comments data',
    schedule='@daily',  # Change schedule as needed
    catchup=False
) as dag:

    clean_task = PythonOperator(
        task_id='clean_youtube_comments',
        python_callable=clean_youtube_data
    )

    clean_task
